import threading

class ThreadVarManagerSingleton:
    stop_event = threading.Event()
    stop_event_main = threading.Event()
    stop_event_game = threading.Event()
    stop_event_progress = threading.Event()
    stop_event_combs_perms = threading.Event()
    data_ready_event = threading.Event()
    cache_lock_progress = threading.Lock()
    cache_lock_event_var = threading.Lock()
    
    session_threads = {}
    
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ThreadVarManagerSingleton, cls).__new__(cls)
        return cls._instance

# Expose an instance of TaskManagerSingleton (only one instance)
task_manager = ThreadVarManagerSingleton()