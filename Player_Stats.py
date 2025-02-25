# Player_Stats.py
import json
from rich.console import Console
from rich.table import Table
from rich import box
from tabulate import tabulate
from collections import defaultdict
from scipy.optimize import linear_sum_assignment
import numpy as np

console = Console()
POSITIONS = ["GK", "LB", "CB", "RB", "CDM", "CM", "LM", "RM", "CAM", "LW", "RW", "ST"]

class Player:
    def __init__(self, name):
        self.name = name
        self.positions = {pos: {'min': 0, 'max': 0, 'votes': []} for pos in POSITIONS}
        
    def to_dict(self):
        return {
            'name': self.name,
            'positions': self.positions
        }
    
    @classmethod
    def from_dict(cls, data):
        player = cls(data['name'])
        player.positions = data.get('positions', {pos: {'min': 0, 'max': 0, 'votes': []} for pos in POSITIONS})
        return player
    
    def add_rating_vote(self, position, min_rating, max_rating, voter):
        """Add a new vote for a position rating"""
        if position not in self.positions:
            raise ValueError(f"Invalid position: {position}")
            
        # Remove previous vote from this voter if exists
        self.positions[position]['votes'] = [v for v in self.positions[position]['votes'] 
                                           if v['voter'] != voter]
        
        # Add new vote
        self.positions[position]['votes'].append({
            'voter': voter,
            'min': min_rating,
            'max': max_rating,
        })
        
        # Update aggregate ratings
        votes = self.positions[position]['votes']
        if votes:
            self.positions[position]['min'] = round(sum(v['min'] for v in votes) / len(votes), 1)
            self.positions[position]['max'] = round(sum(v['max'] for v in votes) / len(votes), 1)

