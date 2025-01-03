import threading

class SessionThreads:
    def __init__(self, my_thread = None):
        self.thread = {}
        self.event = {}
        self.lock = {}

    def set_thread(self, thread_name, my_thread):
        self.thread[thread_name] = my_thread
    
    def add_event(self, event_name):
        self.event[event_name] = threading.Event()

    def add_lock(self, lock_name):
        self.lock[lock_name] = threading.Lock()

class ThreadVarManagerSingleton:
    session_threads = {}

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ThreadVarManagerSingleton, cls).__new__(cls)
        return cls._instance

    def add_session(self, unique_session_id, session_name):
        if unique_session_id not in self.session_threads:
            self.session_threads[unique_session_id] = {}

        self.session_threads[unique_session_id][session_name] = SessionThreads()

# Expose an instance of TaskManagerSingleton (only one instance)
task_manager = ThreadVarManagerSingleton()