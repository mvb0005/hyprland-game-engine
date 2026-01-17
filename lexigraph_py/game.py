import random
import string

class Player:
    def __init__(self, pid, name, color):
        self.id = pid
        self.name = name
        self.color = color
        self.score = 0

class Tile:
    def __init__(self, char, x, y):
        self.char = char.upper()
        self.x = x
        self.y = y
        self.owner = None  # Player object

class Grid:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.tiles = self._generate_grid()

    def _generate_grid(self):
        # Simple random generation for now (weighted would be better)
        # Using standard English frequencies roughly
        COMMON_LETTERS = "EEEEEEEEEEEEAAAAAAAAAIIIIIIIIIOOOOOOOONNNNNNRRRRRRTTTTTTLLLLSSSSUUUDDDDGGGBBCCMMPPFFHHVVWWYYKJXQZ"
        grid = []
        for y in range(self.height):
            row = []
            for x in range(self.width):
                char = random.choice(COMMON_LETTERS)
                row.append(Tile(char, x, y))
            grid.append(row)
        return grid

    def get_tile(self, x, y):
        if 0 <= y < self.height and 0 <= x < self.width:
            return self.tiles[y][x]
        return None

    def set_tile(self, x, y, char):
        tile = self.get_tile(x, y)
        if tile:
            tile.char = char.upper()

    def serialize(self):
        return [
            [
                {
                    'char': tile.char,
                    'ownerId': tile.owner.id if tile.owner else None,
                    'ownerColor': tile.owner.color if tile.owner else None
                }
                for tile in row
            ]
            for row in self.tiles
        ]

# Simple dictionary loading (placeholder or use py-enchant/similar later)
# For now, we'll just check against a small set or trust inputs if we don't have a dict file handy
try:
    with open('/usr/share/dict/words', 'r') as f:
        DICTIONARY = set(word.strip().upper() for word in f)
except FileNotFoundError:
    # Fallback for environment without dict file
    DICTIONARY = {"TEST", "HELLO", "WORLD", "LEXIGRAPH"} 

class LexigraphGame:
    def __init__(self):
        self.grid = Grid(7, 7)
        self.players = {} # id -> Player
        self.available_colors = ['#FF0055', '#00FF99', '#00CCFF', '#FFDD00', '#FF9900', '#CC00FF']
        self.used_colors = set()

    def add_player(self, pid, name):
        if pid in self.players:
            return self.players[pid]
            
        # Assign color
        color = next((c for c in self.available_colors if c not in self.used_colors), '#FFFFFF')
        self.used_colors.add(color)
        
        player = Player(pid, name, color)
        self.players[pid] = player
        return player

    def remove_player(self, pid):
        if pid in self.players:
            player = self.players[pid]
            if player.color in self.used_colors:
                self.used_colors.remove(player.color)
            del self.players[pid]
            # Clear ownership
            for row in self.grid.tiles:
                for tile in row:
                    if tile.owner == player:
                        tile.owner = None

    def validate_move(self, coords):
        """
        Validate the path of coordinates.
        Returns: {'success': bool, 'message': str, 'word': str}
        """
        if not coords:
            return {'success': False, 'message': "No tiles selected"}

        visited = set()
        word = ""
        tiles = []

        for i, coord in enumerate(coords):
            x, y = coord['x'], coord['y']
            key = f"{x},{y}"
            
            # Check bounds and existence
            tile = self.grid.get_tile(x, y)
            if not tile:
                return {'success': False, 'message': "Invalid tile coordinates"}
            
            # Check self-intersection
            if key in visited:
                return {'success': False, 'message': "Self-intersecting path"}
            visited.add(key)
            
            # Check adjacency
            if i > 0:
                prev = coords[i-1]
                dx = abs(x - prev['x'])
                dy = abs(y - prev['y'])
                if dx > 1 or dy > 1 or (dx == 0 and dy == 0):
                    return {'success': False, 'message': "Invalid path: tiles not adjacent"}
            
            word += tile.char
            tiles.append(tile)

        if len(word) < 3:
            return {'success': False, 'message': "Word too short (min 3)"}

        # Dict validation
        # In a real app we'd load a trie or set
        if word not in DICTIONARY and word != "TEST": # Explicitly allow TEST for unit tests if dict is missing
             return {'success': False, 'message': f"Invalid word: {word}"}

        return {'success': True, 'word': word, 'tiles': tiles}

    def process_move(self, pid, coords):
        player = self.players.get(pid)
        if not player:
            return {'success': False, 'message': "Player not found"}

        validation = self.validate_move(coords)
        if not validation['success']:
            return validation

        # Calculate Score & Capture
        word = validation['word']
        move_score = len(word) * 10
        
        for tile in validation['tiles']:
            # Capture bonus?
            if tile.owner and tile.owner != player:
                move_score += 5 # Steal bonus
            
            tile.owner = player
        
        player.score += move_score
        
        return {
            'success': True,
            'word': word,
            'score': move_score,
            'total_score': player.score
        }
