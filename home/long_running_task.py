import time
from django.core.cache import cache
import memcache
from redis import Redis
import sys
import time
from home.std_out_redirector import StdoutRedirector
from home.redis_buffer_singleton import redis_buffer_instance


def long_running_task():

    # cli = Redis('localhost')
    sys.stdout = StdoutRedirector(redis_buffer_instance)

    for i in range(101):  # Simulate some work
        print(f"Task progress: {i+1}\n")  # This goes into output_buffer
        time.sleep(0.2)
    
    sys.stdout = sys.__stdout__  # Restore original stdout
    print("Long-running task completed.\n")  # Debugging output after task completion
