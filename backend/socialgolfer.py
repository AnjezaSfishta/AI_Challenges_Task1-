import itertools
import math
from typing import List, Tuple, Set, Optional, Dict


# --------------------------- Utilities ---------------------------

def calculate_max_theoretical_weeks(n: int, p: int) -> int:
    """
    Upper bound on weeks for Social Golfers:
        floor((n - 1) / (p - 1))
    """
    if p <= 1:
        return 0
    return (n - 1) // (p - 1)


def pairs_of(group: Tuple[int, ...]) -> Set[Tuple[int, int]]:
    """All unordered pairs from a tuple group of players (sorted pairs)."""
    return {tuple(sorted(x)) for x in itertools.combinations(group, 2)}


def canonical_week(week: List[Tuple[int, ...]]) -> List[Tuple[int, ...]]:
    """
    Normalize a week representation:
    - sort members inside each group,
    - sort groups lexicographically.
    This kills permutations of same structure.
    """
    return sorted([tuple(sorted(g)) for g in week])


# --------------------- Week Construction (BT) ---------------------

def build_all_weeks(players: List[int],
                    group_size: int,
                    used_pairs_global: Set[Tuple[int, int]]) -> List[List[Tuple[int, ...]]]:
    """
    Generate ALL valid "weeks":
      - partition all players into groups of size group_size
      - no pair is reused (not in used_pairs_global)
      - no pair repeats within the constructed week either
    Symmetry is reduced by always picking the smallest remaining player
    as the "anchor" of the next group.
    """
    players = sorted(players)
    groups_per_week = len(players) // group_size

    results: List[List[Tuple[int, ...]]] = []
    week_so_far: List[Tuple[int, ...]] = []
    week_pairs: Set[Tuple[int, int]] = set()

    def extend(rem: List[int]) -> None:
        if len(week_so_far) == groups_per_week:
            results.append(canonical_week(week_so_far.copy()))
            return

        anchor = rem[0]  # smallest remaining -> break symmetry between groups

        for partners in itertools.combinations(rem[1:], group_size - 1):
            group = tuple(sorted((anchor, *partners)))
            ps = pairs_of(group)

            # reject if any pair is already used globally OR within this week
            if ps.isdisjoint(used_pairs_global) and ps.isdisjoint(week_pairs):
                # choose this group
                week_so_far.append(group)
                week_pairs_update = ps
                week_pairs.update(week_pairs_update)

                new_rem = [x for x in rem if x not in group]
                extend(new_rem)

                # backtrack
                week_so_far.pop()
                for pp in week_pairs_update:
                    week_pairs.discard(pp)

    extend(players)

    # deduplicate identical structures
    unique: List[List[Tuple[int, ...]]] = []
    seen = set()
    for w in results:
        key = tuple(w)
        if key not in seen:
            seen.add(key)
            unique.append(w)

    return unique


# --------------------- DFS / DLS with Backtracking ---------------------

