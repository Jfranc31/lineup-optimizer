# main.py
import os
from Player_Stats import Team
from rich.console import Console
from rich.table import Table
from rich import box
from rich import print
from tabulate import tabulate

POSITIONS = ["GK", "LB", "CB", "RB", "CDM", "CM", "LM", "RM", "CAM", "LW", "RW", "ST"]
console = Console()

# Define available formations and their positions with improved spacing
FORMATION_LAYOUTS = {
    "4-3-3 attacking": {
        "ST": (3, 35),
        "LW": (3, 15),  # Moved further left
        "RW": (3, 55),  # Moved further right
        "CAM": (7, 35),
        "LCM": (11, 20),  # Spread midfield
        "RCM": (11, 50),  # Spread midfield
        "LB": (18, 10),   # Moved further left
        "LCB": (18, 28),  # Adjusted center backs
        "RCB": (18, 42),  # Adjusted center backs
        "RB": (18, 65),   # Moved further right
        "GK": (23, 36)
    },
    "4-3-3 defending": {
        "ST": (3, 35),
        "LW": (3, 15),  # Moved further left
        "RW": (3, 55),  # Moved further right
        "LCM": (9, 20),  # Spread midfield
        "RCM": (9, 50),  # Spread midfield
        "CDM": (11, 35),
        "LB": (18, 10),   # Moved further left
        "LCB": (18, 28),  # Adjusted center backs
        "RCB": (18, 42),  # Adjusted center backs
        "RB": (18, 65),   # Moved further right
        "GK": (23, 36)
    },
    "4-3-1-2": {
        "ST1": (3, 25),
        "ST2": (3, 45),
        "CAM": (7, 35),
        "LCM": (11, 20),  # Spread midfield
        "CM": (11, 35),
        "RCM": (11, 50),  # Spread midfield
        "LB": (18, 10),   # Moved further left
        "LCB": (18, 28),
        "RCB": (18, 42),
        "RB": (18, 65),   # Moved further right
        "GK": (23, 36)
    },
    "4-2-3-1": {
        "ST": (3, 35),
        "LAM": (7, 15),   # Moved further left
        "CAM": (7, 35),
        "RAM": (7, 55),   # Moved further right
        "CDM1": (11, 25),
        "CDM2": (11, 45),
        "LB": (18, 10),   # Moved further left
        "LCB": (18, 28),
        "RCB": (18, 42),
        "RB": (18, 65),   # Moved further right
        "GK": (23, 36)
    },
    "5-2-1-2": {
        "ST1": (3, 25),
        "ST2": (3, 45),
        "CAM": (7, 35),
        "CM1": (11, 25),
        "CM2": (11, 45),
        "LWB": (18, 8),    # Moved further left
        "LCB": (18, 25),
        "RCB": (18, 35),
        "CB3": (18, 45),
        "RWB": (18, 65),   # Moved further right
        "GK": (23, 36)
    }
}

# Update the formation mapping in Team class
FORMATION_POSITIONS = {
    "4-3-3 attacking": {
        "ST": "ST",
        "LW": "LW",
        "RW": "RW",
        "CAM": "CAM",
        "LCM": "CM",
        "RCM": "CM",
        "LB": "LB",
        "LCB": "CB",
        "RCB": "CB",
        "RB": "RB",
        "GK": "GK"
    },
    "4-3-3 defending": {
        "ST": "ST",
        "LW": "LW",
        "RW": "RW",
        "LCM": "CM",
        "RCM": "CM",
        "CDM": "CDM",
        "LB": "LB",
        "LCB": "CB",
        "RCB": "CB",
        "RB": "RB",
        "GK": "GK"
    },
    "4-3-1-2": {
        "ST1": "ST",
        "ST2": "ST",
        "CAM": "CAM",
        "LCM": "CM",
        "CM": "CM",
        "RCM": "CM",
        "LB": "LB",
        "LCB": "CB",
        "RCB": "CB",
        "RB": "RB",
        "GK": "GK"
    },
    "4-2-3-1": {
        "ST": "ST",
        "LAM": "CAM",
        "CAM": "CAM",
        "RAM": "CAM",
        "CDM1": "CDM",
        "CDM2": "CDM",
        "LB": "LB",
        "LCB": "CB",
        "RCB": "CB",
        "RB": "RB",
        "GK": "GK"
    },
    "5-2-1-2": {
        "ST1": "ST",
        "ST2": "ST",
        "CAM": "CAM",
        "CM1": "CM",
        "CM2": "CM",
        "LWB": "LB",
        "LCB": "CB",
        "RCB": "CB",
        "CB3": "CB",
        "RWB": "RB",
        "GK": "GK"
    }
}

