import itertools
import time

# --- DFS with Backtracking Implementation (with Group Ordering Symmetry Breaking) ---

def solve_social_golfer_dfs(G, S, W, verbose=False):
    """
    Solves the Social Golfer Problem using Depth-First Search with backtracking.
    Includes symmetry breaking for ordering groups within a week.

    Args:
        G (int): Number of groups per week.
        S (int): Number of golfers per group.
        W (int): Number of weeks.
        verbose (bool): If True, prints status messages about week finding.

    Returns:
        list of list of list of int: A list representing the schedule,
                                     where schedule[week][group] is a list of golfer IDs.
                                     Returns None if no solution is found.
    """
    num_golfers = G * S
    all_golfers = frozenset(range(num_golfers)) # Golfers 0 to num_golfers-1

    solution_schedule = [None] * W
    played_together_history = set()

    # Store the successfully constructed weeks in the order they were confirmed
    # This will be printed at the very end if a full solution is found.
    successful_weeks_log = [None] * W 
    
    # Track weeks explored to avoid duplicates (for debugging/optimization)
    weeks_tried_count = [0]  # Use list to allow modification in nested functions
    weeks_found_count = [0]  # Track how many valid weeks were found at each level

    def find_schedule_recursive(current_week):
        if current_week == W:
            # All weeks found, this is a complete solution for the target W
            return True

        if verbose:
            print(f"  Attempting to construct Week {current_week + 1}...")

        temp_this_week_groups = []
        golfers_remaining_for_this_week = set(all_golfers)
        
        # Track if this is the first week (for counting)
        is_first_week = (current_week == 0)
        if is_first_week:
            weeks_found_count[0] = 0  # Reset counter for first week attempts

        def build_week_groups_recursive(current_group_idx, golfers_currently_available_for_week):
            # Base Case: All groups for the current week are filled
            if current_group_idx == G:
                # All golfers must have been assigned to a group for this week
                if golfers_currently_available_for_week:
                     return False
                
                new_pairs_from_this_week = set()
                for group in temp_this_week_groups:
                    for i in range(S):
                        for j in range(i + 1, S):
                            pair = frozenset({group[i], group[j]})
                            new_pairs_from_this_week.add(pair)
                
                # Check for conflicts with past weeks' pairings before updating history
                if not new_pairs_from_this_week.isdisjoint(played_together_history):
                    return False

                # --- SUCCESS: A valid set of groups for the current week has been found ---
                # Count this as a valid week tried (especially for first week)
                if is_first_week:
                    weeks_tried_count[0] += 1
                    weeks_found_count[0] += 1
                    if verbose:
                        print(f"  Found valid week {weeks_found_count[0]}: {temp_this_week_groups}")
                
                # Update history and solution schedule for this potential path
                played_together_history.update(new_pairs_from_this_week)
                solution_schedule[current_week] = list(temp_this_week_groups)
                
                # Recurse for the next week
                if find_schedule_recursive(current_week + 1):
                    # If this path leads to a full solution, record this week
                    successful_weeks_log[current_week] = list(temp_this_week_groups)
                    return True
                
                # BACKTRACK: If the next week (or subsequent) failed, undo this week's changes
                # This allows us to try a DIFFERENT valid week configuration
                played_together_history.difference_update(new_pairs_from_this_week)
                solution_schedule[current_week] = None # Clear this week's entry
                successful_weeks_log[current_week] = None # Clear this from the log too
                
                # CRITICAL: Return False to continue searching for other valid week configurations
                # The backtracking loop should continue to try the next valid week
                # Do NOT return True here - we want to keep exploring
                return False

            # --- Try to form the current group (current_group_idx) ---

            # Ensure we have enough golfers left to form a group
            if len(golfers_currently_available_for_week) < S:
                return False

            # Symmetry Breaking: The first golfer of the current group must be
            # >= the first golfer of the last group added (if not the first group).
            min_first_golfer_for_this_group = 0
            if current_group_idx > 0:
                # We sort groups by their first golfer ID. So, the first golfer
                # of the current group must be >= the first golfer of the *previous* group.
                min_first_golfer_for_this_group = temp_this_week_groups[-1][0] 
            
            # Find the actual first golfer for this group that respects the symmetry breaking.
            actual_first_golfer_for_group = -1
            # Iterate through available golfers in sorted order to find the smallest suitable one.
            for g in sorted(list(golfers_currently_available_for_week)):
                if g >= min_first_golfer_for_this_group:
                    actual_first_golfer_for_group = g
                    break
            
            if actual_first_golfer_for_group == -1: # No suitable golfer found for this position
                return False

            # Create the pool of remaining golfers from which to choose S-1 additional golfers
            remaining_pool_for_combination = sorted(list(golfers_currently_available_for_week - {actual_first_golfer_for_group}))

            # Ensure enough golfers are available for combinations
            if len(remaining_pool_for_combination) < S - 1:
                return False

            # Generate combinations of S-1 golfers to complete the current group
            # IMPORTANT: We try ALL combinations - the backtracking ensures we explore all branches
            for other_golfers_tuple in itertools.combinations(remaining_pool_for_combination, S - 1):
                current_group = tuple(sorted((actual_first_golfer_for_group,) + other_golfers_tuple))

                # Check #1: Validity of this group (no internal repeated pairs from history)
                # Early pruning: check pairs before committing
                group_pairs = {frozenset({current_group[i], current_group[j]}) 
                              for i in range(S) for j in range(i + 1, S)}
                
                if not group_pairs.isdisjoint(played_together_history):
                    continue  # Skip this invalid group, try next combination

                # Valid group found - MAKE MOVE
                temp_this_week_groups.append(list(current_group))
                
                # Update available golfers for THIS week for the NEXT group
                next_golfers_available_for_week = golfers_currently_available_for_week - set(current_group)

                # Recurse to fill the next group in this week
                if build_week_groups_recursive(current_group_idx + 1, next_golfers_available_for_week):
                    return True

                # BACKTRACK: If recursive call failed, undo changes for this group
                # This allows us to try the next combination for this group position
                temp_this_week_groups.pop()
            
            # All combinations for this group position exhausted - backtrack to previous group
            return False

        # Start building groups for the current_week from group 0,
        # using all golfers as initially available for this week.
        return build_week_groups_recursive(0, golfers_remaining_for_this_week)

    # Start the recursive search
    result = find_schedule_recursive(0)
    
    # Debug info: show how many first weeks were tried
    if weeks_tried_count[0] > 0:
        print(f"  (Explored {weeks_tried_count[0]} different valid first weeks)")
    
    if result:
        # After the full solution is found, print them in order, if verbose
        # This is where the final set of weeks are confirmed
        if verbose:
            print(f"  --- Full schedule for W={W} successfully constructed! ---")
            for week_idx, week in enumerate(successful_weeks_log):
                print(f"  Week {week_idx + 1}: {week}")
        return solution_schedule
    else:
        return None

