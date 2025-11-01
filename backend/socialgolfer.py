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
