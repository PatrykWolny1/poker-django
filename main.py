from classes.Game import Game
import time
import cProfile
import pstats
from classes.Player import Player

def main():
    # start_time = time.time()
    # cards_1, rand_int_1, all_comb_perm = Player().cards_permutations(combs_gen=True)
    print("HELLO")
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