#!/usr/bin/env python
# coding: utf-8

from ScoreBoard import ScoreBoard
def main():

    sboard = ScoreBoard(1)
    sboard.calculateScore()
    sboard.printAverageEndOfAllGames()

if __name__ == "__main__":
    main()