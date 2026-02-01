import sqlite3
import json
from datetime import datetime
from typing import List, Optional
from models import ChatMessage, Conversation, EngagementMetric, AttackClassification

DB_NAME = "database.db"

def init_db():
    """Initialize database with all required tables"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Read and execute schema
    try:
        with open('schema.sql', 'r') as schema_file:
            schema = schema_file.read()
            cursor.executescript(schema)
    except FileNotFoundError:
        # Fallback: create tables directly
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS profiles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                bio TEXT NOT NULL,
                openness REAL,
                conscientiousness REAL,
                extraversion REAL,
                agreeableness REAL,
                neuroticism REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                profile_id INTEGER NOT NULL,
                attacker_id TEXT NOT NULL,
                scam_type TEXT,
                started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ended_at TIMESTAMP,
                status TEXT DEFAULT 'active',
                FOREIGN KEY (profile_id) REFERENCES profiles(id)
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chat_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id INTEGER NOT NULL,
                sender_type TEXT NOT NULL,
                message_text TEXT NOT NULL,
                sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS engagement_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id INTEGER NOT NULL,
                response_time_avg REAL,
                response_time_min REAL,
                response_time_max REAL,
                message_length_avg REAL,
                message_length_total INTEGER,
                message_count INTEGER,
                sentiment_avg REAL,
                sentiment_compound REAL,
                calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS attack_classifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id INTEGER NOT NULL,
                attack_type TEXT NOT NULL,
                confidence REAL,
                techniques_detected TEXT,
                severity_level TEXT,
                classified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
            )
        ''')
    
    conn.commit()
    conn.close()

init_db()

# ==================== PROFILE OPERATIONS ====================

def save_profile(profile_data):
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO profiles (
                bio,
                openness,
                conscientiousness,
                extraversion,
                agreeableness,
                neuroticism
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                profile_data["bio"],
                profile_data["personality"]["openness"],
                profile_data["personality"]["conscientiousness"],
                profile_data["personality"]["extraversion"],
                profile_data["personality"]["agreeableness"],
                profile_data["personality"]["neuroticism"],
            )
        )
        
        conn.commit()
        profile_id = cursor.lastrowid
        conn.close()
        return profile_id
    except Exception as e:
        print(f"Database error: {e}")
        return False


# ==================== CONVERSATION OPERATIONS ====================

def create_conversation(profile_id: int, attacker_id: str, scam_type: str = None) -> int:
    """Create a new conversation between a profile and an attacker"""
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        
        cursor.execute(
            """
            INSERT INTO conversations (profile_id, attacker_id, scam_type, status)
            VALUES (?, ?, ?, 'active')
            """,
            (profile_id, attacker_id, scam_type)
        )
        
        conn.commit()
        conversation_id = cursor.lastrowid
        conn.close()
        return conversation_id
    except Exception as e:
        print(f"Error creating conversation: {e}")
        return None


def end_conversation(conversation_id: int) -> bool:
    """Mark a conversation as ended"""
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        
        cursor.execute(
            """
            UPDATE conversations 
            SET status = 'ended', ended_at = CURRENT_TIMESTAMP 
            WHERE id = ?
            """,
            (conversation_id,)
        )
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error ending conversation: {e}")
        return False


def get_conversation(conversation_id: int) -> Optional[Conversation]:
    """Retrieve a conversation with all its messages"""
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        
        # Get conversation
        cursor.execute(
            """
            SELECT id, profile_id, attacker_id, scam_type, started_at, ended_at, status
            FROM conversations
            WHERE id = ?
            """,
            (conversation_id,)
        )
        
        row = cursor.fetchone()
        if not row:
            return None
        
        conv = Conversation(
            id=row[0],
            profile_id=row[1],
            attacker_id=row[2],
            scam_type=row[3],
            started_at=datetime.fromisoformat(row[4]) if row[4] else None,
            ended_at=datetime.fromisoformat(row[5]) if row[5] else None,
            status=row[6]
        )
        
        # Get messages
        cursor.execute(
            """
            SELECT id, conversation_id, sender_type, message_text, sent_at
            FROM chat_messages
            WHERE conversation_id = ?
            ORDER BY sent_at ASC
            """,
            (conversation_id,)
        )
        
        messages = []
        for msg_row in cursor.fetchall():
            msg = ChatMessage(
                id=msg_row[0],
                conversation_id=msg_row[1],
                sender_type=msg_row[2],
                message_text=msg_row[3],
                sent_at=datetime.fromisoformat(msg_row[4]) if msg_row[4] else None
            )
            messages.append(msg)
        
        conv.messages = messages
        conn.close()
        return conv
    except Exception as e:
        print(f"Error retrieving conversation: {e}")
        return None


def get_profile_conversations(profile_id: int) -> List[Conversation]:
    """Get all conversations for a profile"""
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        
        cursor.execute(
            """
            SELECT id, profile_id, attacker_id, scam_type, started_at, ended_at, status
            FROM conversations
            WHERE profile_id = ?
            ORDER BY started_at DESC
            """,
            (profile_id,)
        )
        
        conversations = []
        for row in cursor.fetchall():
            conv = Conversation(
                id=row[0],
                profile_id=row[1],
                attacker_id=row[2],
                scam_type=row[3],
                started_at=datetime.fromisoformat(row[4]) if row[4] else None,
                ended_at=datetime.fromisoformat(row[5]) if row[5] else None,
                status=row[6]
            )
            conversations.append(conv)
        
        conn.close()
        return conversations
    except Exception as e:
        print(f"Error retrieving conversations: {e}")
        return []


# ==================== MESSAGE OPERATIONS ====================

def add_message(conversation_id: int, sender_type: str, message_text: str) -> Optional[ChatMessage]:
    """Add a message to a conversation"""
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        
        cursor.execute(
            """
            INSERT INTO chat_messages (conversation_id, sender_type, message_text)
            VALUES (?, ?, ?)
            """,
            (conversation_id, sender_type, message_text)
        )
        
        conn.commit()
        message_id = cursor.lastrowid
        conn.close()
        
        return ChatMessage(
            id=message_id,
            conversation_id=conversation_id,
            sender_type=sender_type,
            message_text=message_text,
            sent_at=datetime.now()
        )
    except Exception as e:
        print(f"Error adding message: {e}")
        return None


def get_conversation_messages(conversation_id: int) -> List[ChatMessage]:
    """Get all messages in a conversation"""
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        
        cursor.execute(
            """
            SELECT id, conversation_id, sender_type, message_text, sent_at
            FROM chat_messages
            WHERE conversation_id = ?
            ORDER BY sent_at ASC
            """,
            (conversation_id,)
        )
        
        messages = []
        for row in cursor.fetchall():
            msg = ChatMessage(
                id=row[0],
                conversation_id=row[1],
                sender_type=row[2],
                message_text=row[3],
                sent_at=datetime.fromisoformat(row[4]) if row[4] else None
            )
            messages.append(msg)
        
        conn.close()
        return messages
    except Exception as e:
        print(f"Error retrieving messages: {e}")
        return []


# ==================== ENGAGEMENT METRICS OPERATIONS ====================

def save_engagement_metrics(metrics: EngagementMetric) -> bool:
    """Save or update engagement metrics for a conversation"""
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        
        # Check if metrics exist for this conversation
        cursor.execute(
            "SELECT id FROM engagement_metrics WHERE conversation_id = ?",
            (metrics.conversation_id,)
        )
        
        existing = cursor.fetchone()
        
        if existing:
            # Update existing metrics
            cursor.execute(
                """
                UPDATE engagement_metrics 
                SET response_time_avg = ?, response_time_min = ?, response_time_max = ?,
                    message_length_avg = ?, message_length_total = ?, message_count = ?,
                    sentiment_avg = ?, sentiment_compound = ?, calculated_at = CURRENT_TIMESTAMP
                WHERE conversation_id = ?
                """,
                (
                    metrics.response_time_avg,
                    metrics.response_time_min,
                    metrics.response_time_max,
                    metrics.message_length_avg,
                    metrics.message_length_total,
                    metrics.message_count,
                    metrics.sentiment_avg,
                    metrics.sentiment_compound,
                    metrics.conversation_id
                )
            )
        else:
            # Insert new metrics
            cursor.execute(
                """
                INSERT INTO engagement_metrics 
                (conversation_id, response_time_avg, response_time_min, response_time_max,
                 message_length_avg, message_length_total, message_count, sentiment_avg, sentiment_compound)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    metrics.conversation_id,
                    metrics.response_time_avg,
                    metrics.response_time_min,
                    metrics.response_time_max,
                    metrics.message_length_avg,
                    metrics.message_length_total,
                    metrics.message_count,
                    metrics.sentiment_avg,
                    metrics.sentiment_compound
                )
            )
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error saving engagement metrics: {e}")
        return False


