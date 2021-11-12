#!/usr/bin/env python
# coding: utf-8

from LineEmUp import LineEmUp
from PrintManager import PrintManager
import sys

class ScoreBoard:
    num_of_games_per_symbol = 10
    average_heuristic_times = 0
    average_state_counts = 0
    average_depth_averages = 0
    average_total_state_counts_p_depth = {}
    average_ard_averages = 0
    average_move_counter = 0
    destination =  './scoreboard.txt'

    def __init__(self, r=10):
        self.num_of_games_per_symbol = r

    def calculateScore(self):
        
        
        self.g = LineEmUp(board_size=4, blocks=0, blocks_coord=[], winning_size=4, max_move_time=5, recommend=True, 
                    player_x=LineEmUp.AI, player_o=LineEmUp.AI, heuristic_x=LineEmUp.E1, 
                    heuristic_o=LineEmUp.E2, algo1=LineEmUp.ALPHABETA, algo2=LineEmUp.ALPHABETA, d1=7, d2=8)
        for play in range(0, self.num_of_games_per_symbol):
            self.g.play()
            stats = self.g.getStats()
            self.average_heuristic_times += stats[0]
            self.average_state_counts += stats[1]
            self.average_depth_averages += stats[2]
            for depth in stats[3]:
                if depth in self.average_total_state_counts_p_depth:
                    self.average_total_state_counts_p_depth[depth] += stats[3][depth]
                else:
                    self.average_total_state_counts_p_depth[depth] = stats[3][depth]

            self.average_ard_averages += stats[4]
            self.average_move_counter += stats[5]
            

        self.g = LineEmUp(board_size=4, blocks=0, blocks_coord=[], winning_size=4, max_move_time=5, recommend=True, 
                    player_x=LineEmUp.AI, player_o=LineEmUp.AI, heuristic_x=LineEmUp.E2, 
                    heuristic_o=LineEmUp.E1, algo1=LineEmUp.ALPHABETA, algo2=LineEmUp.ALPHABETA, d1=7, d2=8)
        for play in range(0, self.num_of_games_per_symbol):
            self.g.play()
            stats = self.g.getStats()
            self.average_heuristic_times += stats[0]
            self.average_state_counts += stats[1]
            self.average_depth_averages += stats[2]
            for depth in stats[3]:
                if depth in self.average_total_state_counts_p_depth:
                    self.average_total_state_counts_p_depth[depth] += stats[3][depth]
                else:
                    self.average_total_state_counts_p_depth[depth] = stats[3][depth]

            self.average_ard_averages += stats[4]
            self.average_move_counter += stats[5]

        self.average_heuristic_times = self.average_heuristic_times/(self.num_of_games_per_symbol*2)
        self.average_state_counts = self.average_state_counts/(self.num_of_games_per_symbol*2)
        self.average_depth_averages += self.average_depth_averages/(self.num_of_games_per_symbol*2)
        for depth in stats[3]:
            self.average_total_state_counts_p_depth[depth] = self.average_total_state_counts_p_depth[depth]/(self.num_of_games_per_symbol*2)
        self.average_ard_averages = self.average_ard_averages/(self.num_of_games_per_symbol*2)
        self.average_move_counter += self.average_move_counter/(self.num_of_games_per_symbol*2)

    def printAverageEndOfAllGames(self):
        sys.stdout = PrintManager()
        sys.stdout.setPath('scoreboard.txt')

        self.g.printInitialGame()
        print("")
        print('i. Average of Average evaluation time of heuristic: ' + str(self.average_heuristic_times))
        print('ii. Average of Total states evaluated: ' + str(self.average_state_counts))  
        print('iii. Average of Average of average depths: '+ str(self.average_depth_averages))
        print('iv. Average Total number of states evaluated at each depth: ') 
        for depth in sorted(self.average_total_state_counts_p_depth.keys(), reverse=True):
            print("\t" + str(depth) + ": " + str(self.average_total_state_counts_p_depth[depth]))
        print('v. Average of Average ARD: ' + str(self.average_ard_averages))
        print('vi. Average Total Move Count: ' + str(self.average_move_counter))