def _search_weeks(num_players: int,
                  group_size: int,
                  target_weeks: int) -> List[List[List[int]]]:
    """
    Core recursive search to reach up to target_weeks weeks.
    This differs from previous attempts in one crucial way:
    - We DO NOT hardcode week 1.
    Instead we generate all valid first weeks and branch on them.
    """

    # Problem constants
    all_players = list(range(1, num_players + 1))
    groups_per_week = num_players // group_size
    pairs_per_group = (group_size * (group_size - 1)) // 2
    pairs_per_week = groups_per_week * pairs_per_group
    total_pairs = (num_players * (num_players - 1)) // 2  # C(n,2)

    # global best
    best_so_far: List[List[Tuple[int, ...]]] = []

    # memoization:
    # key: (frozenset(used_pairs), depth) -> we already explored this or deeper
    seen_depth: Dict[frozenset, int] = {}

    def admissible_can_reach(depth_now: int, used_pairs_count: int) -> bool:
        """
        Upper bound pruning:
        remaining_pairs = total_pairs - used_pairs_count
        each new full week consumes at least pairs_per_week distinct pairs,
        so the max extra weeks we *could* still add is floor(remaining/pairs_per_week).
        If depth_now + that max < target_weeks -> prune.
        """
        remaining_pairs = total_pairs - used_pairs_count
        max_additional_weeks = remaining_pairs // pairs_per_week
        return (depth_now + max_additional_weeks) >= target_weeks

    def dfs_build(schedule: List[List[Tuple[int, ...]]],
                  used_pairs: Set[Tuple[int, int]]) -> None:
        nonlocal best_so_far

        depth_now = len(schedule)

        # If we hit or exceed the target depth, update best and stop here.
        if depth_now >= target_weeks:
            if depth_now > len(best_so_far):
                best_so_far = [wk.copy() for wk in schedule]
            return

        # Admissible bound pruning
        if not admissible_can_reach(depth_now, len(used_pairs)):
            # can't possibly reach target_weeks from here
            if depth_now > len(best_so_far):
                best_so_far = [wk.copy() for wk in schedule]
            return

        # Memoization prune:
        key = frozenset(used_pairs)
        prev_depth = seen_depth.get(key, -1)
        # If we've already explored this "used_pairs state" with
        # at least this depth or deeper, don't redo.
        if prev_depth >= depth_now:
            return
        seen_depth[key] = depth_now

        # Build all possible next-week partitions
        candidate_weeks = build_all_weeks(all_players, group_size, used_pairs)
        if not candidate_weeks:
            # dead end
            if depth_now > len(best_so_far):
                best_so_far = [wk.copy() for wk in schedule]
            return

        # Heuristic: prefer weeks that add fewer new pairs first,
        # to keep more flexibility for deeper levels
        def new_pairs_count(week_struct: List[Tuple[int, ...]]) -> int:
            wk_pairs = set().union(*(pairs_of(g) for g in week_struct))
            return len(wk_pairs)

        candidate_weeks.sort(key=new_pairs_count)

        for next_week in candidate_weeks:
            # Light pruning: avoid repeating the exact same week back-to-back
            if depth_now > 0 and next_week == schedule[-1]:
                continue

            new_pairs_this_week = set().union(*(pairs_of(g) for g in next_week))

            # commit
            schedule.append(next_week)
            prev_used_pairs = used_pairs
            used_pairs = used_pairs | new_pairs_this_week

            dfs_build(schedule, used_pairs)

            # backtrack
            schedule.pop()
            used_pairs = prev_used_pairs

            # if we've already matched target_weeks, no need to branch more
            if len(best_so_far) >= target_weeks:
                return

    # EDGE CASES
    if target_weeks <= 0:
        return []
    # If target is 1, we just need ANY valid single week.
    # We'll generate one-week schedules by building all possible weeks directly
    # and pick the first one.
    if target_weeks == 1:
        first_weeks = build_all_weeks(all_players, group_size, used_pairs_global=set())
        if not first_weeks:
            return []
        best_one = first_weeks[0]
        return [[list(group) for group in best_one]]

    # Start recursion with *no* fixed Week 1
    # We start with empty schedule, empty used_pairs
    dfs_build(schedule=[], used_pairs=set())

    # Convert tuples → lists for JSON
    return [
        [list(group) for group in week]
        for week in best_so_far
    ]


def dfs_weeks(num_players: int, group_size: int) -> List[List[List[int]]]:
    """
    Plain DFS search: try to reach the theoretical maximum depth.
    """
    cap = calculate_max_theoretical_weeks(num_players, group_size)
    return _search_weeks(num_players, group_size, cap)


def dls_weeks(num_players: int, group_size: int, depth_limit: int) -> List[List[List[int]]]:
    """
    Depth-Limited Search (DLS): we cap how deep we want to go.
    """
    cap = calculate_max_theoretical_weeks(num_players, group_size)
    target = max(1, min(depth_limit, cap))
    return _search_weeks(num_players, group_size, target)


def ids_weeks(num_players: int, group_size: int) -> List[List[List[int]]]:
    """
    Iterative Deepening Search (IDS): try 1, then 2, ..., up to cap.
    We keep the best schedule found so far.
    """
    cap = calculate_max_theoretical_weeks(num_players, group_size)
    best: List[List[List[int]]] = []
    for d in range(1, cap + 1):
        candidate = _search_weeks(num_players, group_size, d)
        if len(candidate) > len(best):
            best = candidate
        if len(best) >= cap:
            break
    return best


# ----------------------- Flask-facing API -----------------------

def find_max_weeks(num_players: int,
                   group_size: int,
                   algorithm: str = "Depth-First Search (DFS)",
                   depth_limit: Optional[int] = None) -> Tuple[List[List[List[int]]], int]:
    """
    Public API entry used by app.py.
    Returns (schedule, weeks)
    where schedule is:
        [
            [ [p1,p2,p3,p4], [p5,p6,p7,p8], ... ],  # week 1
            [ [..], [..], ... ],                    # week 2
            ...
        ]
    """
    # basic sanity
    if num_players <= 0 or group_size < 2 or (num_players % group_size) != 0:
        return [], 0

    if algorithm == "Depth-First Search (DFS)":
        schedule = dfs_weeks(num_players, group_size)

    elif algorithm == "Depth-Limited Search (DLS)":
        lim = 1 if depth_limit is None else int(max(1, depth_limit))
        schedule = dls_weeks(num_players, group_size, lim)

    elif algorithm == "Iterative Deepening Search (IDS)":
        schedule = ids_weeks(num_players, group_size)

    else:
        schedule = dfs_weeks(num_players, group_size)

    return schedule, len(schedule)


# ----------------------- Local quick test -----------------------

if __name__ == "__main__":
    for n in (8, 12, 16, 20):
        sched, w = find_max_weeks(n, 4, "Depth-First Search (DFS)")
        print(f"\nN={n}, P=4 -> weeks={w}")
        for i, week in enumerate(sched, 1):
            print(f"Week {i}: {week}")
