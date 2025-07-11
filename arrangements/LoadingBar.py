from django.core.cache import cache
from numpy import floor
from home.redis_buffer_singleton import redis_buffer_instance, redis_buffer_instance_stop, redis_buffer_instance_one_pair_game
from home.ThreadVarManagerSingleton import task_manager
import time
import shutil

class LoadingBar:
    def __init__(self, name, total_steps, display_interval, complete_interval, helper_arr):
        self.name = name
        self.total_steps = total_steps                          # Total number of steps in the progress
        self.display_interval = display_interval                # Interval for displaying progress
        self.complete_interval = complete_interval              # Interval to mark progress as completed
        self.current_progress = 0                               # Current progress count
        self.progress_bar = ["#"] * (total_steps // display_interval)
        self.helper_arr = helper_arr                            # Helper array with file paths and other helper info
        self.stop_requested = False                             # Track if stop is requested
        self.begin = True                                       # Flag for initial setup
        self.ret_lb = True

    def update_progress(self, step_count):
        """Updates the internal progress bar based on step count."""

        is_accepted = redis_buffer_instance_one_pair_game.redis_1.get('connection_accepted').decode('utf-8')
        while is_accepted != 'yes':
            is_accepted = redis_buffer_instance_one_pair_game.redis_1.get('connection_accepted').decode('utf-8')

        self.current_progress = step_count
        
        # Update the bar display every `complete_interval` steps
        if step_count % self.complete_interval == 0:
            next_dot_index = self.progress_bar.index("#") if "#" in self.progress_bar else None
            if next_dot_index is not None:
                self.progress_bar[next_dot_index] = "."
                self._update_cache_with_progress()
            # Complete the progress if at the final step

        if step_count == self.total_steps:       
            return False 
        return True # Delete with _finish_progress()
    
    def _update_cache_with_progress(self):
        """Helper to update cache with current progress status and trigger event."""
        with task_manager.cache_lock_progress:
            redis_buffer_instance.redis_1.set('shared_progress', str(self.progress_bar.count('.')))
        task_manager.data_ready_event.set()
        task_manager.data_ready_event.clear()

    def _finish_progress(self):
        """Marks the progress as complete and updates the cache."""
        with task_manager.cache_lock_progress:
            self.progress_bar = ["."] * len(self.progress_bar)
            self._update_cache_with_progress()
        
    def check_stop_event(self):
        """Checks for stop event and finalizes if set."""
        if task_manager.stop_event.is_set():
            self.ret_lb = False
            with task_manager.cache_lock_event_var:
                # Copy the helper file and clear helper arrays
                shutil.copyfile(self.helper_arr.helper_file_class.file_path.resolve(), 
                                self.helper_arr.helper_file_class.file_path_dst.resolve())
                self._log_saved_permutations()
                time.sleep(1)
                
                
                # Clear data structures in helper_arr
                self.helper_arr.weight_gen.clear()
                self.helper_arr.cards_all_permutations.clear()
                
                redis_buffer_instance.redis_1.set('prog_when_fast', '100')
                # Signal stop event to Redis buffer
                redis_buffer_instance_stop.redis_1.set('stop_event_var', '1')
            return False  # Stop the loading bar

        # Initialize helper file on the first run
        if self.begin:
            self.helper_arr.helper_file_class.file_path_dst.write_text('')
            self.begin = False
        return True  # Continue the loading bar

    def _log_saved_permutations(self):
        """Logs the count of saved permutations based on helper file content."""
        with open(self.helper_arr.helper_file_class.file_path_dst.resolve(), 'r') as file:
            lines = file.readlines()
            line_count = len(lines)
        redis_buffer_instance_stop.redis_1.set('count_arrangements_stop', "Ilosc zapisanych ukladow: " + str(int(floor(line_count / 2))))
