import threading
import queue
from home.redis_buffer_singleton import redis_buffer_instance

class MyThread(threading.Thread):
    def __init__(self, target, data_queue=None, thread_id=None):
        super().__init__(target=target, args=(data_queue, ))
        self.thread_id = thread_id  # Use this ID to separate data
        self.data_queue = data_queue if data_queue is not None else queue.Queue()

    def run(self):
        redis_buffer_instance.redis_1.set(f'thread_data_{self.thread_id}', 'running')
        self._target(self.data_queue)
        