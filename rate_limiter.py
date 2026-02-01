import time
from collections import defaultdict, deque

class RateLimiter:
    def __init__(self, max_requests=10, window_seconds=60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.buckets = defaultdict(deque)

    def allow(self, key):
        now = time.time()
        bucket = self.buckets[key]

        while bucket and now - bucket[0] > self.window_seconds:
            bucket.popleft()

        if len(bucket) >= self.max_requests:
            retry_after = int(self.window_seconds - (now - bucket[0]))
            return False, max(retry_after, 1)

        bucket.append(now)
        return True, 0
