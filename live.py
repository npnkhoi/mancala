"""
Script to play with another human
"""

import sys
from game import Game

OPPONENT = 1

cur = sys.argv[1]
cur = int(cur)
game = Game()
node = 1

while True:
    # Show board
    game.print_board(node)
    
    # Check termination
    status = game.status(node)
    if status[0]:
        print(f'End game. Muggle {status[1]} - Computer {status[2]}. Good game!')
        break
    
    if cur == OPPONENT:
        move = int(input('Muggle\'s move: '))
    else:
        move = 0 # FIXME
    node = game.get_new_node(node, move, cur)