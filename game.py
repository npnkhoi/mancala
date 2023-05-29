"""
Move encoding:
    x in [0; 9]
    x div 2: the cell
    x mod 2: the direction
Board class: (as a dict?)
    number of pieces in each of 10 cells
    number of pieces in 2 big cells
    2 flags of whether each big cell has the big piece
"""
from copy import deepcopy
from typing import Dict, List


INITIAL_PIECES = 5
ROW_LEN = 6 # including the big cell
NUM_CELLS = ROW_LEN * 2
BIG_VALUE = 10

class State:
    def __init__(self) -> None:
        """
        Max side is 0, min size is 1
        """
        self.cell = [
            [0, INITIAL_PIECES, INITIAL_PIECES, INITIAL_PIECES, INITIAL_PIECES, INITIAL_PIECES,
            0, INITIAL_PIECES, INITIAL_PIECES, INITIAL_PIECES, INITIAL_PIECES, INITIAL_PIECES]
        ]
        self.has_big = [True, True]
        self.score = [0, 0]
    
    def is_terminal(self):
         # TODO: what if each side still have pieces?
        return self.cell[0] == 0 and self.cell[ROW_LEN] == 0 and sum(self.has_big) == 0
    
    def _next_cell(self, cell, dir):
        cell += dir
        if cell < 0:
            cell += NUM_CELLS
        if cell >= NUM_CELLS:
            cell -= NUM_CELLS
        return cell

    def _is_big_cell(self, pos):
        return pos == 0 or pos == ROW_LEN

    def get_next_state(self, move, side) -> State:
        """
        Scattering scenarios: ???
        """
        ret: State = deepcopy(self)
        pos = move // 2
        drt = move % 2
        while not self._is_big_cell(pos) and ret.cell[pos] != 0:
            # start spreading
            tmp = ret.cell[pos]
            ret.cell = 0
            for _ in range(tmp):
                pos = self._next_cell(pos, drt)
                ret.cell[pos] += 1
            pos = self._next_cell(pos, drt)
        
        # gaining?
        next_pos = self._next_cell(pos, drt)
        while ret.cell[pos] == 0 and ret.cell[self._next_cell(pos, drt)] != 0:
            ret.score[side] += ret.cell[next_pos]
            if self._is_big_cell(next_pos):
                big_id = 0 if next_pos == 0 else 1
                ret.score[side] += BIG_VALUE * ret.has_big[big_id]
                ret.has_big[big_id] = False
            pos = self._next_cell(next_pos, drt)
        
        # FIXME: case of borrowing?
        
        return ret
    
    def score_diff(self):
        return self.score[0] - self.score[1]
        
        

class Game:
    def __init__(self) -> None:
        self._game_tree: Dict[int, List[State, list]] = { # node -> state
            1: [State(), []]
        }
    
    def get_new_node(self, node: int, move, side):
        """
        Returns: the new node ID
        Effect: create the new node record in the game_tree, add to old node's children
        """
        state = self._game_tree[node]
        if state.is_terminal:
            raise ValueError('Cannot go from a terminal node')
        new_node = len(self._game_tree) + 1
        self._game_tree[new_node] = state.get_next_state(move, side)
        self._game_tree[node][1].append(new_node)
        
        return new_node

    def _get_state(self, node):
        return self._game_tree[node][0]

    def status(self, node):
        state = self._get_state(node)
        return (
            state.is_terminal(),
            state.score[0],
            state.score[1],
        )
    
    def print_board(self, node):
        state = self._get_state(node)
        print('Cells')
        for offset in [ROW_LEN, 0]:
            for i in range(ROW_LEN):
                print(str(state.cell[offset + i]).rjust(4), end=' ')
        print('Big states:', state.has_big)
        print('Scores:', state.score)