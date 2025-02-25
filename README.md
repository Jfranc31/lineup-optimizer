# Lineup Optimizer

## Overview
This project optimizes player lineup positioning based on their preferred sides in a formation. It ensures that each player is placed in the position where they perform best, swapping players when necessary and adjusting for AI placeholders.

## How to install.
Clone this repository and open a terminal with the folder.
Ensure Python 3 is installed.

## Features
- Ensures players are positioned on their optimal side (left or right).
- Swaps players if it improves overall team alignment.
- Moves human players to their better side when paired with an AI.
- Supports dynamic position affinity scoring.

## How It Works
1. **Iterates through position pairs** (e.g., `LB-RB`, `LM-RM`).
2. **Calculates player affinities** for left and right side positions.
3. **Swaps players** if it improves alignment.
4. **Handles AI placeholders** by shifting real players to their stronger side.

## Code Example
```python
for left_pos, right_pos in side_pairs:
    if left_pos in lineup and right_pos in lineup:
        left_player, left_rating = lineup[left_pos]
        right_player, right_rating = lineup[right_pos]

        # Get player objects, ignoring AI placeholders
        left_player_obj = self.get_player(left_player) if left_player != "AI" else None
        right_player_obj = self.get_player(right_player) if right_player != "AI" else None

        if left_player_obj and right_player_obj:
            # Calculate affinities
            left_player_left_affinity = sum(left_player_obj.positions[pos]['min'] for pos in ['LW', 'LM', 'LB'])
            right_player_left_affinity = sum(right_player_obj.positions[pos]['min'] for pos in ['LW', 'LM', 'LB'])

            left_player_right_affinity = sum(left_player_obj.positions[pos]['min'] for pos in ['RW', 'RM', 'RB'])
            right_player_right_affinity = sum(right_player_obj.positions[pos]['min'] for pos in ['RW', 'RM', 'RB'])

            # Swap if beneficial
            if right_player_left_affinity + left_player_right_affinity > left_player_left_affinity + right_player_right_affinity:
                lineup[left_pos], lineup[right_pos] = (right_player, right_rating), (left_player, left_rating)

        elif left_player_obj:  # AI on right
            left_affinity = sum(left_player_obj.positions[pos]['min'] for pos in ['LW', 'LM', 'LB'])
            right_affinity = sum(left_player_obj.positions[pos]['min'] for pos in ['RW', 'RM', 'RB'])

            if right_affinity > left_affinity:
                lineup[right_pos], lineup[left_pos] = (left_player, left_rating), ("AI", 0)

        elif right_player_obj:  # AI on left
            left_affinity = sum(right_player_obj.positions[pos]['min'] for pos in ['LW', 'LM', 'LB'])
            right_affinity = sum(right_player_obj.positions[pos]['min'] for pos in ['RW', 'RM', 'RB'])

            if left_affinity > right_affinity:
                lineup[left_pos], lineup[right_pos] = (right_player, right_rating), ("AI", 0)