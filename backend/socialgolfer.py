import itertools
from typing import List, Tuple, Set, Optional, Dict, Iterable

# Global state (imported by Flask)
stop_flag = False
current_progress: List[List[List[int]]] = []


# ==========================================================
# Control functions (called from Flask)
# ==========================================================

def set_stop_flag(value: bool):
    global stop_flag
    stop_flag = value


def get_progress():
    global current_progress
    return current_progress


# ==========================================================
# Utilities
# ==========================================================

def calculate_max_theoretical_weeks(n: int, p: int) -> int:
    """Upper bound on weeks for Social Golfers: floor((n - 1) / (p - 1))."""
    if p <= 1:
        return 0
    return (n - 1) // (p - 1)


def pairs_of(group: Tuple[int, ...]) -> Set[Tuple[int, int]]:
    """All unordered pairs from a tuple group of players (sorted pairs)."""
    return {tuple(sorted(x)) for x in itertools.combinations(group, 2)}


def canonical_week(week: List[Tuple[int, ...]]) -> List[Tuple[int, ...]]:
    """Normalize week representation by sorting members and groups."""
    return sorted([tuple(sorted(g)) for g in week])


# ==========================================================
# Lazy Week Construction (Backtracking)
# ==========================================================

def _iter_one_week(players: List[int],
                   group_size: int,
                   used_pairs_global: Set[Tuple[int, int]]) -> Iterable[List[Tuple[int, ...]]]:
    """Generate valid 'weeks' lazily."""
    players = sorted(players)
    groups_needed = len(players) // group_size

    def rec(week_so_far: List[Tuple[int, ...]],
            week_pairs: Set[Tuple[int, int]],
            last_anchor: int):
        if len(week_so_far) == groups_needed:
            yield canonical_week(week_so_far.copy())
            return

        used_players = {p for g in week_so_far for p in g}
        remaining = [x for x in players if x not in used_players]

        for i, anchor in enumerate(remaining):
            if anchor <= last_anchor:
                continue
            pool = remaining[i + 1:]
            for mates in itertools.combinations(pool, group_size - 1):
                group = tuple(sorted((anchor, *mates)))
                ps = pairs_of(group)
                if ps & used_pairs_global or ps & week_pairs:
                    continue

                week_so_far.append(group)
                for pp in ps:
                    week_pairs.add(pp)

                yield from rec(week_so_far, week_pairs, anchor)

                week_so_far.pop()
                for pp in ps:
                    week_pairs.discard(pp)

    yield from rec([], set(), -1)


# ==========================================================
# DFS / DLS Core with Stop & Progress Tracking
# ==========================================================

def _search_weeks(num_players: int,
                  group_size: int,
                  target_weeks: int) -> List[List[List[int]]]:
    """Backtracking search with stop & progress tracking."""

    global stop_flag, current_progress

    all_players = list(range(1, num_players + 1))
    groups_per_week = num_players // group_size
    pairs_per_group = (group_size * (group_size - 1)) // 2
    pairs_per_week = groups_per_week * pairs_per_group
    total_pairs = (num_players * (num_players - 1)) // 2

    best_so_far: List[List[Tuple[int, ...]]] = []
    seen_depth: Dict[frozenset, int] = {}
    dead_state: Set[frozenset] = set()

    def admissible_can_reach(depth_now: int, used_pairs_count: int) -> bool:
        remaining_pairs = total_pairs - used_pairs_count
        max_additional_weeks = remaining_pairs // pairs_per_week
        return (depth_now + max_additional_weeks) >= target_weeks

    def forward_check(used_pairs_map: Set[Tuple[int, int]], depth_now: int) -> bool:
        adj: Dict[int, Set[int]] = {i: set() for i in all_players}
        for a, b in used_pairs_map:
            adj[a].add(b)
            adj[b].add(a)

        remaining_weeks = target_weeks - (depth_now + 1)
        if remaining_weeks <= 0:
            return True
        need = remaining_weeks * (group_size - 1)
        for pl in all_players:
            unseen = (num_players - 1) - len(adj[pl])
            if unseen < need:
                return False
        return True

    def dfs_build(schedule: List[List[Tuple[int, ...]]],
                  used_pairs: Set[Tuple[int, int]]):
        global stop_flag, current_progress

        if stop_flag:
            current_progress = [[list(g) for g in w] for w in schedule]
            return

        depth_now = len(schedule)

        if depth_now >= target_weeks:
            best_so_far[:] = [wk.copy() for wk in schedule]
            current_progress = [[list(g) for g in w] for w in schedule]
            return

        if not admissible_can_reach(depth_now, len(used_pairs)):
            return
        if not forward_check(used_pairs, depth_now):
            return

        key = frozenset(used_pairs)
        prev_depth = seen_depth.get(key, -1)
        if prev_depth >= depth_now:
            return
        seen_depth[key] = depth_now

        if key in dead_state:
            return

        for next_week in _iter_one_week(all_players, group_size, used_pairs):
            if stop_flag:
                current_progress = [[list(g) for g in w] for w in schedule]
                return

            new_pairs_this_week = set().union(*(pairs_of(g) for g in next_week))
            schedule.append(next_week)
            used_before = used_pairs
            used_pairs = used_pairs | new_pairs_this_week

            current_progress = [[list(g) for g in w] for w in schedule]

            dfs_build(schedule, used_pairs)

            schedule.pop()
            used_pairs = used_before

            if len(best_so_far) >= target_weeks or stop_flag:
                return

        dead_state.add(key)

    if target_weeks <= 0:
        return []
    if (num_players <= 0) or (group_size < 2) or (num_players % group_size != 0):
        return []

    dfs_build(schedule=[], used_pairs=set())
    return [[list(group) for group in week] for week in current_progress]


# ==========================================================
# Public API
# ==========================================================

def find_max_weeks(num_players: int,
                   group_size: int,
                   algorithm: str = "Depth-First Search (DFS)",
                   depth_limit: Optional[int] = None) -> Tuple[List[List[List[int]]], int]:
    """Public API entry used by app.py."""
    global stop_flag, current_progress
    stop_flag = False
    current_progress = []

    cap = calculate_max_theoretical_weeks(num_players, group_size)

    if algorithm == "Depth-Limited Search (DLS)" and depth_limit is not None:
        target = max(1, min(int(depth_limit), cap))
    else:
        target = cap

    schedule = _search_weeks(num_players, group_size, target)
    return schedule, len(schedule)
