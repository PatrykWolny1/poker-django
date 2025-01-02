import threading

class SessionThreads:
    def __init__(self, my_thread = None):
        self.thread = my_thread
        self.stop_event = threading.Event()
        self.stop_event_main = threading.Event()
        self.stop_event_game = threading.Event()
        self.stop_event_progress = threading.Event()
        self.stop_event_combs_perms = threading.Event()
        self.data_ready_event = threading.Event()

        self.cache_lock_progress = threading.Lock()
        self.cache_lock_event_var = threading.Lock()

    def set_thread(self, my_thread):
        self.thread = my_thread

class ThreadVarManagerSingleton:
    session_threads = {}

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ThreadVarManagerSingleton, cls).__new__(cls)
        return cls._instance

    def add_session(self, unique_session_id, name):
        if unique_session_id not in self.session_threads:
            self.session_threads[unique_session_id] = {}

        self.session_threads[unique_session_id][name] = SessionThreads()



# Expose an instance of TaskManagerSingleton (only one instance)
task_manager = ThreadVarManagerSingleton()