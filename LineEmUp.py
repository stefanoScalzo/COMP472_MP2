# !/usr/bin/env python
# coding: utf-8

# based on code from https://stackabuse.com/minimax-and-alpha-beta-pruning-in-python

import time
import random
from PrintManager import PrintManager


class LineEmUp:
    MINIMAX = 0
    ALPHABETA = 1
    HUMAN = 0
    AI = 1
    E1 = 0
    E2 = 1

    def __init__(self, board_size=3, blocks=0, blocks_coord=[], winning_size=3, d1=7, d2=7,
                 max_move_time=5, player_w=AI, player_b=AI, recommend=True, heuristic_w=E2, heuristic_b=E2,
                 a1=ALPHABETA, a2=ALPHABETA):
        """
        Constructor for the game.

        :param board_size: nxn configuration of board
        :param blocks: number of Block nodes in game
        :param blocks_coord:
        :param winning_size:
        :param d1:
        :param d2:
        :param max_move_time:
        :param player_w:
        :param player_b:
        :param recommend:
        :param heuristic_w:
        :param heuristic_b:
        :param a1:
        :param a2:
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
        self.a1 = a1
        self.a2 = a2
        self.player_w = player_w
        self.player_b = player_b
        self.heuristic_w = heuristic_w
        self.heuristic_b = heuristic_b

        self.initialize_game()

    def initialize_game(self):
        """
        Initializes the board and necessary variables so that the game can be restarted with same parameters
        :return:
        """

        # variables required for stats
        self.move_counter = 0
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

        # Player White always plays first
        self.player_turn = 'W'
        self.heuristic = self.heuristic_w
        self.max_depth = self.d1
        self.algo = self.a1

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
            self.current_state[coord[0]][coord[1]] = 'x'

    def draw_board(self, printer):
        """
        Prints the board to the console
        :return:
        """
        printer.write("\n")
        for x in range(0, self.board_size):
            for y in range(0, self.board_size):
                printer.write(F'{self.current_state[x][y]}    ')
            printer.write("\n")
        printer.write("\n")

    def is_valid_play(self, x, y):
        """
        Checks that the provided coordinates x, y would be a valid move for a player to make
        :param x:
        :param y:
        :return: true or false
        """
        if not self.valid_coord(x, y):
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
            - W if White is the winner
            - B if Black is the winner
            - . if it's a tie
            - None if the game is not over
        :return: the winner (W,B, or . for tie) or None
        """

        # Check for winner
        for i in range(0, self.board_size):
            for j in range(0, self.board_size):

                # skip cell if it's empty or a block, since they can't be winners
                if self.current_state[i][j] in ['.', 'x']:
                    continue

                winner = self.current_state[i][j]
                streak = 0

                # Vertical
                for k in range(0, self.winning_size):
                    if self.valid_coord(i, j + k):
                        cell = self.current_state[i][j + k]
                        if winner == cell:
                            streak = streak + 1

                if streak == self.winning_size:
                    return winner

                winner = self.current_state[i][j]
                streak = 0

                # Horizontal
                for k in range(0, self.winning_size):
                    if self.valid_coord(i + k, j):
                        cell = self.current_state[i + k][j]
                        if winner == cell:
                            streak = streak + 1

                if streak == self.winning_size:
                    return winner

                winner = self.current_state[i][j]
                streak = 0

                # Right Diagonal
                for k in range(0, self.winning_size):
                    if self.valid_coord(i + k, j + k):
                        cell = self.current_state[i + k][j + k]
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
            if self.result == 'W':
                print('The winner is White!')
            elif self.result == 'B':
                print('The winner is Black!')
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
        if self.player_turn == 'W':
            self.player_turn = 'B'
            self.heuristic = self.heuristic_b
            self.max_depth = self.d2
            self.algo = self.a2
        elif self.player_turn == 'B':
            self.player_turn = 'W'
            self.max_depth = self.d1
            self.heuristic = self.heuristic_w
            self.algo = self.a1

        return self.player_turn

    def minimax(self, current_depth=0, max_turn=False):
        """
        Minimizing for 'W' and maximizing for 'B'
        Possible values are:
            -inf - win for 'W'
              0  - a tie
            inf  - loss for 'W'
        :param current_depth: required to determine when to stop traversing
        :param max_turn: boolean to decide which computation will be used (max or min)
        :return: the value of the heuristic being propagated along with the x,y coordinates of the best computed move
        """

        value = 101
        if max_turn:
            value = -101
        x = None
        y = None

        current_depth = current_depth + 1

        rows = [*range(0, self.board_size)]
        random.shuffle(rows)
        cols = [*range(0, self.board_size)]
        random.shuffle(cols)

        # Iterate through every possible move (i, j)
        for i in range(0, self.board_size):
            for j in range(0, self.board_size):

                # Only consider valid moves (i.e. cells that are empty)
                if self.current_state[i][j] == '.':

                    # Update timer
                    if time.time() - self.move_start > self.max_move_time:
                        self.timer_is_up = True

                    # end traversal if resources are spent
                    end_of_traversal = current_depth == self.max_depth

                    if max_turn:
                        self.current_state[i][j] = 'B'
                        if end_of_traversal or self.is_end() or self.timer_is_up:
                            self.depths.append(current_depth)
                            self.ard_per_move.append(current_depth)
                            if self.heuristic == self.E1:
                                v = self.e()
                            else:
                                v = self.e2(current_depth)
                        else:
                            (v, _, _) = self.minimax(current_depth, max_turn=False)
                        if v > value:
                            value = v
                            x = i
                            y = j
                    else:
                        self.current_state[i][j] = 'W'
                        if end_of_traversal or self.is_end() or self.timer_is_up:
                            self.depths.append(current_depth)
                            self.ard_per_move.append(current_depth)
                            if self.heuristic == self.E1:
                                v = self.e()
                            else:
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
                     # add state count to depth
                    if current_depth not in self.state_count_p_depth:
                        self.state_count_p_depth[current_depth] = 0

                    self.state_count_p_depth[current_depth] += 1

                    # Reset cell so that state is not permanently modified by A.I. traversal
                    self.current_state[i][j] = '.'

                    if (self.timer_is_up):
                        return value, x, y

        self.ard_per_move[0] = sum(self.ard_per_move) / len(self.ard_per_move)
        self.ard_per_move = self.ard_per_move[0:]
       

        # print("LEAVING STATE SO NOT IN INFINITE LOOP WOO!")
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
        rows = [*range(0, self.board_size)]
        random.shuffle(rows)
        cols = [*range(0, self.board_size)]
        random.shuffle(cols)

        for i in rows:
            for j in cols:

                # Only consider valid moves (i.e. cells that are empty)
                if self.current_state[i][j] == '.':

                    # Update timer
                    if time.time() - self.move_start > self.max_move_time:
                        self.timer_is_up = True

                    # If timer has expired, stop traversing and set the current depth as max depth
                    # if not self.timer_is_up and move_time >= self.max_move_time :
                    #     self.max_depth_adjusted = current_depth
                    #     self.timer_is_up = True

                    # end traversal if resources are spent
                    end_of_traversal = current_depth == self.max_depth

                    if max_turn:
                        self.current_state[i][j] = 'B'
                        if end_of_traversal or self.is_end() or self.timer_is_up:
                            self.depths.append(current_depth)
                            self.ard_per_move.append(current_depth)

                            if self.heuristic == self.E1:
                                v = self.e()
                            else:
                                v = self.e2(current_depth)
                        else:
                            (v, _, _) = self.alphabeta(current_depth, alpha, beta, max_turn=False)
                        if v > value:
                            value = v
                            x = i
                            y = j
                    else:
                        self.current_state[i][j] = 'W'
                        if end_of_traversal or self.is_end() or self.timer_is_up:
                            self.depths.append(current_depth)
                            self.ard_per_move.append(current_depth)

                            if self.heuristic == self.E1:
                                v = self.e()
                            else:
                                v = self.e2(current_depth)

                        else:
                            # current_depth = current_depth + 1
                            (v, _, _) = self.alphabeta(current_depth, alpha, beta, max_turn=True)
                        if v < value:
                            value = v
                            x = i
                            y = j

                    # increase state count
                    self.state_count = self.state_count + 1
                    # add state count to depth
                    if current_depth not in self.state_count_p_depth:
                        self.state_count_p_depth[current_depth] = 0

                    self.state_count_p_depth[current_depth] += 1

                    # Reset cell so that state is not permanently modified by A.I. traversal
                    self.current_state[i][j] = '.'

                    if (self.timer_is_up):
                        return value, x, y

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

        self.ard_per_move[0] = sum(self.ard_per_move) / len(self.ard_per_move)
        self.ard_per_move = self.ard_per_move[0:]
        

        return value, x, y

    def e(self):
        start = time.time()

        score = 0
        count_b = 0
        count_w = 0

        for row in self.current_state:
            for col in range(len(row)):
                if row[col] == 'B':
                    count_b += 1
                elif row[col] == 'W':
                    count_w += 1

            if count_b == self.winning_size:
                score = score + 2
            if count_b >= self.winning_size / 2:
                score = score + 1
            else:
                score = score + 1

        self.heuristic_times.append(time.time() - start)

        return score + count_b

    def e2(self, current_depth):
        """
        More complicated heuristic which will check all winning situations for W and B
        and return the difference in terms of O (i.e. B - W).
        The current depth is required to determine how close the winning or losing situation is
        (i.e., a loss in current turn should be prioritized over a loss in three turns)
        :param current_depth:
        :return:    - +101 if Black wins
                    - -101 if Black loses
                    - 0 if a tie
                    - otherwise, winning situations for Black minus winning situations for White
        """

        start = time.time()
        winning_w = 0
        winning_b = 0

        # check obvious scores (i.e. if there's a winner or a tie)
        if self.is_end() == 'W':
            return -100 * (1 / (current_depth + 1))
        if self.is_end() == 'B':
            return 100 * (1 / (current_depth + 1))
        if self.is_end() == '.':
            return 0

        # calculate score otherwise (i.e. scenarios B is winning minus scenarios W is winning)
        for i in range(0, self.board_size):
            for j in range(0, self.board_size):

                # skip cell if a block
                if self.current_state[i][j] == 'x':
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
                    if winner == 'W':
                        winning_w += 1
                    elif winner == 'B':
                        winning_b += 1
                    elif winner == '.':
                        winning_w += 1
                        winning_b += 1

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
                    if winner == 'W':
                        winning_w += 1
                    elif winner == 'B':
                        winning_b += 1
                    elif winner == '.':
                        winning_w += 1
                        winning_b += 1

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
                    if winner == 'W':
                        winning_w += 1
                    elif winner == 'B':
                        winning_b += 1
                    elif winner == '.':
                        winning_w += 1
                        winning_b += 1

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
                    if winner == 'W':
                        winning_w += 1
                    elif winner == 'B':
                        winning_b += 1
                    elif winner == '.':
                        winning_w += 1
                        winning_b += 1

        self.heuristic_times.append(time.time() - start)

        return winning_b - winning_w

    def printInitialGame(self, printer):
        """
        Prints stats pertaining to the beginning of the game such as
        board size, blocks, number of nodes needed in a row to win, etc.
        :return:
        """
        printer.write("n: " + str(self.board_size) + '\n')
        printer.write("b: " + str(self.blocks) + '\n')
        printer.write("s: " + str(self.winning_size) + '\n')
        printer.write("t: " + str(self.max_move_time) + '\n')
        printer.write("d1: " + str(self.d1) + '\n')
        printer.write("d2: " + str(self.d2) + '\n')
        if (self.player_w == self.AI):
            printer.write("Player White: AI" + '\n')
        else:
            printer.write("Player White: Human" + '\n')

        if (self.player_b == self.AI):
            printer.write("Player Black: AI" + '\n')
        else:
            printer.write("Player Black: Human" + '\n')
        if (self.a1 == self.ALPHABETA):
            printer.write("Algo for White: ALPHABETA" + '\n')
        else:
            printer.write("Algo for White: MINIMAX" + '\n')
        if (self.a2 == self.ALPHABETA):
            printer.write("Algo for Black: ALPHABETA" + '\n')
        else:
            printer.write("Algo for Black: MINIMAX" + '\n')

        if (self.heuristic_w == self.E1):
            printer.write("Player White heuristic: E1" + '\n')
        else:
            printer.write("Player White heuristic: E2" + '\n')
        if (self.heuristic_b == self.E1):
            printer.write("Player Black heuristic: E1" + '\n')
        else:
            printer.write("Player Black heuristic: E2" + '\n')

    def printIntialGameToFile(self, file):
        file.write("n: " + str(self.board_size) + '\n')
        file.write("b: " + str(self.blocks) + '\n')
        file.write("s: " + str(self.winning_size) + '\n')
        file.write("t: " + str(self.max_move_time) + '\n')
        file.write("d1: " + str(self.d1) + '\n')
        file.write("d2: " + str(self.d2) + '\n')
        if (self.player_w == self.AI):
            file.write("Player White: AI" + '\n')
        else:
            file.write("Player White: Human" + '\n')

        if (self.player_b == self.AI):
            file.write("Player Black: AI" + '\n')
        else:
            file.write("Player Black: Human" + '\n')
        if (self.a1 == self.ALPHABETA):
            file.write("Algo for White: ALPHABETA" + '\n')
        else:
            file.write("Algo for White: MINIMAX" + '\n')
        if (self.a2 == self.ALPHABETA):
            file.write("Algo for Black: ALPHABETA" + '\n')
        else:
            file.write("Algo for Black: MINIMAX" + '\n')

        if (self.heuristic_w == self.E1):
            file.write("Player White heuristic: E1" + '\n')
        else:
            file.write("Player White heuristic: E2" + '\n')
        if (self.heuristic_b == self.E1):
            file.write("Player Black heuristic: E1" + '\n')
        else:
            file.write("Player Black heuristic: E2" + '\n')

    def getStats(self):
        """
        :return: a tuple of all the stats
        """
        return (sum(self.total_heuristic_times) / len(self.total_heuristic_times),
                self.total_state_counts, sum(self.depth_averages) / len(self.depth_averages),
                self.total_state_counts_p_depth,
                sum(self.ard_averages) / len(self.ard_averages), self.move_counter,
                self.result)

    def play(self):
        """
        Loops through the game until it is over
        :return:
        """
        printer = PrintManager()
        printer.setPath(F'gameTrace-{self.board_size}{self.blocks}{self.winning_size}{self.max_move_time}.txt')

        self.printInitialGame(printer)

        while True:
            self.draw_board(printer)
            if self.check_end():
                printer.write('i. Average evaluation time of heuristic: ' + str(
                    1.0 * sum(self.total_heuristic_times) / len(self.total_heuristic_times)) + '\n')
                printer.write('ii. Total states evaluated: ' + str(self.total_state_counts) + '\n')
                printer.write('iii. Average of average depths: ' + str(
                    sum(self.depth_averages) / len(self.depth_averages)) + '\n')
                printer.write('iv. Total number of states evaluated at each depth: \n')
                for depth in sorted(self.total_state_counts_p_depth.keys(), reverse=True):
                    printer.write("\t" + str(depth) + ": " + str(self.total_state_counts_p_depth[depth]) + '\n')
                printer.write('v. Average ARD: ' + str(sum(self.ard_averages) / len(self.ard_averages)) + '\n')
                printer.write('vi. Total Move Count: ' + str(self.move_counter) + '\n')
                return

            self.move_start = time.time()

            if self.algo == self.MINIMAX:
                if self.player_turn == 'W':
                    (v, x, y) = self.minimax(max_turn=False)
                else:
                    (v, x, y) = self.minimax(max_turn=True)

            else:  # algo == self.ALPHABETA
                if self.player_turn == 'W':
                    (v, x, y) = self.alphabeta(max_turn=False)
                else:
                    (v, x, y) = self.alphabeta(max_turn=True)
            end = time.time()

            eval_time = round(end - self.move_start, 7)
            self.move_counter += 1

            printer.write('Heuristic returned: ' + str(v) + '\n')
            printer.write(F'i. Evaluation time: {eval_time}s')
            printer.write('i. Heuristic evaluation time: ' + str(sum(self.heuristic_times)) + '\n')
            printer.write("ii. Number of states evaluated: " + str(self.state_count) + '\n')
            printer.write("iii. Number of states evaluated per depth:\n")
            for depth in sorted(self.state_count_p_depth.keys(), reverse=True):
                printer.write("\t" + str(depth) + ": " + str(self.state_count_p_depth[depth]) + '\n')
            printer.write("iv. Average depths of heuristic evaluation: " + str(
                (1.0 * sum(self.depths) / len(self.depths))) + '\n')
            printer.write("v. ARD: " + str(self.ard_per_move[0]) + '\n')

            if (self.player_turn == 'W' and self.player_w == self.HUMAN) or (
                    self.player_turn == 'B' and self.player_b == self.HUMAN):
                if self.recommend:
                    print(F'Recommended move: x = {x}, y = {y}') + '\n'
                (x, y) = self.input_move()
            elif (self.player_turn == 'W' and self.player_w == self.AI) or (
                    self.player_turn == 'B' and self.player_b == self.AI):
                print(F'Player {self.player_turn} under AI control plays: x = {x}, y = {y}' + '\n')

            # store stat variables before resetting
            self.total_heuristic_times.extend(self.heuristic_times)
            self.total_state_counts += self.state_count
            for depth in self.state_count_p_depth:
                if depth not in self.total_state_counts_p_depth:
                    self.total_state_counts_p_depth[depth] = 0
                self.total_state_counts_p_depth[depth] += self.state_count_p_depth[depth]
            self.depth_averages.append(1.0 * sum(self.depths) / len(self.depths))
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
