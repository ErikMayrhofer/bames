import argparse
import sys

class Barameters:
    fullscreen: bool

    def __init__(self):
        parser = argparse.ArgumentParser(description='BAME! (von den Machern von Bame)') 
        parser.add_argument('--fullscreen', dest="fullscreen", action='store_true')
        self.args = parser.parse_args()
        self.fullscreen = self.args.fullscreen

if __name__ == "__main__":
    barameters = Barameters()
