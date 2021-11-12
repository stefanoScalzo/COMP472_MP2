#!/usr/bin/env python
# coding: utf-8

from ScoreBoard import ScoreBoard
import sys

def main():
    sys.stdout = open("./output.txt", "w")
    sboard = ScoreBoard(1)
    sboard.calculateScore()
    sboard.printAverageEndOfAllGames()

if __name__ == "__main__":
    main()