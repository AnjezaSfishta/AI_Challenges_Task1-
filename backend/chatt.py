import itertools
import time

# --- Problem parameters ---
NUM_GROUPS = 4       # g
GROUP_SIZE = 4       # p
NUM_GOLFERS = NUM_GROUPS * GROUP_SIZE
DEPTH_LIMIT = 5      # For 16 golfers, maximum valid weeks = 5

# --- Helper functions ---

def golfer_pairs(group):
    """Return all 2-player pairs from a group."""
    return {frozenset(pair) for pair in itertools.combinations(group, 2)}

def is_valid_week(week, used_pairs):
    """Check if no pair in the week was already used."""
    for group in week:
        for pair in golfer_pairs(group):
            if pair in used_pairs:
                return False
    return True

def all_pairs_in_week(week):
    """Return all pairs that appear in a week."""
    pairs = set()
    for group in week:
        pairs |= golfer_pairs(group)
    return pairs

# --- Recursive DFS ---

def dfs(weeks, used_pairs, depth, limit):
    """Depth-first search with backtracking."""
    if depth == limit:
        return weeks  # reached desired number of weeks

    # Generate all possible ways to divide players into groups for this week
    for week in generate_weeks(NUM_GOLFERS, GROUP_SIZE):
        if is_valid_week(week, used_pairs):
            new_used_pairs = used_pairs | all_pairs_in_week(week)
            result = dfs(weeks + [week], new_used_pairs, depth + 1, limit)
            if len(result) == limit:
                return result  # found complete schedule

    return weeks  # backtrack if no valid extension

# --- Week generation (systematic) ---

def generate_weeks(num_golfers, group_size):
    """Generate all possible weeks (unique partitions of golfers)."""
    golfers = list(range(num_golfers))
    first_group = golfers[:group_size]
    remaining = golfers[group_size:]
    for partition in partitions(remaining, group_size):
        yield [first_group] + partition

def partitions(golfers, group_size):
    """Generate all unique partitions of golfers into equal-sized groups."""
    if not golfers:
        yield []
        return

    first = golfers[0]
    rest = golfers[1:]

    for combo in itertools.combinations(rest, group_size - 1):
        group = [first] + list(combo)
        remaining = [x for x in rest if x not in combo]
        for rest_partition in partitions(remaining, group_size):
            yield [group] + rest_partition

# --- Main ---

def main():
    print("\n=== Social Golfers Problem - DFS Backtracking ===")
    print(f"{NUM_GOLFERS} golfers → {NUM_GROUPS} groups × {GROUP_SIZE}, goal weeks = {DEPTH_LIMIT}\n")

    start = time.time()
    schedule = dfs([], set(), 0, DEPTH_LIMIT)
    elapsed = time.time() - start

    if len(schedule) > 0:
        print(f"✅ Found {len(schedule)} valid weeks in {elapsed:.2f} seconds\n")
        for i, week in enumerate(schedule, 1):
            print(f"📅 Week {i}")
            for g, group in enumerate(week, 1):
                print(f"  Group {g}: {group}")
            print("-" * 40)
    else:
        print(f"❌ No valid schedule found (elapsed: {elapsed:.2f}s)")

if __name__ == "__main__":
    main()
