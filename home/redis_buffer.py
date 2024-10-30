# import redis

# class RedisBuffer:
#     def __init__(self):
#         self.redis = redis.StrictRedis(host='localhost', port=6379, db=0)

#     def write_to_buffer(self, key, data):
#         self.redis.set(key, data)
#         print("Data written to Redis:", data)  # Debugging output

#     def read_from_buffer(self, key):
#         return self.redis.get(key)

import redis
import threading 
import sys

class RedisBuffer:
    def __init__(self):
        self.redis_1 = redis.StrictRedis(host='localhost', port=6379, db=0)
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

# redis_buffer_instance = RedisBuffer()

