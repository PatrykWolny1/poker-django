import redis
import threading 
import sys
from urllib.parse import urlparse
import os

redis_url = os.getenv('REDIS_URL', 'redis://redis:6379/1')

class RedisBuffer:
    def __init__(self):
        print(redis_url)
        self.redis_1 = redis.Redis.from_url(redis_url)
        
        #self.redis_1 = redis.Redis.from_url()
        self.lock = threading.Lock() # Initialize a lock
    
    def write_to_buffer(self, key, data):
        with self.lock:
            self.redis_1.append(key, data)
            # sys.__stdout__.write(f"Data written to Redis: {data}\n") # Directly write to system stdout for debugging
    
    def read_from_buffer(self, key):
        with self.lock:
            data = self.redis_1.get(key)      
            if data:
                self.redis_1.delete(key) # Clear the buffer after reading
                # sys.__stdout__.write(f"Data read from Redis: {data}\n") # Directly write to system stdout for debugging
        return data