# (DLS function remains unchanged as it's not used in the main loop for finding max weeks)
CUTOFF = "CUTOFF"
def solve_social_golfer_dls(G, S, W, depth_limit):
    num_golfers = G * S
    all_golfers = frozenset(range(num_golfers))

    solution_schedule = [None] * W
    played_together_history = set()

    def find_schedule_recursive_dls(current_week, current_depth):
        if current_depth > depth_limit:
            return CUTOFF

        if current_week == W:
            return True

        temp_this_week_groups = []
        golfers_remaining_for_this_week = set(all_golfers)

        def build_week_groups_recursive_dls(current_group_idx, golfers_currently_available_for_week, current_depth_for_groups):
            if current_depth_for_groups > depth_limit:
                return CUTOFF

            if current_group_idx == G:
                if golfers_currently_available_for_week:
                    return False
                
                new_pairs_from_this_week = set()
                for group in temp_this_week_groups:
                    for i in range(S):
                        for j in range(i + 1, S):
                            pair = frozenset({group[i], group[j]})
                            new_pairs_from_this_week.add(pair)
                
                if not new_pairs_from_this_week.isdisjoint(played_together_history):
                    return False

                played_together_history.update(new_pairs_from_this_week)
                solution_schedule[current_week] = list(temp_this_week_groups)
                
                result = find_schedule_recursive_dls(current_week + 1, current_depth_for_groups) # Depth is cumulative by groups
                if result == True: return True
                if result == CUTOFF: return CUTOFF

                played_together_history.difference_update(new_pairs_from_this_week)
                return False

            if len(golfers_currently_available_for_week) < S:
                return False

            # Symmetry Breaking: First golfer of current group must be >= first golfer of previous group
            min_first_golfer_for_this_group = 0
            if current_group_idx > 0:
                min_first_golfer_for_this_group = temp_this_week_groups[-1][0] 
            
            actual_first_golfer_for_group = -1
            for g in sorted(list(golfers_currently_available_for_week)):
                if g >= min_first_golfer_for_this_group:
                    actual_first_golfer_for_group = g
                    break
            
            if actual_first_golfer_for_group == -1:
                return False

            remaining_pool_for_combination = sorted(list(golfers_currently_available_for_week - {actual_first_golfer_for_group}))

            if len(remaining_pool_for_combination) < S - 1:
                return False

            for other_golfers_tuple in itertools.combinations(remaining_pool_for_combination, S - 1):
                current_group = tuple(sorted((actual_first_golfer_for_group,) + other_golfers_tuple))

                is_valid_group = True
                for i in range(S):
                    for j in range(i + 1, S):
                        pair = frozenset({current_group[i], current_group[j]})
                        if pair in played_together_history:
                            is_valid_group = False
                            break
                    if not is_valid_group:
                        break

                if is_valid_group:
                    temp_this_week_groups.append(list(current_group))
                    next_golfers_available_for_week = golfers_currently_available_for_week - set(current_group)

                    result = build_week_groups_recursive_dls(current_group_idx + 1, next_golfers_available_for_week, current_depth_for_groups + 1)
                    if result == True: return True
                    if result == CUTOFF: return CUTOFF

                    temp_this_week_groups.pop()
            return False

        return build_week_groups_recursive_dls(0, golfers_remaining_for_this_week, current_depth)

    result = find_schedule_recursive_dls(0, 0)
    if result == True:
        return solution_schedule
    elif result == CUTOFF:
        return CUTOFF
    else:
        return None



