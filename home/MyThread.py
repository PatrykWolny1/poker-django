import threading
import queue
from home.redis_buffer_singleton import redis_buffer_instance
import ctypes

class MyThread(threading.Thread):
    """
    Custom threading class for handling tasks with flags and session tracking.
    Inherits from threading.Thread.
    """
    
    def __init__(self, target, data_queue=None, flag1=None, flag2=None, session_id=None, name=None):
        """
        Initialize the custom thread with optional queue, flags, session ID, and name.

        :param target: Function that the thread will execute.
        :param data_queue: Queue for data sharing between threads.
        :param flag1: Optional flag for additional control.
        :param flag2: Optional flag for additional control.
        :param session_id: Unique identifier for the session.
        :param name: Name of the thread.
        """
        super().__init__(target=target, args=(data_queue,))  # Pass the queue as an argument to target function
        self.data_queue = data_queue if isinstance(data_queue, queue.Queue) else queue.Queue()  # Initialize queue if not provided
        self.flag1 = flag1  # First optional flag rand_arr in Player.cards_permutations
        self.flag2 = flag2  # Second optional flag combs_gen in Player.cards_permutations
        self.session_id = session_id  # Session identifier
        self.name = name  # Thread name

    def run(self):
        """
        Executes the target function with appropriate arguments.
        """
        thread_id = threading.get_ident()  # Get unique thread identifier
        print(f"Thread {self.name} is starting with flags: {self.flag1}, {self.flag2}, ID: {thread_id}")

        # Check if a valid target function is provided
        if self._target:
            # If both flags are provided, call the target function with flags, session ID, and queue
            if self.flag1 is not None and self.flag2 is not None:
                self._target(self.flag1, self.flag2, self.session_id, self.data_queue)
            else:
                # Otherwise, call the target function with queue, session ID, and thread name
                self._target(self.data_queue, self.session_id, self.name)
