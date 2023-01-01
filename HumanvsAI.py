import copy
import numpy as np
from Game import Game
import time
import threading
import json
import Simulation as simpy
from colorama import Fore, Back, Style


def main():
    a = Game()
    humanFirst = True
    humanTurn = humanFirst

    while a.numMoves >= 0:
        if humanTurn:
            print('Your rack: ')
            print(a.players[a.currentPlayer].rack)
            print('Letter points: ')
            print(a.players[a.currentPlayer].rackLetterScores())
            print('Your score, opponent\'s score:')
            print(str(a.players[a.currentPlayer].score) + ', ' + str(a.players[not a.currentPlayer].score))
            print('Current board: ')
            a.board.printHumanBoard()
            print(Fore.LIGHTMAGENTA_EX + 'Triple Word ', end='')
            print(Fore.RED + 'Double Word ', end='')
            print(Fore.BLUE + 'Triple Letter ', end='')
            print(Fore.GREEN + 'Double Letter' + Fore.WHITE)
            print('USAGE: <row> <col> <across/down> <word>, if no legal moves, type \'pass\'')
            print('EX: 3 4 across NIcE')
            userInput = input('Your move: ')
            if userInput == 'pass':
                a.currentPlayer = not a.currentPlayer
                opponentNoMove = True 
            else:
                moves = a.humanMove(userInput)
                opponentNoMove = False
                a.playBestMove(moves)
                print(a.board)

        else:
            print('Player ' + str(a.currentPlayer + 1) + ' rack:')
            print(a.players[a.currentPlayer].rack)
            print('Player ' + str(a.currentPlayer + 1) + ': ')
            moves = a.find_best_moves(a.players[a.currentPlayer].rack, num=1)
           
            if len(moves) == 0 or moves[0] == None:
                print('no possible move')
                if opponentNoMove:
                    a.endGame()
                    print('racks:')
                    print(a.players[0].rack)
                    print(a.players[1].rack)
                    a.numMoves = -1
                    continue
                a.currentPlayer = not a.currentPlayer
                opponentNoMove = True
            else:
                print(moves[0][0])
                opponentNoMove = False
                a.playBestMove(moves)
                print('Bag size: ' + str(len(a.bag)))
                print(a.board)

        humanTurn = not humanTurn



    return

if __name__ == '__main__':
    main()