# --- Main execution to find maximum weeks (using the corrected DFS) ---
if __name__ == "__main__":
    # --- Configuration for your specific problem (12 players, group size 4) ---
    G_val = 5 # Number of groups (12 players / 4 golfers/group)
    S_val = 4 # Golfers per group
    num_players = G_val * S_val

    print(f"Finding maximum weeks for {num_players} players, with group size {S_val} (G={G_val})...")

    max_achieved_weeks = 0
    best_schedule_found = None
    
    total_unique_pairs = (num_players * (num_players - 1)) // 2
    pairs_per_group = (S_val * (S_val - 1)) // 2  # C(S_val, 2) pairs per group
    pairs_per_week = G_val * pairs_per_group
    
    # Theoretical maximum: floor((N-1)/(P-1)) where N=num_players, P=group_size
    # This is the proven upper bound for Social Golfer Problem
    theoretical_max_W = (num_players - 1) // (S_val - 1) if S_val > 1 else 0
    
    print(f"Total pairs available: {total_unique_pairs}")
    print(f"Pairs per group: {pairs_per_group}, Pairs per week: {pairs_per_week}")
    print(f"Theoretical maximum weeks: {theoretical_max_W}")
    print("Searching now. This might still take a long time, especially for higher W values...")

    current_W_to_test = 1
    total_search_time = 0

    while True:
        # print(f"\nAttempting to solve for W = {current_W_to_test}...")
        start_time = time.time()
        
        # Pass verbose=False to suppress intermediate messages
        solution = solve_social_golfer_dfs(G=G_val, S=S_val, W=current_W_to_test, verbose=False)
        
        end_time = time.time()
        duration = end_time - start_time
        total_search_time += duration
        # print(f"  Attempt for W = {current_W_to_test} took {duration:.4f} seconds.")

        if solution:
            max_achieved_weeks = current_W_to_test
            best_schedule_found = solution
            print(f"  Solution found for W = {current_W_to_test}. Continuing to W = {current_W_to_test + 1}...")
            
            current_W_to_test += 1
            
            if current_W_to_test > theoretical_max_W:
                print(f"  Reached theoretical maximum weeks ({theoretical_max_W}). Stopping.")
                break

        else:
            print(f"  No solution found for W = {current_W_to_test}. This is the maximum.")
            break

    print("\n" + "="*50 + "\n")
    print(f"Summary for {num_players} players (G={G_val}, S={S_val}):")
    print(f"Maximum number of weeks found: {max_achieved_weeks}")
    print(f"Total time spent searching: {total_search_time:.4f} seconds")

    if best_schedule_found:
        print("\nFinal Best schedule found (for max weeks):")
        for week_idx, week in enumerate(best_schedule_found):
            print(f"  Week {week_idx + 1}: {week}")
    else:
        print("No schedule found for even W=1, which indicates an issue or invalid parameters.")

    # # --- Additional Test Cases (for quick verification) ---
    # print("\n" + "="*50 + "\n")
    # print("Verifying DFS with a simple case (G=2, S=2, W=3 - 4 golfers)")
    # start_time_verify_4 = time.time()
    # solution_verify_4 = solve_social_golfer_dfs(G=2, S=2, W=3, verbose=True) # Verbose for this too
    # end_time_verify_4 = time.time()
    # if solution_verify_4:
    #     print(f"Solution for (G=2, S=2, W=3) found in {end_time_verify_4 - start_time_verify_4:.4f} seconds.")
    # else:
    #     print(f"No solution for (G=2, S=2, W=3) found in {end_time_verify_4 - start_time_verify_4:.4f} seconds.")