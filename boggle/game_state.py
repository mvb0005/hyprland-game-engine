import random
import string
import time
import json
import os
from dataclasses import dataclass, field
from typing import List, Dict, Set, Optional, Tuple

# Standard Boggle Die Faces (New Version)
BOGGLE_DICE = [
    "AAEEGN", "ELRTTY", "AOOTTW", "ABBJOO",
    "EHRTVW", "CIMOTU", "DISTTY", "EIOSST",
    "DELRVY", "ACHOPS", "HIMNQU", "EEINSU",
    "EEGHNW", "AFFKPS", "HLNNRZ", "DEILRX"
]

@dataclass
class Player:
    name: str
    score: int = 0
    words: Set[str] = field(default_factory=set)

class BoardGenerator:
    def __init__(self, words_path: str = None):
        self.long_words = []
        if words_path and os.path.exists(words_path):
            with open(words_path, 'r') as f:
                # Filter for long words (8+) for embedding
                self.long_words = [line.strip().upper() for line in f if len(line.strip()) >= 8]
        if not self.long_words:
            self.long_words = ["LEXIGRID", "HYPRLAND", "PYTHONIC", "GHOSTTY", "TERMINAL"]

    def generate(self, width: int, height: int, seed: int = None) -> List[List[str]]:
        if seed:
            random.seed(seed)
        
        # Initialize empty board
        board = [['' for _ in range(width)] for _ in range(height)]
        
        # 1. Embed Long Words
        attempts = (width * height) // 4
        
        for _ in range(attempts):
            word = random.choice(self.long_words)
            self._try_place_word(board, word, width, height)
            
        # 2. Fill Empty with random chars (weighted)
        # Weights roughly based on English frequency
        weights = {
            'E': 12.0, 'A': 8.5, 'R': 7.6, 'I': 7.3, 'O': 7.1, 'T': 6.7, 'N': 6.7, 'S': 5.7,
            'L': 5.5, 'C': 4.5, 'U': 3.6, 'D': 3.4, 'P': 3.2, 'M': 3.0, 'H': 3.0, 'G': 2.5,
            'B': 2.1, 'F': 1.8, 'Y': 1.8, 'W': 1.3, 'K': 1.1, 'V': 1.0, 'X': 0.3, 'Z': 0.3,
            'J': 0.2, 'Q': 0.2
        }
        population = list(weights.keys())
        wgt = list(weights.values())
        
        for y in range(height):
            for x in range(width):
                if not board[y][x]:
                    char = random.choices(population, weights=wgt, k=1)[0]
                    if char == 'Q': char = 'Qu'
                    board[y][x] = char
                    
        return board

    def _try_place_word(self, board, word, width, height) -> bool:
        # Try 10 random starts
        for _ in range(10):
            start_x = random.randint(0, width - 1)
            start_y = random.randint(0, height - 1)
            
            path = [(start_x, start_y)]
            if self._dfs_place(board, word, 1, start_x, start_y, path, width, height, set([(start_x, start_y)])):
                # Success! Commit
                for i, (x, y) in enumerate(path):
                    board[y][x] = word[i]
                return True
        return False

    def _dfs_place(self, board, word, idx, curr_x, curr_y, path, width, height, visited):
        if idx >= len(word):
            return True
            
        all_moves = []
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0: continue
                nx, ny = curr_x + dx, curr_y + dy
                if 0 <= nx < width and 0 <= ny < height:
                    if (nx, ny) not in visited:
                        # Cell must be empty OR match the letter we want
                        if board[ny][nx] == '' or board[ny][nx] == word[idx]:
                           all_moves.append((nx, ny))
        
        random.shuffle(all_moves)
        
        for nx, ny in all_moves:
            path.append((nx, ny))
            visited.add((nx, ny))
            if self._dfs_place(board, word, idx + 1, nx, ny, path, width, height, visited):
                return True
            visited.remove((nx, ny))
            path.pop()
            
        return False

