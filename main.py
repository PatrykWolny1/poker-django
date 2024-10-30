from classes.Game import Game
import time
import cProfile
import pstats
from classes.Player import Player
import sys
import time
from home.redis_buffer_singleton import redis_buffer_instance
from home.std_out_redirector import StdoutRedirector

def main():
    sys.stdout = StdoutRedirector(redis_buffer_instance)
    
    Game()


    # end_time = time.time() - start_time
    
    # with open("time.txt", "w") as file:
    #     file.write(str(end_time) + " sec\n")
    
    # print()    
    # print(end_time, " sec")
    
if __name__ == "__main__":
    #cProfile.run('main()', 'full_profiler.txt')
    
    main()
    
    #p = pstats.Stats('full_profiler.txt')
    #p.sort_stats('cumulative').print_stats()