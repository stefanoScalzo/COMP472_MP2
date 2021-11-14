#!/usr/bin/env python
# coding: utf-8

from LineEmUp import LineEmUp
import random


class ScoreBoard:
    """
    Simulates 2*r LineEmUp games and writes relevant statistics to a file

    Attributes:
        num_of_games_per_symbol - number of games to be simulated per color (i.e. total games = 2*r)
        destination - filepath to be written to
        average_heuristic_times
        average_state_counts
        average_depth_averages
        average_total_state_counts_p_depth
        average_ard_averages
        average_move_counter

    * Note that almost all attributes are simply averages of the averages calculated at the end of each game
    """

    def __init__(self, r=10):
        self.num_of_games_per_symbol = r
        self.average_heuristic_times = 0
        self.average_state_counts = 0
        self.average_depth_averages = 0
        self.average_total_state_counts_p_depth = {}
        self.average_ard_averages = 0
        self.average_move_counter = 0
        self.winning_e1 = 0
        self.winning_e2 = 0
        self.destination = 'scoreboard.txt'

    def calculateScore(self, config):
        """
        Runs 2*r simulations of LineEmUp and calculates all all relevant statistics.
        :return:
        """
        n = int(config["conf"][0])
        b = int(config["conf"][1])
        s = int(config["conf"][2])
        t = int(config["conf"][3])
        d1 = int(config["conf"][4])
        d2 = int(config["conf"][5])
        if config["a1"]:
            a1 = LineEmUp.ALPHABETA
        else:
            a1 = LineEmUp.MINIMAX
        if config["a2"]:
            a2 = LineEmUp.ALPHABETA
        else:
            a2 = LineEmUp.MINIMAX

        if "blocks" in config:
            blocks = config["blocks"]
        else:
            blocks = [(random.randrange(0, n), random.randrange(0, n)) for i in range(b)]

        self.g = LineEmUp(board_size=n, blocks=b, blocks_coord=blocks, winning_size=s, max_move_time=t, recommend=True,
                          player_w=LineEmUp.AI, player_b=LineEmUp.AI, heuristic_w=LineEmUp.E1,
                          heuristic_b=LineEmUp.E2, a1=a1, a2=a2, d1=d1, d2=d2)
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

        self.g = LineEmUp(board_size=n, blocks=b, blocks_coord=blocks, winning_size=s, max_move_time=t, recommend=True,
                          player_w=LineEmUp.AI, player_b=LineEmUp.AI, heuristic_w=LineEmUp.E1,
                          heuristic_b=LineEmUp.E2, a1=a1, a2=a2, d1=d1, d2=d2)
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
            if stats[6] == 'W':
                self.winning_e1 += 1
            elif stats[6] == 'B':
                self.winning_e2 += 1

        self.average_heuristic_times = self.average_heuristic_times / (self.num_of_games_per_symbol * 2)
        self.average_state_counts = self.average_state_counts / (self.num_of_games_per_symbol * 2)
        self.average_depth_averages += self.average_depth_averages / (self.num_of_games_per_symbol * 2)
        for depth in stats[3]:
            self.average_total_state_counts_p_depth[depth] = self.average_total_state_counts_p_depth[depth] / (
                    self.num_of_games_per_symbol * 2)
        self.average_ard_averages = self.average_ard_averages / (self.num_of_games_per_symbol * 2)
        self.average_move_counter += self.average_move_counter / (self.num_of_games_per_symbol * 2)

    def printAverageEndOfAllGames(self, id):
        """
        Prints the results to a file. calculateScore() must first be called.

        :return:
        """
        if self.g is None:
            raise ValueError("Game(s) have not been instantiated. calculateScore() must first be called. ")

        file = open('scoreboard' + str(id) + '.txt', 'w+')
        self.g.printIntialGameToFile(file)
        file.write("")
        file.write("Heuristic 1 winning %: " + str(round(self.winning_e1 / 2.0 * self.num_of_games_per_symbol, 2)) + '\n')
        file.write("Heuristic 2 winning %: " + str(round(self.winning_e2 / 2.0 * self.num_of_games_per_symbol, 2)) + '\n')
        file.write('i. Average of Average evaluation time of heuristic: ' + str(self.average_heuristic_times) + '\n')
        file.write('ii. Average of Total states evaluated: ' + str(self.average_state_counts) + '\n')
        file.write('iii. Average of Average of average depths: ' + str(self.average_depth_averages) + '\n')
        file.write('iv. Average Total number of states evaluated at each depth: ' + '\n')
        for depth in sorted(self.average_total_state_counts_p_depth.keys(), reverse=True):
            file.write("\t" + str(depth) + ": " + str(self.average_total_state_counts_p_depth[depth]) + '\n')
        file.write('v. Average of Average ARD: ' + str(self.average_ard_averages) + '\n')
        file.write('vi. Average Total Move Count: ' + str(self.average_move_counter) + '\n')
        file.close()
