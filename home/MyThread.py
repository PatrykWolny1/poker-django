import threading
import queue
from home.redis_buffer_singleton import redis_buffer_instance

import ctypes

class MyThread(threading.Thread):
    def __init__(self, target, data_queue=None, thread_id=None):
        super().__init__(target=target, args=(data_queue, ))
        self.thread_id = thread_id  # Use this ID to separate data
        self.data_queue = data_queue if data_queue is not None else queue.Queue()

    def run(self):
        redis_buffer_instance.redis_1.set(f'thread_data_{self.thread_id}', 'running')
        self._target(self.data_queue)
    
    def get_id(self):

        # returns id of the respective thread
        if hasattr(self, '_thread_id'):
            return self._thread_id
        for id, thread in threading._active.items():
            if thread is self:
                return id
            
    def raise_exception(self):
        thread_id = self.get_id()
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id,
              ctypes.py_object(SystemExit))
        if res > 1:
            ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, 0)
            print('Exception raise failure')
        print("EXCEPTION")