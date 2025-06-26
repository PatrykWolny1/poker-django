import threading

class SessionThreads:
    """
    A class to manage threads, events, and locks for a session.

    This class allows associating multiple threads, events, and locks within a session.
    """
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
    """
    A singleton class to manage session-based thread storage.

    This class ensures that only one instance of `ThreadVarManagerSingleton` exists
    and maintains a global storage (`session_threads`) for thread-related data.
    """
    session_threads = {}

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ThreadVarManagerSingleton, cls).__new__(cls)
        return cls._instance

    def add_session(self, unique_session_id, session_name):
        """
        Add a new session with an associated thread manager.

        :param unique_session_id: Unique identifier for the session.
        :param session_name: Name of the session.
        """
        if unique_session_id not in self.session_threads:
            self.session_threads[unique_session_id] = {}    # Initialize session dictionary
        
        # Assign a new `SessionThreads` instance for the session
        self.session_threads[unique_session_id][session_name] = SessionThreads()

# Expose a global instance of `ThreadVarManagerSingleton` (singleton instance)
task_manager = ThreadVarManagerSingleton()