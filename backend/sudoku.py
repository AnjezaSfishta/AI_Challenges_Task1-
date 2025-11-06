# sudoku.py
# Vendose këtë file në të njëjtin folder me app.py (backend/).

import random
import time
from copy import deepcopy
from collections import deque
from typing import List, Optional, Tuple


# =========================
#  SudokuSolver (BFS only)
# =========================
class SudokuSolver:
    """
    Zgjidh sudoku me BFS + backtracking (pa heuristika).
    0 = qeliza bosh.
    """

    def __init__(self, grid: List[List[int]]):
        self.grid = grid

    def _is_valid(self, board, r, c, v) -> bool:
        # rreshti
        for j in range(9):
            if board[r][j] == v:
                return False
        # kolona
        for i in range(9):
            if board[i][c] == v:
                return False
        # kuti 3x3
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
        """
        BFS mbi gjendjet. Kthen (ok, solution, stats).
        stats: duration_ms, node_count, timed_out: bool
        """
        start = time.perf_counter()
        q = deque([deepcopy(self.grid)])
        visited = 0

        while q:
            # TIMEOUT / NODES CAP
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

    # Përdoret nga gjeneruesi për numërim zgjidhjesh me BFS (pa DFS).
    def count_solutions_bfs(self, limit: int = 2) -> int:
        """
        Numëron zgjidhjet me BFS, duke ndalur në 'limit'.
        Përdoret për ensure_unique gjatë gjenerimit.
        """
        q = deque([deepcopy(self.grid)])
        solutions = 0
        while q and solutions < limit:
            board = q.popleft()
            r, c = self._find_first_empty(board)
            if r is None:
                solutions += 1
                continue
            for v in range(1, 10):
                # validim i shpejtë
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


# =========================
#  SudokuGenerator
# =========================
class SudokuGenerator:
    """
    Gjeneron puzzle duke nisur nga një zgjidhje bazë e vlefshme,
    pastaj shkund permutime dhe heq qeliza sipas nivelit.
    Nëse ensure_unique=True, verifikon që të ketë <= 1 zgjidhje (me BFS).
    """

    def __init__(self):
        pass

    def _solved_base(self) -> List[List[int]]:
        base = 3
        side = base * base  # 9
        def pattern(r, c): return (base * (r % base) + r // base + c) % side
        rows = [r for r in range(side)]
        cols = [c for c in range(side)]
        nums = [n for n in range(1, side + 1)]
        return [[nums[pattern(r, c)] for c in cols] for r in rows]

    def _shuffle_board(self, board: List[List[int]]) -> List[List[int]]:
        """Shkund në mënyrë të sigurtë numrat, rreshtat/kolonat brenda band/stack dhe vetë band/stack."""
        b = deepcopy(board)

        # 1) Permuto numrat 1..9
        perm = list(range(1, 10))
        random.shuffle(perm)
        mapping = {i + 1: perm[i] for i in range(9)}
        for r in range(9):
            for c in range(9):
                b[r][c] = mapping[b[r][c]]

        # 2) Shuflo rreshtat brenda çdo band-i (0–2, 3–5, 6–8)
        for band in range(0, 9, 3):
            order = [0, 1, 2]
            random.shuffle(order)
            rows = b[band:band + 3]
            b[band:band + 3] = [rows[i] for i in order]

        # 3) Shuflo kolonat brenda çdo stack-u (0–2, 3–5, 6–8)
        for stack in range(0, 9, 3):
            order = [0, 1, 2]
            random.shuffle(order)
            for r in range(9):
                slice3 = b[r][stack:stack + 3]
                b[r][stack:stack + 3] = [slice3[i] for i in order]

        # 4) Shuflo vetë band-et (blloqet e rreshtave 3x3)
        band_order = [0, 1, 2]
        random.shuffle(band_order)
        new_b = []
        for bo in band_order:
            new_b.extend(b[bo * 3: bo * 3 + 3])
        b = new_b

        # 5) Shuflo vetë stack-et (blloqet e kolonave 3x3)
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
        """
        Gjeneron puzzle. Ndalet nëse kalon timeout_sec dhe kthen puzzle-in aktual.
        """
        start = time.perf_counter()

        solved = self._solved_base()
        solved = self._shuffle_board(solved)

        target_clues = self._clue_targets(level)
        puzzle = deepcopy(solved)

        coords = [(r, c) for r in range(9) for c in range(9)]
        random.shuffle(coords)

        checks_done = 0
        for (r, c) in coords:
            # TIMEOUT CHECK
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
