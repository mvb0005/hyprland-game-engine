import unittest
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from lexigraph_py.game import LexigraphGame
except ImportError:
    LexigraphGame = None

class TestLexigraphInitialization(unittest.TestCase):
    def test_game_class_exists(self):
        """Fail if LexigraphGame class is not implemented."""
        self.assertIsNotNone(LexigraphGame, "LexigraphGame class not found. Has it been implemented?")

    def test_game_initialization(self):
        """Fail if game cannot be initialized with default parameters."""
        if LexigraphGame is None:
            self.fail("Cannot test initialization because LexigraphGame is missing.")
        
        game = LexigraphGame()
        self.assertIsNotNone(game.grid, "Game grid should be initialized")
        self.assertEqual(len(game.players), 0, "New game should have no players")

if __name__ == '__main__':
    unittest.main()