class Team:
    def __init__(self, name):
        self.name = name
        self.players = {}
        self.filename = "players_data.json"
        self.load_players()

    def save_players(self):
        data = {
            'team_name': self.name,
            'players': {name: player.to_dict() for name, player in self.players.items()}
        }
        
        try:
            with open(self.filename, 'w') as f:
                json.dump(data, f, indent=4)
            print("\nPlayers data saved successfully!")
        except Exception as e:
            print(f"\nError saving players data: {e}")
    
    def load_players(self):
        try:
            with open(self.filename, 'r') as f:
                data = json.load(f)
                
            self.name = data.get('team_name', self.name)
            players_data = data.get('players', {})
            
            self.players = {
                name: Player.from_dict(player_data)
                for name, player_data in players_data.items()
            }
            print(f"Loaded {len(self.players)} players from file.")
        except FileNotFoundError:
            print("No saved players data found. Starting with empty team.")
        except Exception as e:
            print(f"Error loading players data: {e}")

    def get_position_gaps(self):
        """Find positions where team lacks strong players (avg rating < 3)"""
        position_ratings = defaultdict(list)
        for player in self.players.values():
            for pos, rating in player.positions.items():
                if rating['max'] > 0:  # Only consider rated positions
                    position_ratings[pos].append(rating['max'])
        
        gaps = {}
        for pos in POSITIONS:
            ratings = position_ratings.get(pos, [])
            if not ratings or sum(ratings) / len(ratings) < 3:
                gaps[pos] = ratings
        return gaps

    def get_best_lineup(self, formation, position_mapping):
        """
        Suggest optimal positions for all players based on formation, prioritizing attacking positions
        and considering side preferences (left/right) based on ratings in nearby positions.
    
        Args:
            formation (str): The formation name (e.g., "4-3-3 attacking")
            position_mapping (dict): Maps formation positions to actual positions
        """
        # Priority order: Attack -> Midfield -> Defense -> Goalkeeper
        position_priority = [
            'ST', 'LW', 'RW', 'CAM',  # Prioritize attacking
            'LM', 'RM', 'CM', 'CDM',  # Midfield
            'CB', 'LB', 'RB',         # Defense
            'GK'                      # Goalkeeper
        ]
    
        # First pass: Create a list of best players for each position
        all_ratings = {}
        for player in self.players.values():
            for formation_key, actual_pos in position_mapping.items():
                rating = player.positions[actual_pos]
                if rating['min'] > 0:  # Only consider rated positions
                    all_ratings[(player.name, formation_key)] = rating['min']

        # Create a list of positions to be filled
        all_positions = list(position_mapping.keys())
        check_positions = all_positions.copy()

        # Create cost matrix for Hungarian algorithm
        cost_matrix = np.zeros((len(all_positions), len(self.players)))

        player_list = list(self.players.values())
        player_names = [player.name for player in player_list]

        # Fill the cost matrix with negative ratings (since we want to maximize)
        for i, pos in enumerate(all_positions):
            for j, player in enumerate(player_list):
                # If player can play this position
                if (player.name, pos) in all_ratings:
                    rating = all_ratings[(player.name, pos)]
                    cost_matrix[i, j] = -rating  # Maximize ratings (thus, negative for minimization)
                else:
                    cost_matrix[i, j] = float('inf')  # Can't assign player to this position
    
        # Add prioritization for the top attacking positions
        for i, pos in enumerate(all_positions):
            # Give higher priority (larger negative value) for top positions
            if pos in position_priority:
                cost_matrix[i] *= 2  # Increase the penalty for not filling top positions (for prioritization)
    
        # Ensure we don't have more positions than players (adjust cost matrix)
        if len(all_positions) > len(player_list):
            # Adjust the cost matrix to avoid index out of bounds
            cost_matrix = cost_matrix[:len(player_list), :]
            all_positions = all_positions[:len(player_list)]

        # Use Hungarian algorithm to find the optimal assignment
        row_ind, col_ind = linear_sum_assignment(cost_matrix)
        lineup = {}
        for i, pos in enumerate(all_positions):
            if i < len(row_ind):
                player = player_names[col_ind[i]]
                rating = -cost_matrix[i, col_ind[i]]
                lineup[pos] = (player, rating)
    
        # If there are still unassigned positions, fill them with "AI"
        for pos in check_positions:
            if pos not in lineup:
                lineup[pos] = ("AI", 0.0)
            player, rating = lineup[pos]  # Unpack the tuple
            if rating > 5:
                lineup[pos] = (player, rating / 2)  # Update the tuple with the new value
    
        # Optimize side assignments (e.g., LCM vs RCM, LB vs RB)
        side_pairs = [
            # Midfield pairs
            ('LCM', 'RCM'), ('LM', 'RM'),
            # Defensive pairs
            ('LB', 'RB'), ('LCB', 'RCB'),
            # Attacking pairs
            ('LW', 'RW')
        ]
    
        for left_pos, right_pos in side_pairs:
            if left_pos in lineup and right_pos in lineup:
                left_player, left_rating = lineup[left_pos]
                right_player, right_rating = lineup[right_pos]
            
                # Get actual player objects (ignore AI players)
                left_player_obj = self.get_player(left_player) if left_player != "AI" else None
                right_player_obj = self.get_player(right_player) if right_player != "AI" else None
            
                # Calculate side preference scores
                left_side_positions = ['LW', 'LM', 'LB']
                right_side_positions = ['RW', 'RM', 'RB']
            
                if left_player_obj and right_player_obj:
                    # Calculate left and right side affinity for both players
                    left_player_left_affinity = sum(left_player_obj.positions[pos]['min'] for pos in left_side_positions)
                    right_player_left_affinity = sum(right_player_obj.positions[pos]['min'] for pos in left_side_positions)

                    left_player_right_affinity = sum(left_player_obj.positions[pos]['min'] for pos in right_side_positions)
                    right_player_right_affinity = sum(right_player_obj.positions[pos]['min'] for pos in right_side_positions)
                    
                    # Compare current vs. swapped alignment
                    current_alignment = left_player_left_affinity + right_player_right_affinity
                    swapped_alignment = right_player_left_affinity + left_player_right_affinity

                    if swapped_alignment > current_alignment:
                        # Swap players if beneficial
                        lineup[left_pos] = (right_player, right_rating)
                        lineup[right_pos] = (left_player, left_rating)

                elif left_player_obj:  # Right position has AI
                    left_affinity = sum(left_player_obj.positions[pos]['min'] for pos in left_side_positions)
                    right_affinity = sum(left_player_obj.positions[pos]['min'] for pos in right_side_positions)
                    
                    if right_affinity > left_affinity:
                        # Move player to right position, AI takes left
                        lineup[right_pos] = (left_player, left_rating)
                        lineup[left_pos] = ("AI", 0.0)

                elif right_player_obj:  # Left position has AI
                    left_affinity = sum(right_player_obj.positions[pos]['min'] for pos in left_side_positions)
                    right_affinity = sum(right_player_obj.positions[pos]['min'] for pos in right_side_positions)

                    if left_affinity > right_affinity:
                        # Move player to left position, AI takes right
                        lineup[left_pos] = (right_player, right_rating)
                        lineup[right_pos] = ("AI", 0.0)

        return lineup

    def compare_players(self, player_names, position=None):
        """Compare specified players across all or specific position"""
        comparisons = []
        players = [self.get_player(name) for name in player_names if self.get_player(name)]
        
        positions_to_compare = [position] if position in POSITIONS else POSITIONS

        for pos in positions_to_compare:
            row = [pos]
            for player in players:
                rating = player.positions[pos]
                rating_str = ''
                if rating['min'] != rating['max']:
                    rating_str = f"{rating['min']}-{rating['max']}"
                else:
                    rating_str = f"{rating['min']}"
                row.append(f"{rating_str}")
            comparisons.append(row)

        return comparisons

    def get_top_players_by_position(self, position, limit=3):
        """Get top rated players for a specific position"""
        players_ratings = []
        for player in self.players.values():
            rating = player.positions[position]
            if rating['max'] > 0:  # Only include rated players
                players_ratings.append((
                    player.name,
                    rating['max'],
                ))
        
        # Sort by rating (desc)
        players_ratings.sort(key=lambda x: (x[1]), reverse=True)
        return players_ratings[:limit]

    def get_player(self, player_name):
        formatted_name = player_name.strip().title()
        return self.players.get(formatted_name)

    def add_player(self, player_name):
        formatted_name = player_name.strip().title()
        if formatted_name not in self.players:
            self.players[formatted_name] = Player(formatted_name)
        return self.players[formatted_name]

    def display_player_ratings(self, player_name):
        player = self.get_player(player_name)
        if not player:
            print(f"Player {player_name} not found!")
            return
        
        # Star characters for rating display
        FILLED_STAR = "★"
        EMPTY_STAR = "✩"
        
        print(f"\n=== Ratings for {player.name} ===\n")
        
        table_data = []
        for pos in POSITIONS:
            rating = player.positions[pos]
            min_stars = FILLED_STAR * int(rating['min'])
            additional_stars = FILLED_STAR * (int(rating['max']) - int(rating['min']))
            empty_stars = EMPTY_STAR * (5 - int(rating['max']))
            rating_str = ''
            if rating['min'] != rating['max']:
                rating_str = f"{rating['min']}-{rating['max']}"
            else:
                rating_str = f"{rating['min']}"
            
            stars = f"{min_stars}\033[91m{additional_stars}\033[0m{empty_stars}"
            votes = len(rating['votes'])
            
            table_data.append([pos, stars, rating_str, f"Votes: {votes}"])
        
        headers = ['Position', 'Rating', 'Vote Count']
        print(tabulate(table_data, headers=headers, tablefmt='grid'))