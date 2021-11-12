#!/usr/bin/env python
# coding: utf-8

# based on code from https://stackabuse.com/minimax-and-alpha-beta-pruning-in-python

import time
import random
import sys
from PrintManager import PrintManager

class LineEmUp:
    MINIMAX = 0
    ALPHABETA = 1
    HUMAN = 0
    AI = 1
    E1 = 0
    E2 = 1

    def __init__(self, board_size=3, blocks=0, blocks_coord=[], winning_size=3, d1=7, d2=7, 
                    max_move_time=5, player_x = AI, player_o = AI, recommend=True, heuristic_x=E2, heuristic_o=E2, algo1=ALPHABETA, algo2=ALPHABETA):
        """
        Constructor for the game.
            TODO
        """
        self.board_size = board_size
        self.blocks = blocks
        self.blocks_coord = blocks_coord
        self.winning_size = winning_size
        self.max_move_time = max_move_time
        self.recommend = recommend
        self.result = None
        self.timer_is_up = False
        self.d1 = d1
        self.d2 = d2
        self.algo1 = algo1
        self.algo2 = algo2 
        self.player_x = player_x
        self.player_o = player_o
        self.heuristic_x = heuristic_x
        self.heuristic_o = heuristic_o

        self.initialize_game()

    def initialize_game(self):
        # variables required for stats
        self.heuristic_times = []
        self.total_heuristic_times = []
        self.state_count = 0
        self.total_state_counts = 0
        self.state_count_p_depth = {}
        self.total_state_counts_p_depth = {}
        self.depths = []
        self.depth_averages = []
        self.ard_per_move = []
        self.ard_averages = []

        self.initialize_board()
        
    def initialize_board(self):
        """
        Creates the board: initializes all empty tokens, the block tokens, and sets turn player.

        :return:
        """
        self.current_state = []
        for r in range(0, self.board_size):
            self.current_state.append([0 for c in range(0, self.board_size)])

        # set empty tokens
        for x in range(0, self.board_size):
            for y in range(0, self.board_size):
                    self.current_state[x][y] = '.'

        # set Block nodes
        self.initialize_blocks(self.blocks, self.blocks_coord)

        # Player X always plays first
        self.player_turn = 'X'
        self.heuristic = self.heuristic_x
        self.max_depth = self.d1
        self.algo = self.algo1

    def initialize_blocks(self, blocks, blocks_coord):
        """
        Initializes blocks on the board.

        :param blocks: number of blocks that should be on board
        :param blocks_coord: coordinates for the blocks
        :return:
        """
        if blocks != len(blocks_coord):
            raise ValueError("Number of blocks does not correspond to list of block coordinates.")

        for coord in blocks_coord:
            self.current_state[coord['x']][coord['y']] = 'B'

    def draw_board(self):
        """
        Prints the board to the console

        :return:
        """
        print()
        for x in range(0, self.board_size):
            for y in range(0, self.board_size):
                print(F'{self.current_state[x][y]}', end="  ")
            print()
        print()
        
    def is_valid_play(self, x, y):
        """
        Checks that the provided coordinates x, y would be a valid move for a player to make

        :param x:
        :param y:
        :return: true or false
        """
        if not self.valid_coord(x, y) :
            return False
        elif self.current_state[x][y] != '.':
            return False
        else:
            return True

    def valid_coord(self, x, y):
        """
        Validates that the provided coordinates are within the legal bounds of the board

        :param x:
        :param y:
        :return: true or false
        """

        return 0 <= x < self.board_size and 0 <= y < self.board_size

    def is_end(self):
        """
        Checks if the game is over.
        The game is over if any of the following occur:
            - A player has n consecutive tokens in a horizontal row
            - A player has n consecutive tokens in a vertical column
            - A player has n consecutive tokens in a diagonal
            - The board is full (i.e. a tie)

        Returns any of the following:
            - X if X is the winner
            - O if O is the winner
            - . if it's a tie
            - None if the game is not over

        :return: the winner (X,O, or . for tie) or None
        """

        # Check for winner
        for i in range(0, self.board_size):
            for j in range(0, self.board_size):

                # skip cell if it's empty or a block, since they can't be winners
                if self.current_state[i][j] in ['.', 'B']:
                    continue

                winner = self.current_state[i][j]
                streak = 0

                # Vertical
                for k in range(0, self.winning_size):
                    if self.valid_coord(i,j+k):
                        cell = self.current_state[i][j+k]
                        if winner == cell:
                            streak = streak + 1
                                
                if streak == self.winning_size:
                    return winner

                winner = self.current_state[i][j]
                streak = 0
                
                # Horizontal
                for k in range(0, self.winning_size):
                    if self.valid_coord(i+k,j):
                        cell = self.current_state[i+k][j]
                        if winner == cell:
                            streak = streak + 1
                
                if streak == self.winning_size:
                        return winner

                winner = self.current_state[i][j]
                streak = 0

                # Right Diagonal
                for k in range(0, self.winning_size):
                    if self.valid_coord(i+k,j+k):
                        cell = self.current_state[i+k][j+k]
                        if winner == cell:
                            streak = streak + 1
               
                if streak == self.winning_size:
                        return winner

                winner = self.current_state[i][j]
                streak = 0

                # Left Diagonal
                for k in range(0, self.winning_size):
                    if self.valid_coord(i + k, j - k):
                        cell = self.current_state[i + k][j - k]
                        if winner == cell:
                            streak = streak + 1

                if streak == self.winning_size:
                    return winner

        # Is whole board full?
        for i in range(0, self.board_size):
            for j in range(0, self.board_size):
                # There's an empty field, we continue the game
                if self.current_state[i][j] == '.':
                    return None

        # It's a tie!
        return '.'

    def check_end(self):
        """
        Displays a user-friendly message indicating the winner of the game (if any)
        If game is not over, simply returns value of is_end()

        :return: winner or value of is_end()
        """
        self.result = self.is_end()
        # Printing the appropriate message if the game has ended
        if self.result is not None:
            if self.result == 'X':
                print('The winner is X!')
            elif self.result == 'O':
                print('The winner is O!')
            elif self.result == '.':
                print("It's a tie!")
            self.initialize_board()
        return self.result

    def input_move(self):
        """
        Prompts player move
        """
        while True:
            print(F'Player {self.player_turn}, enter your move:')
            px = int(input('enter the x coordinate: '))
            py = int(input('enter the y coordinate: '))
            if self.is_valid_play(px, py):
                return px, py
            else:
                print('The move is not valid! Try again.')

    def switch_player(self):
        """
        Switches the turn player and updates the heuristic accordingly
        """
        if self.player_turn == 'X':
            self.player_turn = 'O'
            self.heuristic = self.heuristic_o
            self.max_depth = self.d2
            self.algo = self.algo2
        elif self.player_turn == 'O':
            self.player_turn = 'X'
            self.max_depth = self.d1
            self.heuristic = self.heuristic_x
            self.algo = self.algo1


        return self.player_turn

    def minimax(self, current_depth=0, max_turn=False):
        """
        Minimizing for 'X' and maximizing for 'O'
        Possible values are:
            -inf - win for 'X'
              0  - a tie
            inf  - loss for 'X'

        :param current_depth: required to determine when to stop traversing
        :param max_turn: boolean to decide which computation will be used (max or min)
        :return: the value of the heuristic being propagated along with the X,Y coordinates of the best computed move
        """

        value = 101
        if max_turn:
            value = -101
        x = None
        y = None

        current_depth = current_depth + 1

        # Iterate through every possible move (i, j)
        for i in range(0, self.board_size):
            for j in range(0, self.board_size):

                # Only consider valid moves (i.e. cells that are empty)
                if self.current_state[i][j] == '.':

                    # Update timer
                    move_time = time.time() - self.move_start

                    # If timer has expired, stop traversing and set the current depth as max depth
                    if not self.timer_is_up and move_time >= self.max_move_time:
                        self.max_depth_adjusted = current_depth
                        self.timer_is_up = True

                    # end traversal if resources are spent
                    end_of_traversal = current_depth == self.max_depth_adjusted
                    #print(str(end_of_traversal) + " " + str(self.timer_is_up) + " " + str(self.is_end()))

                    if max_turn:
                        self.current_state[i][j] = 'O'
                        if end_of_traversal or self.is_end():
                            #print("I'VE ARRIVED")
                            self.depths.append(current_depth)
                            if self.heuristic == self.E1 :
                                v = self.e()
                            else :
                                v = self.e2(current_depth)
                        else:
                            (v, _, _) = self.minimax(current_depth, max_turn=False)
                        if v > value:
                            value = v
                            x = i
                            y = j
                    else:
                        self.current_state[i][j] = 'X'
                        if end_of_traversal or self.is_end():
                            self.depths.append(current_depth)
                            if self.heuristic == self.E1 :
                                v = self.e()
                            else :
                                v = self.e2(current_depth)
                        else:
                            # current_depth = current_depth + 1
                            (v, _, _) = self.minimax(current_depth, max_turn=True)
                        if v < value:
                            value = v
                            x = i
                            y = j

                    # increase state count
                    self.state_count = self.state_count + 1

                    # Reset cell so that state is not permanently modified by A.I. traversal
                    self.current_state[i][j] = '.'
        
        # add state count to depth
        if current_depth not in self.state_count_p_depth:
            self.state_count_p_depth[current_depth] = 0

        self.state_count_p_depth[current_depth] += self.state_count

        #print("LEAVING STATE SO NOT IN INFINITE LOOP WOO!")
        return value, x, y

    def alphabeta(self, current_depth=0, alpha=-100, beta=100, max_turn=False):
        """
        A more efficient version of minimax (i.e. includes pruning)

        :param current_depth: required to determine when to stop traversing
        :param alpha: required for pruning
        :param beta: required for pruning
        :param max_turn: boolean to decide which computation will be used (max or min)
        :return: the value of the heuristic being propagated along with the X,Y coordinates of the best computed move
        """

        value = 101
        if max_turn:
            value = -101
        x = None
        y = None

        ard = []

        current_depth = current_depth + 1

        # Iterate through every possible move (i, j)
        rows = [*range(0,self.board_size)]
        random.shuffle(rows)
        cols = [*range(0,self.board_size)]
        random.shuffle(cols)

        for i in rows:
            for j in cols:

                # Only consider valid moves (i.e. cells that are empty)
                if self.current_state[i][j] == '.':

                    # Update timer
                    if time.time() - self.move_start > self.max_move_time :
                        self.timer_is_up = True

                    # If timer has expired, stop traversing and set the current depth as max depth
                    # if not self.timer_is_up and move_time >= self.max_move_time :
                    #     self.max_depth_adjusted = current_depth
                    #     self.timer_is_up = True

                    # end traversal if resources are spent
                    end_of_traversal = current_depth == self.max_depth

                    if max_turn:
                        self.current_state[i][j] = 'O'
                        if end_of_traversal or self.is_end() or self.timer_is_up:
                            self.depths.append(current_depth)
                            self.ard_per_move.append(current_depth)

                            if self.heuristic == self.E1 :
                                v = self.e()
                            else :
                                v= self.e2(current_depth)
                        else:
                            (v, _, _) = self.alphabeta(current_depth, alpha, beta, max_turn=False)
                        if v > value:
                            value = v
                            x = i
                            y = j
                    else:
                        self.current_state[i][j] = 'X'
                        if end_of_traversal or self.is_end() or self.timer_is_up:
                            self.depths.append(current_depth)
                            self.ard_per_move.append(current_depth)

                            if self.heuristic == self.E1 :
                                v = self.e()
                            else :
                                v = self.e2(current_depth)

                        else:
                            #current_depth = current_depth + 1
                            (v, _, _) = self.alphabeta(current_depth, alpha, beta, max_turn=True)
                        if v < value:
                            value = v
                            x = i
                            y = j
                    
                    # increase state count
                    self.state_count = self.state_count + 1

                    # Reset cell so that state is not permanently modified by A.I. traversal
                    self.current_state[i][j] = '.'

                    if(self.timer_is_up):
                        return value, x ,y
                        
                    # Prune unnecessary siblings
                    if max_turn:
                        if value >= beta:
                            return value, x, y
                        if value > alpha:
                            alpha = value
                    else:
                        if value <= alpha:
                            return value, x, y
                        if value < beta:
                            beta = value

            
        self.ard_per_move[0] = sum(self.ard_per_move)/len(self.ard_per_move)
        self.ard_per_move = self.ard_per_move[0:]
        # add state count to depth
        if current_depth not in self.state_count_p_depth:
            self.state_count_p_depth[current_depth] = 0
            
        self.state_count_p_depth[current_depth] += self.state_count

        return value, x, y

    def e(self):
        start = time.time()
        
        score = 0
        count_o = 0
        count_x = 0

        for row in self.current_state:
            for col in range(len(row)):
                if row[col] == 'O':
                    count_o = count_o + 1
                elif row[col] == 'X':
                    count_x = count_x + 1
            
            if count_o == self.winning_size:
                score = score + 2
            if count_o >= self.winning_size/2:
                score = score + 1
            else:
                score = score + 1

        self.heuristic_times.append(time.time() - start)
        
        return score +  count_o
    
    def e2(self, current_depth):
        """
        More complicated heuristic which will check all winning situations for X and O
        and return the difference in terms of O (i.e. O - X).

        The current depth is required to determine how close the winning or losing situation is
        (i.e., a loss in current turn should be prioritized over a loss in three turns)

        :param current_depth:
        :return:    - +101 if O wins
                    - -101 if X wins
                    - 0 if a tie
                    - otherwise, winning situations for O minus winning situations for X
        """

        start = time.time()
        winning_x = 0
        winning_o = 0

        # check obvious scores (i.e. if there's a winner or a tie)
        if self.is_end() == 'X':
            return -100*(1/(current_depth+1))
        if self.is_end() == 'O':
            return 100*(1/(current_depth+1))
        if self.is_end() == '.':
            return 0

        # calculate score otherwise (i.e. scenarios O is winning minus scenarios X is winning)
        for i in range(0, self.board_size):
            for j in range(0, self.board_size):

                # skip cell if a block
                if self.current_state[i][j] == 'B':
                    continue

                winner = self.current_state[i][j]
                streak = 0

                # Vertical
                for k in range(0, self.winning_size):
                    if self.valid_coord(i, j + k):
                        cell = self.current_state[i][j + k]

                        # overwrite winner if it can go either way (i.e. an empty token)
                        if winner == '.':
                            winner = cell

                        if winner == cell or cell == '.':
                            streak = streak + 1

                # increment winning score accordingly
                if streak == self.winning_size:
                    if winner == 'X':
                        winning_x += 1
                    elif winner == 'O':
                        winning_o += 1
                    elif winner == '.':
                        winning_x += 1
                        winning_o += 1

                winner = self.current_state[i][j]
                streak = 0

                # Horizontal
                for k in range(0, self.winning_size):
                    if self.valid_coord(i + k, j):
                        cell = self.current_state[i + k][j]

                        # overwrite winner if it can go either way (i.e. an empty token)
                        if winner == '.':
                            winner = cell

                        if winner == cell or cell == '.':
                            streak = streak + 1

                # increment winning score accordingly
                if streak == self.winning_size:
                    if winner == 'X':
                        winning_x += 1
                    elif winner == 'O':
                        winning_o += 1
                    elif winner == '.':
                        winning_x += 1
                        winning_o += 1

                winner = self.current_state[i][j]
                streak = 0

                # Right Diagonal
                for k in range(0, self.winning_size):
                    if self.valid_coord(i + k, j + k):
                        cell = self.current_state[i + k][j + k]

                        # overwrite winner if it can go either way (i.e. an empty token)
                        if winner == '.':
                            winner = cell

                        if winner == cell or cell == '.':
                            streak = streak + 1

                # increment winning score accordingly
                if streak == self.winning_size:
                    if winner == 'X':
                        winning_x += 1
                    elif winner == 'O':
                        winning_o += 1
                    elif winner == '.':
                        winning_x += 1
                        winning_o += 1

                winner = self.current_state[i][j]
                streak = 0

                # Left Diagonal
                for k in range(0, self.winning_size):
                    if self.valid_coord(i + k, j - k):
                        cell = self.current_state[i + k][j - k]

                        # overwrite winner if it can go either way (i.e. an empty token)
                        if winner == '.':
                            winner = cell

                        if winner == cell or cell == '.':
                            streak = streak + 1

                # increment winning score accordingly
                if streak == self.winning_size:
                    if winner == 'X':
                        winning_x += 1
                    elif winner == 'O':
                        winning_o += 1
                    elif winner == '.':
                        winning_x += 1
                        winning_o += 1

        self.heuristic_times.append(time.time() - start)

        return winning_o-winning_x
                    
    def printInitialGame(self):
        print("n: "+ str(self.board_size))
        print("b: "+ str(self.blocks))
        print("s: "+ str(self.winning_size))
        print("t: " + str(self.max_move_time))
        if(self.player_x == self.AI):
            print("Player X: AI")
        else:
            print("Player X: Human")
            
        if(self.player_o == self.AI):
            print("Player O: AI")
        else:
            print("Player O: Human")
        print("Player O: "+ str(self.player_o))
        if(self.algo1 == self.ALPHABETA):
            print("Algo for X: ALPHABETA")
        else:
            print("Algo for ): MINIMAX")
        if(self.algo2 == self.ALPHABETA):
            print("Algo for O: ALPHABETA")
        else:
            print("Algo for O: MINIMAX")

        if(self.heuristic_x == self.E1):
            print("Player X heuristic: E1")
        else:
            print("Player X heuristic: E2")
        if(self.heuristic_o == self.E1):
            print("Player O heuristic: E1")
        else:
            print("Player O heuristic: E2")

    def getStats(self):
        return (sum(self.total_heuristic_times)/len(self.total_heuristic_times), 
        self.total_state_counts,sum(self.depth_averages)/len(self.depth_averages),self.total_state_counts_p_depth,
        sum(self.ard_averages)/len(self.ard_averages),self.move_counter)

    def play(self):
        sys.stdout = PrintManager()
        sys.stdout.setPath(F'gameTrace-{self.board_size}{self.blocks}{self.winning_size}{self.max_move_time}.txt')

        self.printInitialGame()
        game_over = False
        self.move_counter = 0
        while not game_over:
            self.draw_board()
            if self.check_end():
                game_over = True
                print('i. Average evaluation time of heuristic: ' + str(1.0*sum(self.total_heuristic_times)/len(self.total_heuristic_times)))
                print('ii. Total states evaluated: ' + str(self.total_state_counts))  
                print('iii. Average of average depths: '+ str(sum(self.depth_averages)/len(self.depth_averages)))
                print('iv. Total number of states evaluated at each depth: ') 
                for depth in sorted(self.total_state_counts_p_depth.keys(), reverse=True):
                    print("\t" + str(depth) + ": " + str(self.total_state_counts_p_depth[depth]))
                print('v. Average ARD: ' + str(sum(self.ard_averages)/len(self.ard_averages)))
                print('vi. Total Move Count: ' + str(self.move_counter))
                return

            self.move_start = time.time()
            #signal.signal(signal.SIGALRM, timeoutHandler)
            #signal.alarm(self.maxTurnTime)

            if self.algo == self.MINIMAX:
                if self.player_turn == 'X':
                    (v, x, y) = self.minimax(max_turn=False)
                else:
                    (v, x, y) = self.minimax(max_turn=True)

            else: # algo == self.ALPHABETA
                if self.player_turn == 'X':
                    (v, x, y) = self.alphabeta(max_turn=False)
                else:
                    (v, x, y) = self.alphabeta(max_turn=True)
            end = time.time()

            eval_time = round(end - self.move_start, 7)
            self.move_counter += 1
            
            print('Heuristic returned: ' + str(v))
            print(F'i. Evaluation time: {eval_time}s')
            print('i. Heuristic evaluation time: ' + str(sum(self.heuristic_times)))
            print("ii. Number of states evaluated: " + str(self.state_count))
            print("iii. Number of states evaluated per depth:")
            for depth in sorted(self.state_count_p_depth.keys(), reverse=True):
                print("\t"+str(depth) + ": " + str(self.state_count_p_depth[depth]))
            print("iv. Average depths of heuristic evaluation: " + str(round(1.0*sum(self.depths)/len(self.depths),4)))
            print("v. ARD: "+ str(self.ard_per_move[0]))
            if (self.player_turn == 'X' and self.player_x == self.HUMAN) or (self.player_turn == 'O' and self.player_o == self.HUMAN):
                    if self.recommend:
                        print(F'Recommended move: x = {x}, y = {y}')
                    (x,y) = self.input_move()
            elif (self.player_turn == 'X' and self.player_x == self.AI) or (self.player_turn == 'O' and self.player_o == self.AI):
                        print(F'Player {self.player_turn} under AI control plays: x = {x}, y = {y}')

            # store stat variables before resetting
            self.total_heuristic_times.extend(self.heuristic_times)
            self.total_state_counts += self.state_count
            for depth in self.state_count_p_depth:
                if depth not in self.total_state_counts_p_depth :
                    self.total_state_counts_p_depth[depth] = 0
                self.total_state_counts_p_depth[depth] += self.state_count_p_depth[depth]
            self.depth_averages.append(1.0*sum(self.depths)/ len(self.depths))
            self.ard_averages.append(self.ard_per_move[0])
            

            # reset variables
            self.heuristic_times = []
            self.state_count = 0
            self.state_count_p_depth = {}
            self.depths = []
            self.max_depth_adjusted = self.max_depth
            self.timer_is_up = False
            self.current_state[x][y] = self.player_turn
            self.ard_per_move = []
            self.switch_player()

        self.initialize_game()       
    
