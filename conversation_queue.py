"""
Conversation Queue System

Handles queuing and processing of multiple simulated conversations.
Features:
- Queue management for incoming attack simulations
- Priority-based processing
- Conversation batching
- Rate limiting
- Background processing
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Callable
from datetime import datetime, timedelta
from enum import Enum
import asyncio
import threading
from queue import Queue, PriorityQueue
import time

from core.database_module import add_message, get_conversation, save_engagement_metrics, save_attack_classification
from core.engagement_tracker import EngagementTracker
from logging_config import get_logger

logger = get_logger()


class ConversationPriority(Enum):
    """Priority levels for conversation processing"""
    LOW = 3
    NORMAL = 2
    HIGH = 1
    CRITICAL = 0


@dataclass
class ConversationTask:
    """Task in the conversation queue"""
    conversation_id: int
    attacker_id: str
    message: str
    sender_type: str  # 'attacker' or 'bait_profile'
    priority: ConversationPriority = ConversationPriority.NORMAL
    timestamp: datetime = field(default_factory=datetime.now)
    retry_count: int = 0
    max_retries: int = 3
    
    def __lt__(self, other):
        """For priority queue ordering"""
        if self.priority.value != other.priority.value:
            return self.priority.value < other.priority.value
        return self.timestamp < other.timestamp


class ConversationQueue:
    """Queue for managing conversation messages"""
    
    def __init__(self, max_queue_size: int = 1000, workers: int = 5):
        """
        Initialize conversation queue.
        
        Args:
            max_queue_size: Maximum number of tasks in queue
            workers: Number of worker threads
        """
        self.queue: PriorityQueue = PriorityQueue(maxsize=max_queue_size)
        self.workers = workers
        self.running = False
        self.worker_threads: List[threading.Thread] = []
        self.stats = {
            'processed': 0,
            'failed': 0,
            'retried': 0,
            'queue_size': 0,
            'start_time': None
        }
        self.failed_tasks: List[ConversationTask] = []
    
    def enqueue(self, task: ConversationTask) -> bool:
        """
        Add a task to the queue.
        
        Args:
            task: ConversationTask to process
            
        Returns:
            True if enqueued successfully, False if queue is full
        """
        try:
            self.queue.put_nowait((task.priority.value, task.timestamp.timestamp(), task))
            self.stats['queue_size'] = self.queue.qsize()
            logger.info(f"TASK_ENQUEUED | conv_id={task.conversation_id} priority={task.priority.name} queue_size={self.stats['queue_size']}")
            return True
        except Exception as e:
            logger.error(f"ENQUEUE_ERROR | conv_id={task.conversation_id} | {str(e)}")
            return False
    
    def dequeue(self, timeout: float = 1.0) -> Optional[ConversationTask]:
        """
        Get next task from queue.
        
        Args:
            timeout: Timeout in seconds
            
        Returns:
            ConversationTask or None if queue is empty
        """
        try:
            _, _, task = self.queue.get(timeout=timeout)
            self.stats['queue_size'] = self.queue.qsize()
            return task
        except:
            return None
    
    def start(self):
        """Start worker threads"""
        if self.running:
            logger.warning("Queue already running")
            return
        
        self.running = True
        self.stats['start_time'] = datetime.now()
        
        for i in range(self.workers):
            thread = threading.Thread(target=self._worker_loop, daemon=True, name=f"ConvWorker-{i}")
            thread.start()
            self.worker_threads.append(thread)
        
        logger.info(f"QUEUE_STARTED | workers={self.workers}")
    
    def stop(self):
        """Stop worker threads"""
        self.running = False
        
        # Wait for threads to finish
        for thread in self.worker_threads:
            thread.join(timeout=5)
        
        logger.info(f"QUEUE_STOPPED | processed={self.stats['processed']} failed={self.stats['failed']}")
    
    def _worker_loop(self):
        """Worker thread main loop"""
        while self.running:
            task = self.dequeue(timeout=1.0)
            if task:
                self._process_task(task)
    
    def _process_task(self, task: ConversationTask) -> bool:
        """
        Process a single task.
        
        Args:
            task: ConversationTask to process
            
        Returns:
            True if successful, False if failed
        """
        try:
            # Add message to conversation
            message = add_message(
                conversation_id=task.conversation_id,
                sender_type=task.sender_type,
                message_text=task.message
            )
            
            if not message:
                raise Exception("Failed to add message")
            
            # Log success
            self.stats['processed'] += 1
            logger.info(f"TASK_PROCESSED | conv_id={task.conversation_id} message_id={message.id} retry={task.retry_count}")
            
            return True
            
        except Exception as e:
            logger.error(f"TASK_FAILED | conv_id={task.conversation_id} | {str(e)}")
            
            # Retry logic
            if task.retry_count < task.max_retries:
                task.retry_count += 1
                self.stats['retried'] += 1
                # Re-enqueue with higher priority
                task.priority = ConversationPriority.HIGH
                self.enqueue(task)
                logger.info(f"TASK_RETRIED | conv_id={task.conversation_id} attempt={task.retry_count}/{task.max_retries}")
            else:
                self.stats['failed'] += 1
                self.failed_tasks.append(task)
                logger.error(f"TASK_FAILED_PERMANENTLY | conv_id={task.conversation_id} attempts={task.retry_count}")
            
            return False
    
    def get_stats(self) -> Dict:
        """Get queue statistics"""
        uptime = None
        if self.stats['start_time']:
            uptime = (datetime.now() - self.stats['start_time']).total_seconds()
        
        return {
            'running': self.running,
            'queue_size': self.queue.qsize(),
            'workers': self.workers,
            'processed': self.stats['processed'],
            'failed': self.stats['failed'],
            'retried': self.stats['retried'],
            'uptime_seconds': uptime,
            'failed_tasks': len(self.failed_tasks)
        }
    
    def get_failed_tasks(self) -> List[Dict]:
        """Get list of permanently failed tasks"""
        return [
            {
                'conversation_id': task.conversation_id,
                'attacker_id': task.attacker_id,
                'retry_count': task.retry_count,
                'timestamp': task.timestamp.isoformat()
            }
            for task in self.failed_tasks
        ]


class ConversationBatcher:
    """Batch process conversations for analytics"""
    
    def __init__(self, batch_size: int = 50, analysis_callback: Optional[Callable] = None):
        """
        Initialize conversation batcher.
        
        Args:
            batch_size: Number of conversations to batch before processing
            analysis_callback: Optional callback function to process batch
        """
        self.batch_size = batch_size
        self.current_batch: List[int] = []
        self.analysis_callback = analysis_callback
        self.processed_batches = 0
    
    def add_conversation(self, conversation_id: int) -> bool:
        """
        Add conversation to batch.
        
        Args:
            conversation_id: ID of conversation to add
            
        Returns:
            True if batch should be processed, False otherwise
        """
        self.current_batch.append(conversation_id)
        
        if len(self.current_batch) >= self.batch_size:
            self.process_batch()
            return True
        
        return False
    
    def process_batch(self):
        """Process current batch"""
        if not self.current_batch:
            return
        
        try:
            if self.analysis_callback:
                self.analysis_callback(self.current_batch)
            
            self.processed_batches += 1
            logger.info(f"BATCH_PROCESSED | size={len(self.current_batch)} batches_total={self.processed_batches}")
            
        except Exception as e:
            logger.error(f"BATCH_PROCESSING_ERROR | {str(e)}")
        
        finally:
            self.current_batch = []
    
    def flush(self):
        """Process any remaining conversations in batch"""
        self.process_batch()


class ConversationRateLimiter:
    """Rate limit conversation processing"""
    
    def __init__(self, max_messages_per_minute: int = 100, max_conversations_per_minute: int = 20):
        """
        Initialize rate limiter.
        
        Args:
            max_messages_per_minute: Max messages to process per minute
            max_conversations_per_minute: Max conversations to start per minute
        """
        self.max_messages = max_messages_per_minute
        self.max_conversations = max_conversations_per_minute
        self.message_timestamps: List[datetime] = []
        self.conversation_timestamps: List[datetime] = []
    
    def can_add_message(self) -> bool:
        """Check if we can add a message"""
        now = datetime.now()
        minute_ago = now - timedelta(minutes=1)
        
        # Remove old timestamps
        self.message_timestamps = [ts for ts in self.message_timestamps if ts > minute_ago]
        
        # Check limit
        if len(self.message_timestamps) >= self.max_messages:
            return False
        
        self.message_timestamps.append(now)
        return True
    
    def can_create_conversation(self) -> bool:
        """Check if we can create a new conversation"""
        now = datetime.now()
        minute_ago = now - timedelta(minutes=1)
        
        # Remove old timestamps
        self.conversation_timestamps = [ts for ts in self.conversation_timestamps if ts > minute_ago]
        
        # Check limit
        if len(self.conversation_timestamps) >= self.max_conversations:
            return False
        
        self.conversation_timestamps.append(now)
        return True
    
    def get_status(self) -> Dict:
        """Get current rate limit status"""
        now = datetime.now()
        minute_ago = now - timedelta(minutes=1)
        
        recent_messages = sum(1 for ts in self.message_timestamps if ts > minute_ago)
        recent_conversations = sum(1 for ts in self.conversation_timestamps if ts > minute_ago)
        
        return {
            'messages_this_minute': recent_messages,
            'max_messages_per_minute': self.max_messages,
            'conversations_this_minute': recent_conversations,
            'max_conversations_per_minute': self.max_conversations,
            'message_capacity_available': self.max_messages - recent_messages,
            'conversation_capacity_available': self.max_conversations - recent_conversations
        }


class ConversationManager:
    """High-level conversation management with queuing and analytics"""
    
    def __init__(self, queue_workers: int = 5, batch_size: int = 50):
        """
        Initialize conversation manager.
        
        Args:
            queue_workers: Number of queue workers
            batch_size: Batch size for analytics
        """
        self.queue = ConversationQueue(workers=queue_workers)
        self.batcher = ConversationBatcher(batch_size=batch_size)
        self.rate_limiter = ConversationRateLimiter()
        self.queue.start()
        logger.info("Conversation manager initialized")
    
    def add_message(self, conversation_id: int, attacker_id: str, sender_type: str, 
                   message: str, priority: ConversationPriority = ConversationPriority.NORMAL) -> bool:
        """
        Add message to conversation via queue.
        
        Args:
            conversation_id: ID of conversation
            attacker_id: ID of attacker
            sender_type: 'attacker' or 'bait_profile'
            message: Message text
            priority: Processing priority
            
        Returns:
            True if queued successfully
        """
        # Check rate limit
        if not self.rate_limiter.can_add_message():
            logger.warning(f"RATE_LIMITED | conv_id={conversation_id}")
            return False
        
        # Create and enqueue task
        task = ConversationTask(
            conversation_id=conversation_id,
            attacker_id=attacker_id,
            message=message,
            sender_type=sender_type,
            priority=priority
        )
        
        return self.queue.enqueue(task)
    
    def get_status(self) -> Dict:
        """Get manager status"""
        return {
            'queue': self.queue.get_stats(),
            'rate_limiter': self.rate_limiter.get_status(),
            'batcher': {
                'batch_size': self.batcher.batch_size,
                'current_batch_size': len(self.batcher.current_batch),
                'processed_batches': self.batcher.processed_batches
            }
        }
    
    def shutdown(self):
        """Shutdown manager"""
        self.queue.stop()
        self.batcher.flush()
        logger.info("Conversation manager shutdown")


# Global instance
_manager: Optional[ConversationManager] = None


def get_conversation_manager() -> ConversationManager:
    """Get or create global conversation manager"""
    global _manager
    if _manager is None:
        _manager = ConversationManager(queue_workers=5, batch_size=50)
    return _manager
