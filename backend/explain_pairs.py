"""
Visual explanation of pairs in groups
"""
import itertools

print("="*60)
print("UNDERSTANDING PAIRS IN A GROUP")
print("="*60)
print()

# Example: Group of 4 players
players = ['A', 'B', 'C', 'D']
print(f"Group of {len(players)} players: {', '.join(players)}")
print()

print("All possible pairs (combinations of 2 players):")
pairs = []
for i, combo in enumerate(itertools.combinations(players, 2), 1):
    pairs.append(combo)
    print(f"  {i}. {combo[0]}-{combo[1]}")

print()
print(f"Total pairs: {len(pairs)}")
print()

print("Formula explanation:")
print(f"  C(n, k) = n! / (k! × (n-k)!)")
print(f"  C(4, 2) = 4! / (2! × 2!) = (4×3×2×1) / ((2×1) × (2×1))")
print(f"  C(4, 2) = 24 / (2 × 2) = 24 / 4 = 6")
print()

print("For Social Golfer Problem with 12 players, groups of 4:")
print("  - 12 players = 3 groups per week")
print("  - Each group has 6 pairs")
print("  - Total pairs per week = 3 × 6 = 18 pairs")
print("  - Total pairs available = C(12,2) = 66 pairs")
print("  - Theoretical max weeks = floor(66/18) = 3 weeks")
print()
print("Note: You might think '2 pairs per group' but that's not correct.")
print("A group of 4 players has 6 unique pairs because:")
print("  - Each player pairs with each other player exactly once")
print("  - Player A pairs with B, C, D (3 pairs)")
print("  - Player B pairs with C, D (2 more pairs, A-B already counted)")
print("  - Player C pairs with D (1 more pair, others already counted)")
print("  - Total: 3 + 2 + 1 = 6 pairs")

