from classes.Game import Game
from classes.Player import Player
from home.redis_buffer_singleton import redis_buffer_instance
from home.std_out_redirector import StdoutRedirector
from home.MyThread import MyThread
from threading import Event
from home.ThreadVarManagerSingleton import task_manager
import json
import sys
import queue
import time
import cProfile
import pstats

def main(data_queue_combinations = None, session_id = None, stop_event = None):
    when_game_one_pair = redis_buffer_instance.redis_1.get(f'when_one_pair_{session_id}').decode('utf-8')
    print("One Pair or not: ", when_game_one_pair)

    print(f"Thread started for session {session_id}")
    
    if when_game_one_pair == '1':
        data_queue_combinations = queue.Queue()
        
        my_thread = MyThread(target=Player(thread=False, unique_session_id=session_id, all_arrangements=False).cards_permutations, 
                             data_queue=data_queue_combinations, 
                             flag1=False, 
                             flag2=True, 
                             session_id=session_id)
        
        name = "thread_one_pair_game"
        task_manager.session_threads[session_id][name].set_thread(session_id, my_thread)
        task_manager.session_threads[session_id][name].thread[session_id].daemon = True
        task_manager.session_threads[session_id][name].thread[session_id].start()

        Game(data_queue_combinations, session_id, task_manager.stop_event_progress)
        my_thread.join()
    else:
        # sys.stdout = StdoutRedirector(redis_buffer_instance)
        Game(data_queue_combinations, session_id, task_manager.session_threads[session_id]["thread_perms_combs"].event["stop_event_progress"])


    # end_time = time.time() - start_time
    
    # with open("time.txt", "w") as file:
    #     file.write(str(end_time) + " sec\n")
    
    # print()    
    # print(end_time, " sec")
    
# if __name__ == "__main__":
#     #cProfile.run('main()', 'full_profiler.txt')
    
#     main()
    
#     #p = pstats.Stats('full_profiler.txt')
#     #p.sort_stats('cumulative').print_stats()