def clear_screen():
    os.system('clear' if os.name == 'posix' else 'cls')

def display_player_names(team):
    players = list(team.players.keys())
    print(f"Players: {players}")

def display_menu():
    options = [
        "Add new player",
        "View player ratings",
        "Rate a player",
        "Modify your ratings",
        "Compare players",
        "View best lineup",
        "Show position rankings",
        "View position gaps",
        "Save and exit"
    ]
    
    options_length = len(options)
    
    while True:
        clear_screen()
        print("\n=== Pro Clubs Rating System ===")
        
        for i, option in enumerate(options, 1):
            print(f"{i}. {option}")
            
        try:
            choice = input(f"\nEnter your choice (1-{options_length}): ").strip()
            if choice.isdigit() and 1 <= int(choice) <= options_length:
                return int(choice)
        except ValueError:
            pass
        print("Invalid choice. Please try again.")

def rate_player(team, player_name=None):
    clear_screen()
    display_player_names(team)
    if player_name is None:
        player_name = input("Enter player name: ").strip().title()
    
    player = team.get_player(player_name)
    if not player:
        print(f"Player {player_name} not found!")
        return
    
    voter = input("Enter your name (for voting): ").strip().title()
    
    print("\nEnter ratings (0-5) for positions:")
    print("- Single number (e.g., '3') for fixed rating")
    print("- Range (e.g., '2-4') for potential rating")
    print("- Press Enter to skip position")
    print("- Enter 'done' to finish\n")
    
    for position in POSITIONS:
        # Show current average rating and top players in this position
        current = player.positions[position]
        print(f"\n{position}:")
        print(f"Current rating: {current['min']}-{current['max']}")
        
        # Show top 3 players in this position for comparison
        top_players = team.get_top_players_by_position(position)
        if top_players:
            print("Top rated players in this position:")
            for p_name, rating in top_players:
                if p_name != player_name:  # Don't show the current player
                    print(f"- {p_name}: {rating}")
        
        while True:
            rating = input(f"Enter rating for {position}: ").strip().lower()
            
            if rating == 'done':
                return
            if not rating:
                break
                
            try:
                if '-' in rating:
                    min_rating, max_rating = map(float, rating.split('-'))
                else:
                    min_rating = max_rating = float(rating)
                    
                if 0 <= min_rating <= 5 and 0 <= max_rating <= 5:
                    player.add_rating_vote(position, min_rating, max_rating, voter)
                    break
            except ValueError:
                pass
            print("Invalid input. Please enter a number (0-5) or range (e.g., '2-4')")

