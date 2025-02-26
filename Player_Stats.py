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
        print(formation)
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

    def get_balanced_lineup(self, formation, position_mapping):
        """
        Generate a balanced lineup that distributes talent across all areas of the field.
        
        Args:
            formation (str): The formation name (e.g., "4-3-3 attacking")
            position_mapping (dict): Maps formation positions to actual positions
        """
        # First, get all player ratings for each position
        all_ratings = {}
        for player in self.players.values():
            for formation_key, actual_pos in position_mapping.items():
                rating = player.positions[actual_pos]
                if rating['min'] > 0:  # Only consider rated positions
                    all_ratings[(player.name, formation_key)] = rating['min']
        
        # Group positions by field area
        field_areas = {
            "defense": ["LB", "RB", "CB", "LCB", "RCB", "LWB", "RWB"],
            "midfield": ["CDM", "CM", "LM", "RM", "LCM", "RCM", "CM1", "CM2"],
            "attack": ["CAM", "ST", "LW", "RW", "ST1", "ST2", "LAM", "RAM"]
        }
        
        # Reverse mapping from formation position to field area
        position_to_area = {}
        for area, positions in field_areas.items():
            for pos in positions:
                position_to_area[pos] = area
        
        # Split positions by area
        positions_by_area = {area: [] for area in field_areas}
        for pos in position_mapping.keys():
            area = next((a for a in field_areas if any(p in pos for p in field_areas[a])), "midfield")
            positions_by_area[area].append(pos)
        
        # Order players by overall average rating
        player_overall_ratings = {}
        for player in self.players.values():
            valid_ratings = [r['min'] for _, r in player.positions.items() if r['min'] > 0]
            if valid_ratings:
                player_overall_ratings[player.name] = sum(valid_ratings) / len(valid_ratings)
        
        sorted_players = sorted(player_overall_ratings.items(), key=lambda x: x[1], reverse=True)
        
        # Allocate the top players evenly across areas
        area_allocations = {area: [] for area in field_areas}
        area_cycle = ["defense", "midfield", "attack"] * (len(sorted_players) // 3 + 1)
        
        for i, (player_name, _) in enumerate(sorted_players):
            if i < len(area_cycle):
                area_allocations[area_cycle[i]].append(player_name)
        
        # Create the lineup
        lineup = {}
        assigned_players = set()
        
        # For each area, assign the allocated players to their best positions
        for area, players in area_allocations.items():
            area_positions = positions_by_area[area]
            player_position_ratings = []
            
            # Get all player-position ratings for this area
            for player_name in players:
                if player_name not in assigned_players:  # Ensure player hasn't been assigned yet
                    for pos in area_positions:
                        if (player_name, pos) in all_ratings:
                            player_position_ratings.append((player_name, pos, all_ratings[(player_name, pos)]))
            
            # Sort by rating (highest first)
            player_position_ratings.sort(key=lambda x: x[2], reverse=True)
            
            # Assign players to positions
            for player_name, pos, rating in player_position_ratings:
                if pos not in lineup and player_name not in assigned_players:
                    lineup[pos] = (player_name, rating)
                    assigned_players.add(player_name)
        
        # Fill any unassigned positions with other players or AI
        remaining_positions = [pos for pos in position_mapping if pos not in lineup]
        remaining_players = [p.name for p in self.players.values() if p.name not in assigned_players]
        
        if remaining_positions:
            # Create a matrix of ratings for remaining players and positions
            remaining_ratings = []
            for player_name in remaining_players:
                for pos in remaining_positions:
                    if (player_name, pos) in all_ratings:
                        remaining_ratings.append((player_name, pos, all_ratings[(player_name, pos)]))
            
            # Sort by rating
            remaining_ratings.sort(key=lambda x: x[2], reverse=True)
            
            # Assign remaining players to positions
            for player_name, pos, rating in remaining_ratings:
                if pos not in lineup and player_name not in assigned_players:
                    lineup[pos] = (player_name, rating)
                    assigned_players.add(player_name)
        
        # Fill any still unassigned positions with AI
        for pos in position_mapping:
            if pos not in lineup:
                lineup[pos] = ("AI", 0.0)
        
        return lineup

    def get_attack_focused_lineup(self, formation, position_mapping):
        """
        Generate an attack-focused lineup that prioritizes placing best players in attacking positions.
        
        Args:
            formation (str): The formation name (e.g., "4-3-3 attacking")
            position_mapping (dict): Maps formation positions to actual positions
        """
        # First, get all player ratings for each position
        all_ratings = {}
        for player in self.players.values():
            for formation_key, actual_pos in position_mapping.items():
                rating = player.positions[actual_pos]
                if rating['min'] > 0:  # Only consider rated positions
                    all_ratings[(player.name, formation_key)] = rating['min']
        
        # Define attacking positions (adjust based on formation)
        attacking_positions = [
            "ST", "ST1", "ST2", "LW", "RW", "CAM", "LAM", "RAM"
        ]
        
        # Calculate player overall ratings (for non-attacking positions)
        player_overall_ratings = {}
        for player in self.players.values():
            valid_ratings = [r['min'] for p, r in player.positions.items() 
                            if r['min'] > 0 and p not in ["ST", "LW", "RW", "CAM"]]
            if valid_ratings:
                player_overall_ratings[player.name] = sum(valid_ratings) / len(valid_ratings)
        
        # Start with attacking positions
        lineup = {}
        attacking_assignments = []
        
        # Get all player ratings for attacking positions
        for player in self.players.values():
            for pos_key in position_mapping:
                if any(attack_pos in pos_key for attack_pos in attacking_positions):
                    actual_pos = position_mapping[pos_key]
                    rating = player.positions[actual_pos]
                    if rating['min'] > 0:
                        attacking_assignments.append((player.name, pos_key, rating['min']))
        
        # Sort attacking assignments by rating
        attacking_assignments.sort(key=lambda x: x[2], reverse=True)
        
        # Assign players to attacking positions
        assigned_players = set()
        for player_name, pos, rating in attacking_assignments:
            if pos not in lineup and player_name not in assigned_players:
                lineup[pos] = (player_name, rating)
                assigned_players.add(player_name)
        
        # Fill remaining positions with other players
        remaining_positions = [pos for pos in position_mapping if pos not in lineup]
        remaining_players = [p.name for p in self.players.values() if p.name not in assigned_players]
        
        # Sort remaining players by overall rating
        sorted_remaining_players = sorted(
            [(player, player_overall_ratings.get(player, 0)) 
            for player in remaining_players],
            key=lambda x: x[1], 
            reverse=True
        )
        
        # Create a cost matrix for remaining assignments
        remaining_ratings = []
        for player_name, _ in sorted_remaining_players:
            for pos in remaining_positions:
                if (player_name, pos) in all_ratings:
                    remaining_ratings.append((player_name, pos, all_ratings[(player_name, pos)]))
        
        # Sort by rating
        remaining_ratings.sort(key=lambda x: x[2], reverse=True)
        
        # Assign remaining players
        for player_name, pos, rating in remaining_ratings:
            if pos not in lineup and player_name not in assigned_players:
                lineup[pos] = (player_name, rating)
                assigned_players.add(player_name)
        
        # Fill any remaining positions with AI
        for pos in position_mapping:
            if pos not in lineup:
                lineup[pos] = ("AI", 0.0)
        
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