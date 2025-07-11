import threading
import queue
from home.redis_buffer_singleton import redis_buffer_instance

import ctypes

class MyThread(threading.Thread):
    def __init__(self, target, data_queue=None, flag1=None, flag2=None):
        super().__init__(target=target, args=(data_queue))
        self.data_queue = data_queue if isinstance(data_queue, queue.Queue) else queue.Queue()
        self.flag1 = flag1
        self.flag2 = flag2
        self.daemon = True

    def run(self):
        thread_id = threading.get_ident()  # Get unique thread identifier
        print(f"Thread {thread_id} is starting with flags: {self.flag1}, {self.flag2}")

        if self._target:
            if self.flag1 is not None and self.flag2 is not None:
                self._target(self.flag1, self.flag2, self.data_queue)
            else:
                
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
