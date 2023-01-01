import copy
import numpy as np
from Game import Game
import time
import threading
import json

def find_best_move_lookahead(game, score=0, k=1, protagonist=1):
    '''
    returns:
        move:      the optimal move according to k-ply lookahead
        score:     the difference in score between players (protagonist_score - antagonist_score)
    '''

    if k == 0:
        # make the this player fill entirely random rack 'numDraws' times, 
        # make the best moves, and return average score
        avg_score = 0
        numDraws = 10
        count = 0
        for i in range(numDraws):
        # make the next player fill entirely random rack
            game.exchangeSeven(game.currentPlayer)
            moves = game.find_best_moves(game.players[game.currentPlayer].rack, num=1)
            if len(moves) == 0:
                continue
            else:
                avg_score += moves[0][1]
                count += 1

        if count > 0:
            avg_score = avg_score / count

        if protagonist:
            score += avg_score
        else:
            score -= avg_score

        return [], score

    if k == 99:
        avg_score = 0
        moves = game.find_best_moves(game.players[game.currentPlayer].rack, num=1)
        if len(moves) >= 1:
            avg_score += moves[0][1]
        if protagonist:
            score += avg_score
        else:
            score -= avg_score
        return [], score


    # find the best move according to lookahead
    branchingFactor = 5 # how many moves to analyze
    moves = game.find_best_moves(game.players[game.currentPlayer].rack, num=branchingFactor)
    bestMove = None
    bestScore = -np.inf
    for nextMove in moves:
        inputScore = score
        if protagonist:
            inputScore += nextMove[1]
        else:
            inputScore -= nextMove[1]

        # memorize the state here
        tempBag = copy.deepcopy(game.bag)
        tempBoard = copy.deepcopy(game.board)
        tempPlayers = copy.deepcopy(game.players)
        tempCurrentPlayer = copy.deepcopy(game.currentPlayer)
        tempNumMoves = copy.deepcopy(game.numMoves)

        game.playBestMove(list([nextMove, nextMove]))

        _, tempScore = find_best_move_lookahead(game, inputScore, k-1, not protagonist)
        
        game.bag = tempBag
        game.board = tempBoard
        game.players = tempPlayers
        game.currentPlayer = tempCurrentPlayer
        game.numMoves = tempNumMoves
        
        if tempScore > bestScore:
            bestScore = tempScore
            bestMove = nextMove

    return bestMove, bestScore


def saveExample(state, lock):
    lock.acquire()
    with open('examples.json', 'r') as f:
        config = json.load(f)
    if len(config["examples"]) == 0:
        config["examples"] = [state]
    else:
        config["examples"].append(state)
    with open('examples.json','w') as f:
        json.dump(config, f)
    lock.release()

def multiplierToNumber(ml):
    if ml == None:
        return 0
    if ml == "DL":
        return 1
    if ml == "TL":
        return 2
    if ml == "DW":
        return 3
    if ml == "TW":
        return 4

def mapBoardToState(game, leave):
    state = {}
    bag = [0] * 27
    rack = [0] * 27
    for letter in game.bag:
        if letter == '?':
            bag[0] += 1
        else:
            bag[ord(letter) - 64] += 1
    for letter in game.players[game.currentPlayer].rack:
        if letter == '?':
            bag[0] += 1
        else:
            bag[ord(letter) - 64] += 1
    state['bag'] = bag
    for letter in leave:
        if letter == '?':
            rack[0] += 1
        else:
            rack[ord(letter) - 64] += 1
    state['rack'] = rack
    state['score'] = [game.players[not game.currentPlayer].score, game.players[not game.currentPlayer].score - game.players[game.currentPlayer].score]
    board = [[[0,0] for i in range(15)] for j in range(15)]
    for i in range(len(game.board.board)):
        for j in range(len(game.board.board)):
            board[i][j][0] = 0 if game.board.board[i][j].letter == None else ord(game.board.board[i][j].letter.upper()) - 64
            board[i][j][1] = multiplierToNumber(game.board.board[i][j].multiplier)
    state['board'] = board
    return state

def thread_func(move, game, ply, lock):
    lettersUsed = game.board.get_letters_used(move[2], move[0], move[3])
    lettersLeft = game.players[game.currentPlayer].rack[:]
    for letter in game.players[game.currentPlayer].rack:
        if letter.islower() and "?" in game.players[game.currentPlayer].rack:
            lettersLeft.remove("?")
        elif letter in lettersUsed:
            lettersLeft.remove(letter)
    print(lettersLeft, move[0])
    for _ in range(10):
        temp_board = copy.deepcopy(game.board)
        temp_players = copy.deepcopy(game.players)
        temp_game = copy.copy(game)
        temp_game.players = temp_players
        temp_game.board = temp_board
        temp_game.exchangeSeven(not temp_game.currentPlayer)
        temp_game.players[temp_game.currentPlayer].score += move[1]
        temp_game.play(move[2], move[0], move[3])
        state = mapBoardToState(temp_game, lettersLeft)
        temp_game.playBestMove()
        for __ in range(ply - 1):
            temp_game.playBestMove()
            temp_game.playBestMove()
        diff = temp_game.players[temp_game.currentPlayer].score - temp_game.players[not temp_game.currentPlayer].score
        state['scoreDifferentialAfterXPly'] = diff
        saveExample(state, lock)

def simulate(game, ply=2):
    lock = threading.Lock()
    print('Player ' + str(game.currentPlayer+1) + ': ')
    moves = game.find_best_moves(game.players[game.currentPlayer].rack)
    threads = []
    for move in moves:
        threads.append(threading.Thread(target=thread_func, args=(move, game, ply, lock,)))
    for th in threads:
        th.start()
    for th in threads:
        th.join()

def main():
    bagNum = 0 # 0 to 100
    kply = 1 # 1 or 2
    greedyPlayer = 0 # 0 or 1
    player1Wins = 0
    player2Wins = 0
    player1Score = 0
    player2Score = 0
    count = 0
    a = Game()
    while count < 50: # number of sims to run
        a.clear()
        opponentNoMove = False
        while a.numMoves >= 0:
            print('Player ' + str(a.currentPlayer + 1) + ' rack:')
            print(a.players[a.currentPlayer].rack)
            print('Player ' + str(a.currentPlayer + 1) + ': ')
            if a.currentPlayer == greedyPlayer or len(a.bag) >= bagNum:
                moves = a.find_best_moves(a.players[a.currentPlayer].rack, num=1)
            else:
                # memorize the current state
                tempBag = copy.deepcopy(a.bag)
                tempBoard = copy.deepcopy(a.board)
                tempPlayers = copy.deepcopy(a.players)
                tempCurrentPlayer = copy.deepcopy(a.currentPlayer)
                tempNumMoves = copy.deepcopy(a.numMoves)

                # make sure we don't know the opponent's real rack
                a.exchangeSeven(not a.currentPlayer)

                moves = find_best_move_lookahead(a, k=kply)

                a.bag = tempBag 
                a.board = tempBoard
                a.players = tempPlayers
                a.currentPlayer = tempCurrentPlayer
                a.numMoves = tempNumMoves
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
                # print(a.board)

        if a.players[0].score > a.players[1].score:
            player1Wins += 1
        else:
            player2Wins += 1
        print('Player 1 wins: ' + str(player1Wins))
        print('Player 2 wins: ' + str(player2Wins))
        player1Score += a.players[0].score
        player2Score += a.players[1].score
        count += 1
    print('Player 1 avg score: ' + str(player1Score / count))
    print('Player 2 avg score: ' + str(player2Score / count))



if __name__ == '__main__':
    main()