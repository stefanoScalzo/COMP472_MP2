#!/usr/bin/env python
# coding: utf-8

from ScoreBoard import ScoreBoard
from PrintManager import PrintManager
import sys

def main():
    sys.stdout = PrintManager()
    sboard = ScoreBoard(1)
    sboard.calculateScore()
    sboard.printAverageEndOfAllGames()

if __name__ == "__main__":
    main()