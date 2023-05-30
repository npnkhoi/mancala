"""
Script to play with another human
"""

import sys
from game import Game
from uct import UCTPlayer

OPPONENT = 1

cur = sys.argv[1]
cur = int(cur)
game = Game()
p = UCTPlayer(game, 2, 1000)
uct_node = p.root
game_node = 1

while True:
    # Show board
    game.print_board(game_node)
    
    # Check termination
    status = game.status(game_node)
    if status[0]:
        print(f'End game. SILVER {status[1]} - Muggle {status[2]}. Good game!')
        break
    
    while True:
        try:
            if cur == OPPONENT:
                move = int(input('MUGGLE goes: '))
            else:
                res = p.get_result(uct_node)
                move = res['move']
                print(f'SILVER goes: {move} (util={round(res["utility"], 2)})')
            game_node = game.get_new_node(game_node, move, cur)
            if move not in uct_node.children:
                p._expand(uct_node, move)
            uct_node = uct_node.children[move]
            
            break
        except Exception as e:
            print(e)
        
    cur = 1-cur