def modify_player_rating(team):
    """Allow a user to modify their specific ratings for a player"""
    clear_screen()
    display_player_names(team)
    
    player_name = input("Enter player name whose rating you want to modify: ").strip().title()
    player = team.get_player(player_name)
    
    if not player:
        print(f"Player {player_name} not found!")
        input("\nPress Enter to continue...")
        return
    
    voter = input("Enter your name (to find your votes): ").strip().title()
    
    # Check if this voter has rated the player
    has_votes = False
    for pos in POSITIONS:
        for vote in player.positions[pos]['votes']:
            if vote['voter'] == voter:
                has_votes = True
                break
        if has_votes:
            break
    
    if not has_votes:
        print(f"\nYou ({voter}) haven't rated {player_name} yet!")
        print("Please use the 'Rate a player' option first.")
        input("\nPress Enter to continue...")
        return
    
    # Display current ratings by this voter
    print(f"\n=== Your current ratings for {player_name} ===")
    
    table = Table(show_header=True, header_style="bold", box=box.SIMPLE)
    table.add_column("Position")
    table.add_column("Your Rating")
    
    for pos in POSITIONS:
        user_vote = None
        for vote in player.positions[pos]['votes']:
            if vote['voter'] == voter:
                user_vote = vote
                break
        
        if user_vote:
            if user_vote['min'] == user_vote['max']:
                rating_str = f"{user_vote['min']}"
            else:
                rating_str = f"{user_vote['min']}-{user_vote['max']}"
            table.add_row(pos, rating_str)
    
    console.print(table)
    
    # Modify ratings
    print("\nEnter the position you want to modify (or 'done' to finish):")
    while True:
        position = input("Position to modify: ").strip().upper()
        
        if position.lower() == 'done':
            break
            
        if position not in POSITIONS:
            print(f"Invalid position! Must be one of: {', '.join(POSITIONS)}")
            continue
        
        # Check if user has rated this position
        user_vote = None
        for vote in player.positions[position]['votes']:
            if vote['voter'] == voter:
                user_vote = vote
                break
        
        if not user_vote:
            print(f"You haven't rated {player_name} for {position} yet!")
            continue
        
        # Show current rating and get new one
        if user_vote['min'] == user_vote['max']:
            current_rating = f"{user_vote['min']}"
        else:
            current_rating = f"{user_vote['min']}-{user_vote['max']}"
            
        print(f"Current rating for {position}: {current_rating}")
        
        while True:
            new_rating = input(f"Enter new rating for {position} (0-5 or range like '2-4'): ").strip().lower()
            
            try:
                if '-' in new_rating:
                    min_rating, max_rating = map(float, new_rating.split('-'))
                else:
                    min_rating = max_rating = float(new_rating)
                    
                if 0 <= min_rating <= 5 and 0 <= max_rating <= 5:
                    # Update the rating
                    player.add_rating_vote(position, min_rating, max_rating, voter)
                    print(f"Rating updated for {position}!")
                    break
            except ValueError:
                pass
            print("Invalid input. Please enter a number (0-5) or range (e.g., '2-4')")
    
    print("\nRatings have been updated!")
    team.save_players()
    input("\nPress Enter to continue...")

def compare_players(team):
    clear_screen()
    display_player_names(team)
    print("Enter player names to compare (press Enter when done, or type 'ALL' to select all players)")
    players = []
    while True:
        name = input("Enter player name (or 'ALL' for all players): ").strip().title()
        if not name:
            if len(players) > 1:
                break
            else:
                print("Need at least two players!")
                continue
        
        if name == 'All' or name == 'ALL':
            # Get all player names
            players = list(team.players.keys())
            print(f"Selected all {len(players)} players")
            break
            
        if name in players:
            print("Already chose that player!")
            continue
            
        if team.get_player(name):
            players.append(name)
        else:
            print(f"Player {name} not found!")
    
    if len(players) < 2:
        print("Need at least 2 players to compare!")
        return
    
    position = input("\nEnter position to compare (or press Enter for all): ").strip().upper()
    if position and position != 'ALL' and position not in POSITIONS:
        print("Invalid position!")
        return
    
    # Get comparisons data
    raw_comparisons = team.compare_players(players, position)
    
    # Create a rich table
    table = Table(box=box.DOUBLE_EDGE)
    table.add_column("Position", style="bold")
    
    for player in players:
        table.add_column(player, justify="center")
    
    # Process each row to add colors
    for row in raw_comparisons:
        position_name = row[0]
        rating_strs = row[1:]
        
        # Create a rating priority list based on exact string matching
        # Order: Single high ratings first, then ranges
        ratings_with_index = []
        for i, rating_str in enumerate(rating_strs):
            if not rating_str or rating_str == '0.0':
                # Skip empty or 0.0 ratings
                continue
                
            # Determine a sort key for precise ordering
            if '-' in rating_str:
                # For ranges like "4.0-5.0", use both parts and a flag
                low, high = map(float, rating_str.split('-'))
                ratings_with_index.append((i, (high, low, 0)))  # 0 flag indicates range
            else:
                # For single values, make sure they sort higher than ranges with same max
                val = float(rating_str)
                ratings_with_index.append((i, (val, val, 1)))  # 1 flag prioritizes singles
        
        # Sort by max value (desc), then by single/range flag (desc)
        # This ensures "5.0" sorts higher than "4.0-5.0"
        ratings_with_index.sort(key=lambda x: (x[1][0], x[1][2], x[1][1]), reverse=True)

        # Now we handle the ranking logic where tied players get the same rank
        ranks = {}
        current_rank = 1
        last_rating = None
        for i, (idx, (max_rating, min_rating, _)) in enumerate(ratings_with_index):
            if last_rating is None or (max_rating != last_rating[0] or min_rating != last_rating[1]):
                # New rank if the rating is different from the last one
                ranks[idx] = current_rank
                current_rank += 1
            else:
                # If the rating is the same as the last one, assign the same rank
                ranks[idx] = ranks[ratings_with_index[i-1][0]]  # same rank as the previous player
            
            last_rating = (max_rating, min_rating)

        # Assign colors based on position in sorted list
        colors = {}
        for idx, rank in ranks.items():
            if rank == 1:
                colors[idx] = "green"
            elif rank == 2:
                colors[idx] = "blue"
            elif rank == 3:
                colors[idx] = "yellow"
            else:
                colors[idx] = "red"
        
        # Apply colors to ratings
        styled_ratings = []
        for i, rating_str in enumerate(rating_strs):
            if not rating_str or rating_str == '0.0':
                styled_ratings.append(f"[red]{rating_str}[/red]")
            else:
                color = colors.get(i, "red")
                styled_ratings.append(f"[{color}]{rating_str}[/{color}]")
        
        table.add_row(position_name, *styled_ratings)
    
    # Display the table
    console.print(table)
    input("\nPress Enter to continue...")

