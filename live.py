"""
Script to play with another human
"""

import sys
from game import Game
from uct import UCTPlayer
from util import Side

N_ITER = 10000


first_pers = int(sys.argv[1])
cur = Side.MAX

game = Game(first_view=first_pers)
p = UCTPlayer(game, bias_constant=2, num_iterations=N_ITER)
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
            if cur != first_pers:
                move = int(input('... MUGGLE goes: '))
            else:
                res = p.get_result(uct_node)
                move = res['move']
                print(f'... SILVER goes: {move} (util={round(res["utility"], 2)})')
            
            game_node = game.get_new_node(game_node, move)
            if move not in uct_node.children:
                p._expand(uct_node, move)
            uct_node = uct_node.children[move]
            
            break
        except Exception as e:
            print(e)
            raise e
        
    cur = -cur