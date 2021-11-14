#!/usr/bin/env python
# coding: utf-8

import sys

class PrintManager(object):
    """
    Utility class so that system's prints are outputted to both the console and a designated filepath
    """

    def __init__(self):
        self.terminal = sys.stdout
        self.log = open('log.log', "w")
   
    def write(self, message):
        self.terminal.write(message)
        self.log.write(message) 

    """ Custom method to update the path of the file being written to """
    def setPath(self, path):
        self.log.close()
        self.log = open(path, "w")

    def flush(self):
        pass    