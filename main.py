#!/usr/bin/env python
# coding: utf-8

# based on code from https://stackabuse.com/minimax-and-alpha-beta-pruning-in-python

import time
import signal

class Game:
    MINIMAX = 0
    ALPHABETA = 1
    HUMAN = 2
    AI = 3
    board_size = 0
    current_state = []
    winningSize = 3
    timer = 1

    def __init__(self, board_size, blocks, blockCoord, winningSize,timer, recommend = True):
        self.board_size = board_size
        self.winningSize = winningSize
        self.initialize_blocks(blocks, blockCoord)
        self.initialize_game()
        self.recommend = recommend
        
    def initialize_blocks(self, blocks, blockCoord):
        for r in range(0, self.board_size):
            self.current_state.append(['.' for c in range(0, self.board_size)])
            
        for x in range(0, self.board_size):
            for y in range(0, self.board_size):
                if(len(list((filter(lambda item: item['x']==x , blockCoord))))+len(list((filter(lambda item: item['y']==y , blockCoord))))>1):
                    self.current_state[x][y]='B'
        
    def initialize_game(self):
        for r in range(0, self.board_size):
            self.current_state.append([0 for c in range(0, self.board_size)])
            
        for x in range(0, self.board_size):
            for y in range(0, self.board_size):
                if(self.current_state[x][y]!='B'):
                    self.current_state[x][y]='.'
        # Player X always plays first
        self.player_turn = 'X'

    def e3(self, current_depth):
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
                for k in range(0, self.winningSize):
                    if self.valid_coord(i, j + k):
                        cell = self.current_state[i][j + k]

                        # overwrite winner if it can go either way (i.e. an empty token)
                        if winner == '.':
                            winner = cell

                        if winner == cell or cell == '.':
                            streak = streak + 1

                # increment winning score accordingly
                if streak == self.winningSize:
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
                for k in range(0, self.winningSize):
                    if self.valid_coord(i + k, j):
                        cell = self.current_state[i + k][j]

                        # overwrite winner if it can go either way (i.e. an empty token)
                        if winner == '.':
                            winner = cell

                        if winner == cell or cell == '.':
                            streak = streak + 1

                # increment winning score accordingly
                if streak == self.winningSize:
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
                for k in range(0, self.winningSize):
                    if self.valid_coord(i + k, j + k):
                        cell = self.current_state[i + k][j + k]

                        # overwrite winner if it can go either way (i.e. an empty token)
                        if winner == '.':
                            winner = cell

                        if winner == cell or cell == '.':
                            streak = streak + 1

                # increment winning score accordingly
                if streak == self.winningSize:
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
                for k in range(0, self.winningSize):
                    if self.valid_coord(i + k, j - k):
                        cell = self.current_state[i + k][j - k]

                        # overwrite winner if it can go either way (i.e. an empty token)
                        if winner == '.':
                            winner = cell

                        if winner == cell or cell == '.':
                            streak = streak + 1

                # increment winning score accordingly
                if streak == self.winningSize:
                    if winner == 'X':
                        winning_x += 1
                    elif winner == 'O':
                        winning_o += 1
                    elif winner == '.':
                        winning_x += 1
                        winning_o += 1

        return winning_o-winning_x
        
    def e1(self, posX, posY): #checks around the one we want to put
        if(posX>=self.board_size | posY>self.board_size):
            return -100
        elif(self.current_state[posX][posY]!='.'):
            return -100
        else:
            available = 0
            for x in range(posX-1,posX+1):
                for y in range(posY-1, posY+1):
                    if(x>=0 & x<self.board_size & y>=0 & y<self.board_size & x != posX & y!=posY):
                        #if not off board and not the actual index
                        if(self.current_state[x][y]=='.' or self.current_state[x][y]=='X'):
                            available = available + 1
                        elif(self.current_state[x][y]=='O'):
                            available = available -10
            return available

    def e2(self, posX, posY): # Player is X or O
        if(self.e2(posX,posY,'O') > self.winningSize - 1):#absolute defence needed
            return 100
        else: return self.e2(self,posX,posY,'X')

    def e2(self, posX, posY, player): #Player is X or Y
        if(posX>=self.board_size | posY>self.board_size):
            return -100
        elif(self.current_state[posX][posY]!='.'):
            return -100
        else:
            available = 0
            for x in range(posX,posX+self.winningSize): #to the right
                if(x>=0 & x<self.board_size & posY>=0 & posY<self.board_size):
                    if(self.current_state[x][posY]=='.'):
                        available = available + 1
                    else: available = available * 0.1    #so that if there are no moves left he places his token
            for x in range(posX-self.winningSize,posX): #to the left
                if(x>=0 & x<self.board_size & posY>=0 & posY<self.board_size):
                    if(self.current_state[x][posY]=='.' | self.current_state[x][posY]==player):
                        available = available + 1
                    else: available = available * 0.1

            for y in range(posX,posX+self.winningSize): #to the top
                if(posX>=0 & posX<self.board_size & y>=0 & y<self.board_size):
                    if(self.current_state[x][posY]=='.' | self.current_state[x][posY]==player):
                        available = available + 1
                    else: available = available * 0.1

            for y in range(posX-self.winningSize,posX): #to the bottom
                if(posX>=0 & posX<self.board_size & y>=0 & y<self.board_size):
                    if(self.current_state[posX][y]=='.' | self.current_state[posX][y]==player):
                        available = available + 1
                    else: available = available * 0.1
            for increase in range(0,self.winningSize): #to the top right diagonal
                if(posX+increase<self.board_size & y+increase<self.board_size):
                    if(self.current_state[posX+increase][posY+increase]=='.' | self.current_state[posX+increase][posY+increase]==player):
                        available = available + 1
                    else: available = available * 0.1
            for increase in range(0,self.winningSize): #to the bottom right diagonal
                if(posX+increase<self.board_size & y-increase>=0):
                    if(self.current_state[posX+increase][posY-increase]=='.' | self.current_state[posX+increase][posY-increase]==player):
                        available = available + 1
                    else: available = available * 0.1
            for increase in range(0,self.winningSize): #to the bottom left diagonal
                if(x-increase>=0 & y-increase>=0):
                    if(self.current_state[posX-increase][posY-increase]=='.' | self.current_state[posX-increase][posY-increase]==player):
                        available = available + 1
                    else: available = available * 0.1
            for increase in range(0,self.winningSize): #to the top left diagonal
                if(x-increase>=0 & posY+increase<self.board_size):
                    if(self.current_state[posX-increase][posY+increase]=='.' | self.current_state[posX-increase][posY+increase]==player):
                        available = available + 1
                    else: available = available * 0.1
            return available

    def draw_board(self):
        print()
        for x in range(0, self.board_size):
            for y in range(0, self.board_size):
                print(F'{self.current_state[x][y]}', end="  ")
            print()
        print()
        
    def is_valid(self, px, py):
        if px < 0 or px > 2 or py < 0 or py > 2:
            return False
        elif self.current_state[px][py] != '.':
            return False
        else:
            return True

    def valid_coord(self, x, y):
        return x >= 0 and x < self.board_size and y >= 0 and y < self.board_size

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
                for k in range(0, self.winningSize):
                    if self.valid_coord(i,j+k):
                        cell = self.current_state[i][j+k]
                        if winner == cell:
                            streak = streak + 1
                                
                if streak == self.winningSize:
                    return winner

                winner = self.current_state[i][j]
                streak = 0
                
                # Horizontal
                for k in range(0, self.winningSize):
                    if self.valid_coord(i+k,j):
                        cell = self.current_state[i+k][j]
                        if winner == cell:
                            streak = streak + 1
                
                if streak == self.winningSize:  
                        return winner

                winner = self.current_state[i][j]
                streak = 0

                # Right Diagonal
                for k in range(0, self.winningSize):
                    if self.valid_coord(i+k,j+k):
                        cell = self.current_state[i+k][j+k]
                        if winner == cell:
                            streak = streak + 1
               
                if streak == self.winningSize:  
                        return winner

                winner = self.current_state[i][j]
                streak = 0

                # Left Diagonal
                for k in range(0, self.winningSize):
                    if self.valid_coord(i + k, j - k):
                        cell = self.current_state[i + k][j - k]
                        if winner == cell:
                            streak = streak + 1

                if streak == self.winningSize:
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
            self.initialize_game()
        return self.result

    def input_move(self):
        while True:
            print(F'Player {self.player_turn}, enter your move:')
            px = int(input('enter the x coordinate: '))
            py = int(input('enter the y coordinate: '))
            if self.is_valid(px, py):
                return px, py
            else:
                print('The move is not valid! Try again.')

    def switch_player(self):
        if self.player_turn == 'X':
            self.player_turn = 'O'
        elif self.player_turn == 'O':
            self.player_turn = 'X'
        return self.player_turn

    # variables requires for minimax & alphabeta Adversial Searches
    max_depth = 3
    maxTurnTime = 5
    max_depth_adjusted = max_depth
    timer_is_up = False

    def minimax(self, current_depth=0, max=False):
        """
        Minimizing for 'X' and maximizing for 'O'
        Possible values are:
            -inf - win for 'X'
              0  - a tie
            inf  - loss for 'X'

        :param current_depth: required to determine when to stop traversing
        :param max: boolean to decide which computation will be used (max or min)
        :return: the value of the heuristic being propagated along with the X,Y coordinates of the best computed move
        """

        value = 100
        if max:
            value = -100
        x = None
        y = None

        # Iterate through every possible move (i, j)
        for i in range(0, self.board_size):
            for j in range(0, self.board_size):

                # Update timer
                move_time = time.time() - self.move_start

                # Only consider valid moves (i.e. cells that are empty)
                if self.current_state[i][j] == '.':

                    # If timer is has expired, stop traversing and set the current depth as max depth
                    if not self.timer_is_up and move_time >= self.maxTurnTime :
                        self.max_depth_adjusted = current_depth
                        self.timer_is_up = True

                    # End traversal when resources are spent or game is over
                    end_of_traversal = current_depth == self.max_depth_adjusted or self.is_end()
                    if end_of_traversal:
                        v = self.e3()

                    if max:
                        self.current_state[i][j] = 'O'
                        if not end_of_traversal:
                            current_depth = current_depth + 1
                            (v, _, _) = self.minimax(current_depth, max=False)
                        if v > value:
                            value = v
                            x = i
                            y = j
                    else:
                        self.current_state[i][j] = 'X'
                        if not end_of_traversal:
                            current_depth = current_depth + 1
                            (v, _, _) = self.minimax(current_depth, max=True)
                        if v < value:
                            value = v
                            x = i
                            y = j

                    # Reset cell so that state is not permanently modified by A.I. traversal
                    self.current_state[i][j] = '.'
        return value, x, y

    def alphabeta(self, current_depth=0, alpha=-100, beta=100, max=False):
        """
        A more efficient version of minimax (i.e. includes pruning)

        :param current_depth: required to determine when to stop traversing
        :param alpha: required for pruning
        :param beta: required for pruning
        :param max: boolean to decide which computation will be used (max or min)
        :return: the value of the heuristic being propagated along with the X,Y coordinates of the best computed move
        """

        value = 1
        if max:
            value = -1
        x = None
        y = None

        # Iterate through every possible move (i, j)
        for i in range(0, self.board_size):
            for j in range(0, self.board_size):
                # Update timer
                move_time = time.time() - self.move_start

                # Only consider valid moves (i.e. cells that are empty)
                if self.current_state[i][j] == '.':

                    # If timer is has expired, stop traversing and set the current depth as max depth
                    if not self.timer_is_up and move_time >= self.maxTurnTime :
                        self.max_depth_adjusted = current_depth
                        self.timer_is_up = True

                    # end traversal if resources are spent
                    end_of_traversal = current_depth == self.max_depth_adjusted

                    if max:
                        self.current_state[i][j] = 'O'
                        if end_of_traversal or self.is_end():
                            v = self.e3(current_depth)
                        else:
                            current_depth = current_depth + 1
                            (v, _, _) = self.alphabeta(current_depth, alpha, beta, max=False)
                        if v > value:
                            value = v
                            x = i
                            y = j
                    else:
                        self.current_state[i][j] = 'X'
                        if end_of_traversal or self.is_end():
                            v = self.e3(current_depth)
                        else:
                            current_depth = current_depth + 1
                            (v, _, _) = self.alphabeta(current_depth, alpha, beta, max=True)
                        if v < value:
                            value = v
                            x = i
                            y = j

                    print(str(current_depth) + " " + str(v) + " " + str(max))
                    # Reset cell so that state is not permanently modified by A.I. traversal
                    self.current_state[i][j] = '.'

                    # Prune unnecessary siblings
                    if max: 
                        if value >= beta:
                            return value, x, y
                        if value > alpha:
                            alpha = value
                    else:
                        if value <= alpha:
                            return value, x, y
                        if value < beta:
                            beta = value

        return value, x, y

    def play(self,algo=None,player_x=None,player_o=None):
        if algo is None:
            algo = self.ALPHABETA
        if player_x is None:
            player_x = self.HUMAN
        if player_o is None:
            player_o = self.HUMAN
        while True:
            self.draw_board()
            if self.check_end():
                return
            self.move_start = time.time()
            #signal.signal(signal.SIGALRM, timeoutHandler)
            #signal.alarm(self.maxTurnTime)

            if algo == self.MINIMAX:
                if self.player_turn == 'X':
                    (_, x, y) = self.minimax(max=False)
                else:
                    (_, x, y) = self.minimax(max=True)

            else: # algo == self.ALPHABETA
                if self.player_turn == 'X':
                    (m, x, y) = self.alphabeta(max=False)
                else:
                    (m, x, y) = self.alphabeta(max=True)
                print(m)
            end = time.time()
            if (self.player_turn == 'X' and player_x == self.HUMAN) or (self.player_turn == 'O' and player_o == self.HUMAN):
                    if self.recommend:
                        print(F'Evaluation time: {round(end - self.move_start, 7)}s')
                        print(F'Recommended move: x = {x}, y = {y}')
                    (x,y) = self.input_move()
            if (self.player_turn == 'X' and player_x == self.AI) or (self.player_turn == 'O' and player_o == self.AI):
                        print(F'Evaluation time: {round(end - self.move_start, 7)}s')
                        print(F'Player {self.player_turn} under AI control plays: x = {x}, y = {y}')

            # reset variables
            self.max_depth_adjusted = self.max_depth
            self.timer_is_up = False
            self.current_state[x][y] = self.player_turn
            self.switch_player()

def timeoutHandler():
    raise TimeoutError("Player took too long to move!")

def main():
    g = Game(6, 1, [{'x':0,'y':0}], 4, 12, recommend=True)
    g.play(algo=Game.ALPHABETA,player_x=Game.AI,player_o=Game.AI)
    #g.play(algo=Game.MINIMAX,player_x=Game.AI,player_o=Game.HUMAN)

if __name__ == "__main__":
    main()