def get_engagement_metrics(conversation_id: int) -> Optional[EngagementMetric]:
    """Retrieve engagement metrics for a conversation"""
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        
        cursor.execute(
            """
            SELECT id, conversation_id, response_time_avg, response_time_min, response_time_max,
                   message_length_avg, message_length_total, message_count, sentiment_avg, 
                   sentiment_compound, calculated_at
            FROM engagement_metrics
            WHERE conversation_id = ?
            """,
            (conversation_id,)
        )
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
        
        return EngagementMetric(
            id=row[0],
            conversation_id=row[1],
            response_time_avg=row[2],
            response_time_min=row[3],
            response_time_max=row[4],
            message_length_avg=row[5],
            message_length_total=row[6],
            message_count=row[7],
            sentiment_avg=row[8],
            sentiment_compound=row[9],
            calculated_at=datetime.fromisoformat(row[10]) if row[10] else None
        )
    except Exception as e:
        print(f"Error retrieving engagement metrics: {e}")
        return None


# ==================== ATTACK CLASSIFICATION OPERATIONS ====================

def save_attack_classification(classification: AttackClassification) -> bool:
    """Save attack classification for a conversation"""
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        
        techniques_json = json.dumps(classification.techniques_detected) if classification.techniques_detected else "[]"
        
        cursor.execute(
            """
            INSERT INTO attack_classifications
            (conversation_id, attack_type, confidence, techniques_detected, severity_level)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                classification.conversation_id,
                classification.attack_type,
                classification.confidence,
                techniques_json,
                classification.severity_level
            )
        )
        
        conn.commit()
        classification.id = cursor.lastrowid
        conn.close()
        return True
    except Exception as e:
        print(f"Error saving attack classification: {e}")
        return False


def get_attack_classifications(conversation_id: int) -> List[AttackClassification]:
    """Get all attack classifications for a conversation"""
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        
        cursor.execute(
            """
            SELECT id, conversation_id, attack_type, confidence, techniques_detected, 
                   severity_level, classified_at
            FROM attack_classifications
            WHERE conversation_id = ?
            ORDER BY classified_at DESC
            """,
            (conversation_id,)
        )
        
        classifications = []
        for row in cursor.fetchall():
            techniques = json.loads(row[4]) if row[4] else []
            
            classification = AttackClassification(
                id=row[0],
                conversation_id=row[1],
                attack_type=row[2],
                confidence=row[3],
                techniques_detected=techniques,
                severity_level=row[5],
                classified_at=datetime.fromisoformat(row[6]) if row[6] else None
            )
            classifications.append(classification)
        
        conn.close()
        return classifications
    except Exception as e:
        print(f"Error retrieving attack classifications: {e}")
        return []


def get_latest_attack_classification(conversation_id: int) -> Optional[AttackClassification]:
    """Get the most recent attack classification for a conversation"""
    classifications = get_attack_classifications(conversation_id)
    return classifications[0] if classifications else None
