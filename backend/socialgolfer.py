import itertools
import random

def is_valid_week(week, history):
    """Check if no pair of players repeats."""
    all_players = [p for group in week for p in group]
    if len(all_players) != len(set(all_players)):
        return False
    for group in week:
        for a, b in itertools.combinations(group, 2):
            if tuple(sorted((a, b))) in history:
                return False
    return True

def add_to_history(week, history):
    """Add all pairs from this week into history."""
    for group in week:
        for a, b in itertools.combinations(group, 2):
            history.add(tuple(sorted((a, b))))
            
def generate_random_week(players, group_size):
    """Shuffle players into random groups."""
    shuffled = players.copy()
    random.shuffle(shuffled)
    return [shuffled[i:i + group_size] for i in range(0, len(shuffled), group_size)]

def backtrack(schedule, history, players, group_size, max_weeks, depth=0, depth_limit=None):
    """Recursive DFS/DLS search."""
    if len(schedule) >= max_weeks:
        return schedule
    if depth_limit and depth >= depth_limit:
        return None
    for _ in range(300):  # Try random arrangements
        week = generate_random_week(players, group_size)
        if is_valid_week(week, history):
            new_history = history.copy()
            add_to_history(week, new_history)
            result = backtrack(schedule + [week], new_history, players, group_size, max_weeks, depth + 1, depth_limit)
            if result:
                return result
    return None

def can_schedule_weeks(num_players, group_size, target_weeks, algorithm, depth_limit=None):
    players = list(range(num_players))
    history = set()
    if algorithm == "Depth-First Search (DFS)":
        return backtrack([], history, players, group_size, target_weeks)
    else:
        return backtrack([], history, players, group_size, target_weeks, depth_limit=depth_limit)

def find_max_weeks(num_players, group_size, algorithm, depth_limit=None, max_attempt=10, progress_callback=None):
    """Incrementally find the maximum number of feasible weeks."""
    best_solution, best_weeks = None, 0
    for w in range(1, max_attempt + 1):
        if progress_callback:
            progress_callback(w, max_attempt, f"⏳ Trying {w} weeks...")
        schedule = can_schedule_weeks(num_players, group_size, w, algorithm, depth_limit)
        if schedule:
            best_solution, best_weeks = schedule, w
            if progress_callback:
                progress_callback(w, max_attempt, f"✅ {w} weeks possible!")
        else:
            if progress_callback:
                progress_callback(w, max_attempt, f"⚠️ {w} weeks not possible — stopping.")
            break
    if progress_callback:
        progress_callback(max_attempt, max_attempt, "🔍 Search completed.")
    return best_solution, best_weeks
