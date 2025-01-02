import threading

class SessionThreads:
    def __init__(self, my_thread = None):
        self.thread = my_thread
        self.event = {}

    def set_thread(self, my_thread):
        self.thread = my_thread
    
    def add_event(self, event_name):
        self.event[event_name] = threading.Event()

class ThreadVarManagerSingleton:
    session_threads = {}

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ThreadVarManagerSingleton, cls).__new__(cls)
        return cls._instance

    def add_session(self, unique_session_id, thread_name):
        if unique_session_id not in self.session_threads:
            self.session_threads[unique_session_id] = {}

        self.session_threads[unique_session_id][thread_name] = SessionThreads()

# Expose an instance of TaskManagerSingleton (only one instance)
task_manager = ThreadVarManagerSingleton()