def show_best_lineup(team, formation=None):
    clear_screen()
    width = 75
    height = 25

    # If no formation specified, let user choose
    if formation is None:
        print("Available formations:")
        for i, form in enumerate(FORMATION_LAYOUTS.keys(), 1):
            print(f"{i}. {form}")
        
        while True:
            try:
                choice = int(input("\nSelect formation (enter number): "))
                if 1 <= choice <= len(FORMATION_LAYOUTS):
                    formation = list(FORMATION_LAYOUTS.keys())[choice - 1]
                    break
                print("Invalid choice. Please try again.")
            except ValueError:
                print("Please enter a number.")
    
    # Get lineup data with the selected formation
    lineup = team.get_best_lineup(formation, FORMATION_POSITIONS[formation])
    
    # Create the pitch
    pitch = [[' ' for _ in range(width)] for _ in range(height)]
    
    # Draw borders and lines
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
    
    # Draw penalty area
    penalty_width = width // 2
    penalty_height = height // 3
    penalty_start_x = (width - penalty_width) // 2
    for y in range(penalty_height):
        pitch[height - 1 - y][penalty_start_x-1] = '|'
        pitch[height - 1 - y][penalty_start_x + penalty_width] = '|'
    for x in range(penalty_width):
        pitch[height - 1 - penalty_height][x + penalty_start_x] = '-'

    # Draw goal area
    goal_width = width // 3
    goal_height = height // 6
    goal_start_x = (width - goal_width) // 2
    for y in range(goal_height):
        pitch[height - 1 - y][goal_start_x - 1] = '|'
        pitch[height - 1 - y][goal_start_x + goal_width] = '|'
    for x in range(goal_width):
        pitch[height - 1 - goal_height][x + goal_start_x] = '-'

    def safe_write(y, x, text):
        """Safely write text to pitch at given coordinates"""
        if 0 <= y < height:
            for i, char in enumerate(text):
                if 0 <= x + i < width:
                    pitch[y][x + i] = char
    
    # Add players to the pitch
    for pos, coords in FORMATION_LAYOUTS[formation].items():
        y, x = coords
        if pos in lineup:
            player, rating = lineup[pos]
            # Draw player icon
            safe_write(y, x, "□")
            
            # Write position
            pos_x = max(0, x - len(pos) // 2)
            safe_write(y - 1, pos_x, pos)
            
            # Write player name
            name = player[:7] if player != "AI" else "AI"
            name_x = max(0, x - len(name) // 2)
            safe_write(y + 1, name_x, name)
            
            # Write rating
            if player != "AI":
                rating_str = f"({rating:.1f})"
                rating_x = max(0, x - len(rating_str) // 2)
                safe_write(y + 2, rating_x, rating_str)
    
    # Print formation at top
    formation_text = f"=== Suggested Best Lineup ({formation}) ==="
    x_offset = (width - len(formation_text)) // 2
    safe_write(0, x_offset, formation_text)
    
    # Print the pitch
    print("\nPitch Layout:")
    for row in pitch:
        print(''.join(row))
    
    # Print detailed player list
    print("\nDetailed Player List:")
    table = Table(show_header=True, header_style="bold", box=box.SIMPLE)
    table.add_column("Position")
    table.add_column("Player")
    table.add_column("Rating")
    
    for pos, (player, rating) in lineup.items():
        rating_str = f"{rating:.1f}" if player != "AI" else "-"
        table.add_row(pos, player, rating_str)
    
    console.print(table)
    input("\nPress Enter to continue...")

def show_position_rankings(team):
    clear_screen()
    position = input("Enter position to view rankings: ").strip().upper()
    
    if position not in POSITIONS:
        print("Invalid position!")
        return
    
    top_players = team.get_top_players_by_position(position, limit=None)  # Get all players
    if not top_players:
        print(f"No players rated for {position}")
        return
    
    print(f"\n=== Rankings for {position} ===\n")
    rankings_data = [(i+1, name, f"{rating:.1f}") 
                    for i, (name, rating) in enumerate(top_players)]
    
    print(tabulate(rankings_data, 
                  headers=['Rank', 'Player', 'Rating'],
                  tablefmt='grid'))
    input("\nPress Enter to continue...")

def show_position_gaps(team):
    clear_screen()
    print("\n=== Position Coverage Gaps ===\n")
    
    gaps = team.get_position_gaps()
    if not gaps:
        print("Good coverage in all positions!")
        return
    
    gap_data = []
    for pos, ratings in gaps.items():
        if ratings:
            avg_rating = sum(ratings) / len(ratings)
            gap_data.append([pos, f"{avg_rating:.1f}", len(ratings)])
        else:
            gap_data.append([pos, "No ratings", 0])
    
    print(tabulate(gap_data, 
                  headers=['Position', 'Avg Rating', 'Rated Players'],
                  tablefmt='grid'))
    
    print("\nNote: Positions shown have average rating below 3.0 or no ratings")
    input("\nPress Enter to continue...")

def view_player_ratings(team):
    while True:
        clear_screen()
        display_player_names(team)
        name = input("Enter player name (or press Enter to exit): ").strip().title()
        
        if not name:  # Exit if user just presses Enter
            break
            
        team.display_player_ratings(name)
        
        input("\nPress Enter to continue...")

def add_new_player(team):
    clear_screen()
    name = input("\nEnter player name (or press Enter to go back): ").strip().title()
    if not name:
        return
        
    if team.get_player(name):
        print(f"\nPlayer '{name}' already exists!")
        input("\nPress Enter to continue...")
        return
            
    team.add_player(name)
    print(f"\nAdded player: {name}")
    rate_player(team, name)  # Pass the name directly to rate_player

def main():
    team = Team("Pro Clubs FC")

    while True:
        choice = display_menu()
        clear_screen()

        if choice == 1:
            add_new_player(team)
            team.save_players()
        elif choice == 2:
            view_player_ratings(team)
        elif choice == 3:
            rate_player(team)
            team.save_players()
        elif choice == 4:
            modify_player_rating(team)  # New option
        elif choice == 5:
            compare_players(team)
        elif choice == 6:
            show_best_lineup(team)
        elif choice == 7:
            show_position_rankings(team)
        elif choice == 8:
            show_position_gaps(team)
        elif choice == 9:  # Changed from 8 to 9
            team.save_players()
            print("Goodbye!")
            break

if __name__ == "__main__":
    main()