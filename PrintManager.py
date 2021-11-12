#!/usr/bin/env python
# coding: utf-8

import sys

class PrintManager(object):

    def __init__(self):
        self.terminal = sys.stdout
        self.log = open('log.log', "w")
   
    def write(self, message):
        self.terminal.write(message)
        self.log.write(message) 

    def setPath(self, path):
        self.log = open(path, "w")

    def flush(self):
        pass    