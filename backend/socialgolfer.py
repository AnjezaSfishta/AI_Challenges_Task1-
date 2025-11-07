import itertools
from typing import List, Tuple, Set, Optional, Dict, Iterable


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
# DFS / DLS with Controlled Logging
# ==========================================================

def _search_weeks(num_players: int,
                  group_size: int,
                  target_weeks: int) -> List[List[List[int]]]:
    """Backtracking search that prints each week only once when depth increases."""

    all_players = list(range(1, num_players + 1))
    groups_per_week = num_players // group_size
    pairs_per_group = (group_size * (group_size - 1)) // 2
    pairs_per_week = groups_per_week * pairs_per_group
    total_pairs = (num_players * (num_players - 1)) // 2

    best_so_far: List[List[Tuple[int, ...]]] = []
    seen_depth: Dict[frozenset, int] = {}
    dead_state: Set[frozenset] = set()
    printed_depths: Set[int] = set()  # <- tracks what depths were printed

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
        nonlocal best_so_far, printed_depths

        depth_now = len(schedule)

        # Reached or exceeded depth target
        if depth_now >= target_weeks:
            if depth_now > len(best_so_far):
                best_so_far = [wk.copy() for wk in schedule]
                if depth_now not in printed_depths:
                    printed_depths.add(depth_now)
                    print(f"✅ Week {depth_now} finalized: {[[list(g) for g in schedule[-1]]]}", flush=True)
            return

        # Pruning checks
        if not admissible_can_reach(depth_now, len(used_pairs)):
            return
        if not forward_check(used_pairs, depth_now):
            return

        # Memoization
        key = frozenset(used_pairs)
        prev_depth = seen_depth.get(key, -1)
        if prev_depth >= depth_now:
            return
        seen_depth[key] = depth_now

        if key in dead_state:
            return

        next_week_found = False
        for next_week in _iter_one_week(all_players, group_size, used_pairs):
            next_week_found = True
            if depth_now > 0 and next_week == schedule[-1]:
                continue

            new_pairs_this_week = set().union(*(pairs_of(g) for g in next_week))
            schedule.append(next_week)
            used_before = used_pairs
            used_pairs = used_pairs | new_pairs_this_week

            # If we’ve reached a new max depth → print once
            if len(schedule) > len(best_so_far) and len(schedule) not in printed_depths:
                printed_depths.add(len(schedule))
                print(f"✅ Week {len(schedule)} finalized: {[[list(g) for g in next_week]]}", flush=True)

            dfs_build(schedule, used_pairs)

            schedule.pop()
            used_pairs = used_before

            if len(best_so_far) >= target_weeks:
                return

        if not next_week_found:
            dead_state.add(key)
            return

    # Base conditions
    if target_weeks <= 0:
        return []
    if (num_players <= 0) or (group_size < 2) or (num_players % group_size != 0):
        return []

    # Simple single week case
    if target_weeks == 1:
        gen = _iter_one_week(all_players, group_size, used_pairs_global=set())
        try:
            first = next(gen)
            print(f"✅ Week 1 finalized: {[[list(g) for g in first]]}", flush=True)
            return [[list(group) for group in first]]
        except StopIteration:
            return []

    dfs_build(schedule=[], used_pairs=set())

    return [[list(group) for group in week] for week in best_so_far]


# ==========================================================
# Public Algorithms
# ==========================================================

def dfs_weeks(num_players: int, group_size: int) -> List[List[List[int]]]:
    cap = calculate_max_theoretical_weeks(num_players, group_size)
    return _search_weeks(num_players, group_size, cap)


def dls_weeks(num_players: int, group_size: int, depth_limit: int) -> List[List[List[int]]]:
    cap = calculate_max_theoretical_weeks(num_players, group_size)
    target = max(1, min(depth_limit, cap))
    return _search_weeks(num_players, group_size, target)

# ==========================================================
# Flask-facing API
# ==========================================================

def find_max_weeks(num_players: int,
                   group_size: int,
                   algorithm: str = "Depth-First Search (DFS)",
                   depth_limit: Optional[int] = None) -> Tuple[List[List[List[int]]], int]:
    """Public API entry for Flask app."""
    if num_players <= 0 or group_size < 2 or (num_players % group_size) != 0:
        return [], 0

    if algorithm == "Depth-First Search (DFS)":
        schedule = dfs_weeks(num_players, group_size)
    elif algorithm == "Depth-Limited Search (DLS)":
        lim = 1 if depth_limit is None else int(max(1, depth_limit))
        schedule = dls_weeks(num_players, group_size, lim)
    else:
        schedule = dfs_weeks(num_players, group_size)

    return schedule, len(schedule)


# ==========================================================
# Local Quick Test
# ==========================================================

if __name__ == "__main__":
    for n in (8, 12, 16, 20):
        sched, w = find_max_weeks(n, 4, "Depth-First Search (DFS)")
        print(f"\nN={n}, P=4 -> weeks={w}")
        for i, week in enumerate(sched, 1):
            print(f"Week {i}: {week}")
