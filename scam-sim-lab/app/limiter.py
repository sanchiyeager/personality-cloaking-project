import time

last_request_time = 0
MIN_INTERVAL = 5  # seconds between requests

def allow_request():
    global last_request_time
    current = time.time()
    if current - last_request_time < MIN_INTERVAL:
        return False
    last_request_time = current
    return True
