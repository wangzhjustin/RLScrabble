import numpy as np
import utils

class Player():
    def __init__(self):
        super().__init__()
        self.rack = []
        self.score = 0

    def __str__(self):
        return str(self.rack) + '\n' + str(self.score)

    def drawTiles(self, bag, tiles):
        tilesDrawn = 0
        for letter in tiles:
            if letter.islower():
                letter = '?'
            self.rack.remove(letter)
        for i in range(len(tiles)):
            if i < len(bag):
                self.rack.append(bag[i])
                tilesDrawn += 1
        return tilesDrawn

    def rackLetterScores(self):
        return np.array2string(np.vectorize(utils.points.__getitem__)(self.rack), separator=', ')
