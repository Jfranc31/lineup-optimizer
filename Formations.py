def draw_side_view_pitch():
    # Define pitch dimensions
    width = 75  # Width of the pitch (side-to-side)
    height = 25  # Height of the pitch (goal-to-half line)

    # Create the pitch as a list of lists (2D array)
    pitch = [[' ' for _ in range(width)] for _ in range(height)]

    # Draw the goal area at the bottom, centered horizontally
    penalty_width = width // 2  # Increased width for the goal
    penalty_height = height // 3
    penalty_start_x = (width - penalty_width) // 2
    for y in range(penalty_height):
        # Only draw the vertical borders of the goal area
        pitch[height - 1 - y][penalty_start_x-1] = f"\033[91m|\033[0m"  # Left border
        pitch[height - 1 - y][penalty_start_x + penalty_width] = f"\033[91m|\033[0m"  # Right border

    for x in range(penalty_width):
        pitch[height - 1 - penalty_height][x + penalty_start_x] = f"\033[91m-\033[0m"

    goal_width = width // 3
    goal_height = height // 6
    goal_start_x = (width - goal_width) // 2
    for y in range(goal_height):
        pitch[height - 1 - y][goal_start_x - 1] = f"\033[91m|\033[0m"
        pitch[height - 1 - y][goal_start_x + goal_width] = f"\033[91m|\033[0m"
    
    for x in range(goal_width):
        pitch[height - 1 - goal_height][x + goal_start_x] = f"\033[91m-\033[0m"

    # Draw the half line at the top
    half_line = 0  # Half line is at the very top of the pitch
    for x in range(width):
        pitch[half_line][x] = '-'

    # Draw the border (top, bottom, left, right)
    for i in range(height):
        pitch[i][0] = '|'
        pitch[i][width - 1] = '|'
    for i in range(width):
        pitch[0][i] = '-'
        pitch[height - 1][i] = '-'
    # Add corners
    pitch[0][0] = "┌"
    pitch[0][width - 1] = "┐"
    pitch[height - 1][0] = "└"
    pitch[height - 1][width - 1] = "┘"
    
    # Add players in positions that replace the space
    player_positions = [
        (23, 37, 23, 38, "G", "K"),  # Goalkeeper (represented by P)
        (18, 10, 18, 11, "L", "B"),  # Left-back (represented by P)
        (18, 30, 18, 31, "C", "B"),  # Center-back (represented by P)
        (18, 43, 18, 44, "C", "B"),  # Center-back (represented by P)
        (18, 65, 18, 66, "R", "B")   # Right-back (represented by P)
    ]
    
    for a, b, c, d, first, second in player_positions:
        pitch[a][b] = first  # Replace the space with the player marker
        pitch[c][d] = second

    # Print the pitch
    for row in pitch:
        print(''.join(row))

# Call the function to draw the side view pitch
draw_side_view_pitch()


# player 1 ST: 5 CAM: 5 CM: 5
# player 2 ST: 5 CAM: 4 CM: 4
# player 3 ST: 4 CAM: 5 CM: 3
#
#
#