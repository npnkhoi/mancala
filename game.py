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
BIG_VALUE = 5

class State:
    def __init__(self) -> None:
        """
        Max side is +1, min size is -1
        """
        self.cell = [
            BIG_VALUE, INITIAL_PIECES, INITIAL_PIECES, INITIAL_PIECES, INITIAL_PIECES, INITIAL_PIECES,
            BIG_VALUE, INITIAL_PIECES, INITIAL_PIECES, INITIAL_PIECES, INITIAL_PIECES, INITIAL_PIECES
        ]
        self.score = [0, 0]
        self.legal_moves = list(range(10))
    
    def is_terminal(self):
         # TODO: what if each side still have pieces?
        return self.cell[0] + self.cell[ROW_LEN] == 0
    
    def _next_cell(self, cell, dir):
        cell += -1 if dir == 0 else 1
        if cell < 0:
            cell += NUM_CELLS
        if cell >= NUM_CELLS:
            cell -= NUM_CELLS
        return cell

    def _is_big_cell(self, pos):
        return pos == 0 or pos == ROW_LEN

    def get_next_state(self, move, side):
        """
        Returns: (State)
        Scattering scenarios: ???
        """
        ret: State = deepcopy(self)
        pos, drt = self._get_pos_drt(move, side)
        if ret.cell[pos] == 0:
            raise ValueError('Must not start from an empty cell')
        if self._is_big_cell(pos):
            raise ValueError('Must not start at the big cell')
        while not self._is_big_cell(pos) and ret.cell[pos] != 0:
            # start spreading
            tmp = ret.cell[pos]
            ret.cell[pos] = 0
            for _ in range(tmp):
                pos = self._next_cell(pos, drt)
                ret.cell[pos] += 1
            pos = self._next_cell(pos, drt)
        
        # gaining?
        next_pos = self._next_cell(pos, drt)
        while ret.cell[pos] == 0 and ret.cell[next_pos] != 0:
            ret.score[side] += ret.cell[next_pos]
            ret.cell[next_pos] = 0
            pos = self._next_cell(next_pos, drt)
            next_pos = self._next_cell(pos, drt)
        
        if ret.is_terminal():
            # end game, distribute stuffs
            for i in range(ROW_LEN-1):
                for side in [0, 1]:
                    pos = ROW_LEN * side + i + 1
                    ret.score[side] += ret.cell[pos]
                    ret.cell[pos] = 0
        else:
            # case of borrowing
            flag, new_side = False, 1-side
            for i in range(ROW_LEN-1):
                pos, _ = self._get_pos_drt(i*2, new_side)
                if ret.cell[pos] != 0:
                    flag = True
                    break
            if not flag: # no pieces left to play => borrow
                ret.score[side] -= 5
                for i in range(ROW_LEN-1):
                    pos, _ = self._get_pos_drt(i*2, new_side)
                    ret.cell[pos] = 1
        
        
        # change legal moves
        ret.legal_moves = [move for move in range(10) if ret._is_legal_move(move, 1-side)]
        
        return ret
    
    def score_diff(self):
        return self.score[0] - self.score[1]

    def _get_pos_drt(self, move, side):
        pos = move // 2 + side * ROW_LEN + 1 # plus one due to the big cell on the left
        drt = move % 2
        return (pos, drt)
        

    def _is_legal_move(self, move, side):
        pos, _ = self._get_pos_drt(move, side)
        return self.cell[pos] != 0 and not self._is_big_cell(pos)
        

class Game:
    def __init__(self) -> None:
        self._game_tree: Dict[int, List[State, list]] = { # node -> state
            1: [State(), []]
        }
        self.branching_factor = ROW_LEN*2-2
    
    def get_new_node(self, node: int, move, side):
        """
        Returns: the new node ID
        Effect: create the new node record in the game_tree, add to old node's children
        """
        state = self._game_tree[node][0]
        if state.is_terminal():
            raise ValueError('Cannot go from a terminal node')
        new_node = len(self._game_tree) + 1
        self._game_tree[new_node] = [state.get_next_state(move, side), []]
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
        print('Scores:', state.score)
        print('-'*(7*7))
        print(' '.rjust(7), end='')
        for i in range(ROW_LEN-2, -1, -1):
            print(f'({i*2+1}-{i*2}) '.rjust(7), end='')
        print()
        print('|'.rjust(7), end='')
        for i in range(ROW_LEN-1, -1, -1):
            print(f'{state.cell[ROW_LEN + i]} |'.rjust(7), end='')
        print()
        for i in range(ROW_LEN):
            print(f'{state.cell[i]} |'.rjust(7), end='')
        print()
        print(' '.rjust(7), end='')
        for i in range(0, ROW_LEN-1):
            print(f'({i*2}-{i*2+1}) '.rjust(7), end='')
        print('\n' + '-'*(7*7))
    
    def get_eval(self, node):
        state = self._get_state(node)
        max_score = 60 # 2*5 + 5*10
        return (state.score[0] - state.score[1]) / (2 * max_score) + 0.5