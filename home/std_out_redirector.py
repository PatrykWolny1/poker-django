class StdoutRedirector:
    def __init__(self, redis_instance):
        self.redis_instance = redis_instance
    def write(self, data):
        self.redis_instance.write_to_buffer('prog', data)
    def flush(self):
        pass