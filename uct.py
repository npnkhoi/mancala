"""
Implementation of Upper Confidence bounds applied to Trees (UCT)

Author: Khoi Nguyen
"""
from enum import IntEnum
import random
from typing import Dict
from game import Game
from dataclasses import dataclass
from math import sqrt, log
import sys

class Side(IntEnum):
    MAX = 1
    MIN = -1

# Structure to store a node of the UCT search tree
@dataclass
class UCTNode:
    state: int
    side: Side
    children: Dict[int, dataclass]  # mapping: move -> node
    utility: float = 0.0
    visit_count: int = 0


class UCTPlayer():
    """ Class to play games by UCT algorithm """
    INFINITY = 1e9
    
    def __init__(self, game: Game, bias_constant, num_iterations, random_seed=None):
        self.game = game
        self.root = UCTNode(state=1, side=Side.MAX, children={})
        if num_iterations < self.game.branching_factor:
            raise ValueError("num_iterations must exceeed game's branching factor.")
        self.num_iterations = num_iterations # the number of nodes to expand
        self.bias_constant = bias_constant  # the constant c in UCB1 formula
        self.node_count = 0
        self.latest_expansion = None
        sys.setrecursionlimit(100005) # NOTICE: how much should this be?

    def get_result(self, node: UCTNode):
        """ 
        This function proceeds the iteration for a number of times,
        then returns the best move based on estimated utility.
        This is the main function to communicate with the playing environment.
        """

        self.node_count = 1
        # Repeat the UCT iterations
        for _ in range(self.num_iterations):
            self._uct_recurse(node)

        move = self._select_move(node=node, bias_constant=0)
        return {
            "move": move,
            "utility": node.children[move].utility,
            "node_count": self.node_count,
        }

    def _uct_recurse(self, node: UCTNode) -> int:
        """
        Recursive method to proceed UCT iteration
        """

        # Select the best move to explore
        move = self._select_move(node, self.bias_constant)

        # Recurse or expand
        if move is None:
            # Encounter leaf node, result = heuristic value
            result = self.game.get_eval(node.state)
        elif move in node.children:
            result = self._uct_recurse(node.children[move])
        else:
            result = self._expand(node, move)

        # Backpropagrate
        node.visit_count += 1
        # utility: average of results over all iterations from that node
        # below is slightly different than the original formula, but actually correct
        node.utility += (result - node.utility) / node.visit_count 

        return result
    
    def _break_tie(self, node: UCTNode, moves: list) -> int:
        return random.choice(moves)

    def _select_move(self, node: UCTNode, bias_constant: float) -> int or None:
        """ 
        Return the best child to visit next according to UCB1 algorithm
        """
        state = self.game._game_tree[node.state][0]
        legal_moves = state.legal_moves
        if self.game.status(node.state)[0]:
            return None
        elif len(node.children) == len(legal_moves):
            # All the children are visited.
            best_moves = []
            best_score = -node.side * self.INFINITY
            
            for move in legal_moves:
                child = node.children[move]
                # UCB1 formula
                score = (child.utility + node.side * bias_constant *
                         sqrt(log(node.visit_count) / child.visit_count))
                if ((score > best_score and node.side == Side.MAX) 
                    or (score < best_score and node.side == Side.MIN)):
                    # Better move found
                    best_score = score
                    best_moves = [move]
                elif score == best_score:
                    best_moves.append(move)

            return self._break_tie(node, best_moves)
        else:
            # At least one child is unvisited -- cannot apply UCB1 formula
            # => Choose one random move
            new_moves = []
            for move in legal_moves:
                if move not in node.children:
                    new_moves.append(move)
            return self._break_tie(node, new_moves)

    def _expand(self, node, move):
        """ 
        Context: from a node (as well as a state), 
                 the algorithm tries making a move
        This method expands a new node on UCT tree for that move and return the 
        ultility of the new state
        """

        self.node_count += 1
        new_state = self.game.get_new_node(node.state, move, 0 if node.side == Side.MAX else 1)
        self.latest_expansion = new_state
        result = self.game.get_eval(new_state)

        # Create a new node on UCT tree as a new child of the old node
        node.children[move] = UCTNode(
            state=new_state,
            side=-node.side,
            children={},
            utility=result,
            visit_count=1
        )

        return result