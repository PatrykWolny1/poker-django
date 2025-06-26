import redis
import threading 
import sys
from urllib.parse import urlparse
import os

redis_url = os.getenv('REDIS_URL', 'redis://redis:6379/1')

class RedisBuffer:
    def __init__(self):
        print(redis_url) # Debugging: Print the Redis connection URL
        self.redis_1 = redis.Redis.from_url(redis_url) # Create a Redis connection instance
