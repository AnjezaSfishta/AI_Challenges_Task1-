import random
from collections import deque
import copy

class SudokuSolver:
    def __init__(self, board):
        """
        board: list[list[int]] 9x9; 0 for blanks
        """
        self.board = board
        self.size = 9

    def is_valid_board(self, board):
        # rows and cols
        for i in range(9):
            row_vals = [v for v in board[i] if v != 0]
            if len(row_vals) != len(set(row_vals)):
                return False
            col_vals = [board[r][i] for r in range(9) if board[r][i] != 0]
            if len(col_vals) != len(set(col_vals)):
                return False
        # 3x3 blocks
        for br in range(0, 9, 3):
            for bc in range(0, 9, 3):
                vals = []
                for r in range(br, br + 3):
                    for c in range(bc, bc + 3):
                        if board[r][c] != 0:
                            vals.append(board[r][c])
                if len(vals) != len(set(vals)):
                    return False
        return True

    def is_valid(self, board, row, col, num):
        if num in board[row]:
            return False
        for i in range(9):
            if board[i][col] == num:
                return False
        sr, sc = 3 * (row // 3), 3 * (col // 3)
        for i in range(sr, sr + 3):
            for j in range(sc, sc + 3):
                if board[i][j] == num:
                    return False
        return True

    def find_empty(self, board):
        for i in range(9):
            for j in range(9):
                if board[i][j] == 0:
                    return i, j
        return None

    def solve_bfs_backtracking(self, max_states=200000):
        if not self.is_valid_board(self.board):
            return False, None
        queue = deque([copy.deepcopy(self.board)])
        states = 0
        while queue:
            current_board = queue.popleft()
            states += 1
            if states > max_states:
                return False, None
            empty_pos = self.find_empty(current_board)
            if not empty_pos:
                self.board = current_board
                return True, current_board
            row, col = empty_pos
            for num in range(1, 10):
                if self.is_valid(current_board, row, col, num):
                    new_board = copy.deepcopy(current_board)
                    new_board[row][col] = num
                    queue.append(new_board)
        return False, None

    @staticmethod
    def format_board(board):
        return board

class SudokuGenerator:
    def __init__(self):
        self.base = 3
        self.side = self.base * self.base

    def pattern(self, r, c):
        return (self.base * (r % self.base) + r // self.base + c) % self.side

    def shuffle(self, s):
        return random.sample(list(s), len(list(s)))

    def generate_full_board(self):
        r_base = range(self.base)
        rows = [g * self.base + r for g in self.shuffle(r_base) for r in self.shuffle(r_base)]
        cols = [g * self.base + c for g in self.shuffle(r_base) for c in self.shuffle(r_base)]
        nums = self.shuffle(range(1, self.side + 1))
        board = [[nums[self.pattern(r, c)] for c in cols] for r in rows]
        return board

    def remove_cells(self, board, level="easy"):
        if level == "easy":
            empties = 30
        elif level == "medium":
            empties = 45
        else:
            empties = 60

        new_board = [row[:] for row in board]
        removed, attempts = 0, 0
        while removed < empties and attempts < empties * 10:
            row = random.randrange(9)
            col = random.randrange(9)
            if new_board[row][col] != 0:
                new_board[row][col] = 0
                removed += 1
            attempts += 1
        return new_board

    def generate_sudoku(self, level="easy"):
        full_board = self.generate_full_board()
        puzzle = self.remove_cells(full_board, level)
        return puzzle