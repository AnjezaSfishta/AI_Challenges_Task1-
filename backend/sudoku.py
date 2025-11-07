
import random
import time
from copy import deepcopy
from collections import deque
from typing import List, Optional, Tuple



class SudokuSolver:

    def __init__(self, grid: List[List[int]]):
        self.grid = grid

    def _is_valid(self, board, r, c, v) -> bool:

        for j in range(9):
            if board[r][j] == v:
                return False

        for i in range(9):
            if board[i][c] == v:
                return False

        br, bc = (r // 3) * 3, (c // 3) * 3
        for i in range(br, br + 3):
            for j in range(bc, bc + 3):
                if board[i][j] == v:
                    return False
        return True

    def _find_first_empty(self, board) -> Tuple[Optional[int], Optional[int]]:
        for r in range(9):
            for c in range(9):
                if board[r][c] == 0:
                    return r, c
        return None, None

    def solve_bfs_backtracking(
        self,
        max_time_sec: Optional[float] = None,
        max_nodes: Optional[int] = None
    ):

        start = time.perf_counter()
        q = deque([deepcopy(self.grid)])
        visited = 0

        while q:
            if max_time_sec is not None and (time.perf_counter() - start) >= max_time_sec:
                dur_ms = (time.perf_counter() - start) * 1000.0
                return False, None, {"duration_ms": round(dur_ms, 3), "node_count": visited, "timed_out": True}
            if max_nodes is not None and visited >= max_nodes:
                dur_ms = (time.perf_counter() - start) * 1000.0
                return False, None, {"duration_ms": round(dur_ms, 3), "node_count": visited, "timed_out": True}

            board = q.popleft()
            visited += 1

            r, c = self._find_first_empty(board)
            if r is None:
                dur_ms = (time.perf_counter() - start) * 1000.0
                return True, board, {"duration_ms": round(dur_ms, 3), "node_count": visited, "timed_out": False}

            for v in range(1, 10):
                if self._is_valid(board, r, c, v):
                    nb = deepcopy(board)
                    nb[r][c] = v
                    q.append(nb)

        dur_ms = (time.perf_counter() - start) * 1000.0
        return False, None, {"duration_ms": round(dur_ms, 3), "node_count": visited, "timed_out": False}


    def count_solutions_bfs(self, limit: int = 2) -> int:

        q = deque([deepcopy(self.grid)])
        solutions = 0
        while q and solutions < limit:
            board = q.popleft()
            r, c = self._find_first_empty(board)
            if r is None:
                solutions += 1
                continue
            for v in range(1, 10):
                valid = True
                for j in range(9):
                    if board[r][j] == v:
                        valid = False
                        break
                if not valid:
                    continue
                for i in range(9):
                    if board[i][c] == v:
                        valid = False
                        break
                if not valid:
                    continue
                br, bc = (r // 3) * 3, (c // 3) * 3
                for i in range(br, br + 3):
                    for j in range(bc, bc + 3):
                        if board[i][j] == v:
                            valid = False
                            break
                    if not valid:
                        break
                if not valid:
                    continue

                nb = deepcopy(board)
                nb[r][c] = v
                q.append(nb)

        return solutions



class SudokuGenerator:

    def __init__(self):
        pass

    def _solved_base(self) -> List[List[int]]:
        base = 3
        side = base * base  
        def pattern(r, c): return (base * (r % base) + r // base + c) % side
        rows = [r for r in range(side)]
        cols = [c for c in range(side)]
        nums = [n for n in range(1, side + 1)]
        return [[nums[pattern(r, c)] for c in cols] for r in rows]

    def _shuffle_board(self, board: List[List[int]]) -> List[List[int]]:
        b = deepcopy(board)

        perm = list(range(1, 10))
        random.shuffle(perm)
        mapping = {i + 1: perm[i] for i in range(9)}
        for r in range(9):
            for c in range(9):
                b[r][c] = mapping[b[r][c]]

        for band in range(0, 9, 3):
            order = [0, 1, 2]
            random.shuffle(order)
            rows = b[band:band + 3]
            b[band:band + 3] = [rows[i] for i in order]


        for stack in range(0, 9, 3):
            order = [0, 1, 2]
            random.shuffle(order)
            for r in range(9):
                slice3 = b[r][stack:stack + 3]
                b[r][stack:stack + 3] = [slice3[i] for i in order]


        band_order = [0, 1, 2]
        random.shuffle(band_order)
        new_b = []
        for bo in band_order:
            new_b.extend(b[bo * 3: bo * 3 + 3])
        b = new_b


        stack_order = [0, 1, 2]
        random.shuffle(stack_order)
        for r in range(9):
            stacks = [b[r][0:3], b[r][3:6], b[r][6:9]]
            b[r] = stacks[stack_order[0]] + stacks[stack_order[1]] + stacks[stack_order[2]]

        return b

    def _clue_targets(self, level: str) -> int:
        level = (level or "easy").lower()
        if level == "easy":
            return 40
        if level == "medium":
            return 32
        if level == "hard":
            return 26
        return 40

    def _count_filled(self, board) -> int:
        return sum(1 for r in range(9) for c in range(9) if board[r][c] != 0)

    def _try_remove_cell(self, board, r, c) -> int:
        old = board[r][c]
        board[r][c] = 0
        return old

    def _unique_check_bfs(self, puzzle: List[List[int]], limit=2) -> int:
        solver = SudokuSolver(puzzle)
        return solver.count_solutions_bfs(limit=limit)

    def generate_sudoku(
        self,
        level: str = "easy",
        ensure_unique: bool = False,
        max_checks: int = 50,
        timeout_sec: Optional[float] = None
    ) -> List[List[int]]:

        start = time.perf_counter()

        solved = self._solved_base()
        solved = self._shuffle_board(solved)

        target_clues = self._clue_targets(level)
        puzzle = deepcopy(solved)

        coords = [(r, c) for r in range(9) for c in range(9)]
        random.shuffle(coords)

        checks_done = 0
        for (r, c) in coords:

            if timeout_sec is not None and (time.perf_counter() - start) >= timeout_sec:
                break

            if self._count_filled(puzzle) <= target_clues:
                break
            if puzzle[r][c] == 0:
                continue

            old = self._try_remove_cell(puzzle, r, c)
            if ensure_unique:
                if checks_done < max_checks:
                    checks_done += 1
                    cnt = self._unique_check_bfs(puzzle, limit=2)
                    if cnt != 1:
                        puzzle[r][c] = old
        return puzzle