class BoggleGame:
    def __init__(self):
        self.board: List[List[str]] = []
        self.players: Dict[str, Player] = {}
        self.state: str = "LOBBY" # LOBBY, PLAYING, SCORING
        self.timer_end: float = 0
        self.duration: int = 180 # 3 minutes
        self.valid_words: Set[str] = set() 
        
        # Path resolution
        base_dir = os.path.dirname(os.path.abspath(__file__))
        words_path = os.path.join(base_dir, "../../boggle/assets/words_alpha.txt")
        self.generator = BoardGenerator(words_path)
        
    def to_json(self):
        return {
            "board": self.board,
            "players": {name: {"score": p.score, "words": list(p.words)} for name, p in self.players.items()},
            "state": self.state,
            "time_remaining": self.get_time_remaining()
        }

    def generate_board(self, width=5, height=5):
        self.board = self.generator.generate(width, height)
        return self.board

    def to_svg(self) -> str:
        if not self.board:
            return "<svg></svg>"
            
        height = len(self.board)
        width = len(self.board[0])
        # Increase cell size for better visibility
        cell_size = 100 
        padding = 10
        
        svg_width = width * (cell_size + padding) + padding
        svg_height = height * (cell_size + padding) + padding
        
        svg_parts = [
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {svg_width} {svg_height}" style="background: #1e1e2e; width: 100%; height: 100%;">'
        ]
        
        # Style
        svg_parts.append("""
            <style>
                text { font-family: 'JetBrains Mono', monospace; font-weight: bold; fill: #1e1e2e; pointer-events: none; }
                rect { fill: #f5e0dc; rx: 12; ry: 12; stroke: #11111b; stroke-width: 0; transition: all 0.2s; }
                rect:hover { fill: #f9e2af; transform: scale(1.05); transform-origin: center; }
                .cell-container:hover rect { fill: #f9e2af; }
            </style>
        """)
        
        for y in range(height):
            for x in range(width):
                char = self.board[y][x]
                px = padding + x * (cell_size + padding)
                py = padding + y * (cell_size + padding)
                
                # Group for hover effect if needed, but rect:hover works
                svg_parts.append(f'<g class="cell-container">')
                svg_parts.append(f'<rect x="{px}" y="{py}" width="{cell_size}" height="{cell_size}" />')
                
                # Center text
                font_size = 60 if len(char) > 1 else 70
                tx = px + cell_size / 2
                ty = py + cell_size / 2 + (font_size / 3)
                svg_parts.append(f'<text x="{tx}" y="{ty}" font-size="{font_size}" text-anchor="middle">{char}</text>')
                svg_parts.append('</g>')                
        svg_parts.append('</svg>')
        return "".join(svg_parts)

    def start_game(self):

        self.generate_board()
        self.state = "PLAYING"
        self.timer_end = time.time() + self.duration
        # Reset player words for new round
        for p in self.players.values():
            p.words = set()

    def add_player(self, name: str):
        if name not in self.players:
            self.players[name] = Player(name=name)

    def submit_word(self, player_name: str, word: str):
        if self.state != "PLAYING":
            return False
        word = word.upper()
        # Basic validation (length, etc) - Dictionary check skipped for prototype
        if len(word) < 3:
            return False
        
        if player_name in self.players:
            self.players[player_name].words.add(word)
            return True
        return False

    def get_time_remaining(self) -> int:
        if self.state != "PLAYING":
            return 0
        remaining = int(self.timer_end - time.time())
        if remaining <= 0:
            self.state = "SCORING"
            self.score_round()
            return 0
        return remaining

    def score_round(self):
        # Naive scoring: 1 point per word, no unique checks yet
        # Real rules: check uniqueness across all players
        all_words = []
        for p in self.players.values():
            all_words.extend(list(p.words))
            
        from collections import Counter
        counts = Counter(all_words)
        
        for p in self.players.values():
            round_score = 0
            for w in p.words:
                if counts[w] == 1: # Only unique words count in some rules, or all count?
                    # Standard rules: Only words found by ONE player count? 
                    # No, usually duplicates cancel out.
                    # "Any word found by more than one player is disqualified."
                    length = len(w)
                    pts = 0
                    if length == 3 or length == 4: pts = 1
                    elif length == 5: pts = 2
                    elif length == 6: pts = 3
                    elif length == 7: pts = 5
                    elif length >= 8: pts = 11
                    round_score += pts
            
            p.score += round_score

    def to_json(self):
        return {
            "state": self.state,
            "board": self.board,
            "time_remaining": self.get_time_remaining(),
            # Return as dict for TUI compatibility: {name: {score: ..., words: ...}}
            "players": {
                p.name: {"score": p.score, "words": list(p.words)}
                for p in self.players.values()
            }
        }
