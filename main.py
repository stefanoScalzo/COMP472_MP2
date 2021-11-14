#!/usr/bin/env python
# coding: utf-8

import json
from ScoreBoard import ScoreBoard


def main():
    config_file = open('./configurations.json')
    configs = json.load(config_file)
    sboard = ScoreBoard(5)
    for i, config in enumerate(configs):
        sboard.calculateScore(config)
        sboard.printAverageEndOfAllGames(i)


if __name__ == "__main__":
    main()
