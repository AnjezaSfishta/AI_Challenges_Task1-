import random
from collections import deque
import copy

class SudokuSolver:
    def __init__(self, board):

        self.board = board
        self.size = 9


    @staticmethod
    def _copy(board):
        return [row[:] for row in board]

    def is_valid_board(self, board):

        for i in range(9):
            row_vals = [v for v in board[i] if v != 0]
            if len(row_vals) != len(set(row_vals)):
                return False
            col_vals = [board[r][i] for r in range(9) if board[r][i] != 0]
            if len(col_vals) != len(set(col_vals)):
                return False

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


    def solve_one_dfs(self, board):
        empty = self.find_empty(board)
        if not empty:
            return True
        i, j = empty
        for v in range(1, 10):
            if self.is_valid(board, i, j, v):
                board[i][j] = v
                if self.solve_one_dfs(board):
                    return True
                board[i][j] = 0
        return False


    def count_solutions(self, board, limit=2):
        empty = self.find_empty(board)
        if not empty:
            return 1
        i, j = empty
        count = 0
        for v in range(1, 10):
            if self.is_valid(board, i, j, v):
                board[i][j] = v
                count += self.count_solutions(board, limit)
                board[i][j] = 0
                if count >= limit:
                    break
        return count


    def classify_puzzle(self, board, limit=2):

        if not self.is_valid_board(board):
            return {"status": "invalid", "solution": None}

        b_for_count = self._copy(board)
        cnt = self.count_solutions(b_for_count, limit=limit)

        if cnt == 0:
            return {"status": "unsolvable", "solution": None}
        elif cnt == 1:
            b_solution = self._copy(board)
            self.solve_one_dfs(b_solution)
            return {"status": "unique", "solution": b_solution}
        else:
            b_solution = self._copy(board)
            self.solve_one_dfs(b_solution)
            return {"status": "multiple", "solution": b_solution}

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

    def generate_sudoku(self, level="easy", ensure_unique=False, max_checks=50):

        tries = 0
        while True:
            full_board = self.generate_full_board()
            puzzle = self.remove_cells(full_board, level)
            if not ensure_unique:
                return puzzle
            solver = SudokuSolver(puzzle)
            klass = solver.classify_puzzle(puzzle, limit=2)
            if klass["status"] == "unique":
                return puzzle
            tries += 1
            if tries >= max_checks:
                return puzzle
