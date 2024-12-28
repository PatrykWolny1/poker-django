from classes.Game import Game
from classes.Player import Player
from home.redis_buffer_singleton import redis_buffer_instance, redis_buffer_instance_one_pair_game
from home.std_out_redirector import StdoutRedirector
from home.MyThread import MyThread
import json
import sys
import threading
import queue
import time
import cProfile
import pstats

def main(data_queue_combinations = None):
    when_game_one_pair = redis_buffer_instance.redis_1.get('when_one_pair').decode('utf-8')
    print("One Pair or not: ", when_game_one_pair)

    
    
    if when_game_one_pair == '1':
        # thread_cards_permutations = threading.Thread(target=Player().cards_permutations, args=(False, True, data_queue_combinations,))
        # thread_cards_permutations.start()
        data_queue_combinations = queue.Queue()
        my_thread = MyThread(target=Player().cards_permutations, data_queue=data_queue_combinations, flag1=False, flag2=True)
        my_thread.start()
        # my_thread.join()
        Game(data_queue_combinations)
    else:
        # sys.stdout = StdoutRedirector(redis_buffer_instance)
        Game()


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