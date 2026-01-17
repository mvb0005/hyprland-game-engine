import unittest
from lexigraph_py.game import LexigraphGame, Player, Tile, Grid

class TestLexigraphLogic(unittest.TestCase):
    def setUp(self):
        self.game = LexigraphGame()

    def test_grid_initialization(self):
        """Grid should be 7x7 and populated with letters."""
        self.assertEqual(self.game.grid.width, 7)
        self.assertEqual(self.game.grid.height, 7)
        self.assertIsNotNone(self.game.grid.get_tile(0, 0))
        self.assertIsInstance(self.game.grid.get_tile(0, 0), Tile)

    def test_player_management(self):
        """Adding/Removing players should work and assign colors."""
        p1 = self.game.add_player("id1", "Alice")
        self.assertEqual(p1.name, "Alice")
        self.assertIsNotNone(p1.color)
        
        p2 = self.game.add_player("id2", "Bob")
        self.assertNotEqual(p1.color, p2.color)
        
        self.game.remove_player("id1")
        self.assertNotIn("id1", self.game.players)

    def test_move_validation_adjacency(self):
        """Moves must form a valid adjacent path."""
        # Self-intersection check
        coords = [{'x': 0, 'y': 0}, {'x': 0, 'y': 1}, {'x': 0, 'y': 0}]
        result = self.game.validate_move(coords)
        self.assertFalse(result['success'])
        self.assertIn("Self-intersecting", result['message'])
        
        # Non-adjacent check
        coords = [{'x': 0, 'y': 0}, {'x': 2, 'y': 2}]
        result = self.game.validate_move(coords)
        self.assertFalse(result['success'])
        self.assertIn("not adjacent", result['message'])

    def test_capture_logic(self):
        """Valid moves should change tile ownership."""
        p1 = self.game.add_player("id1", "Alice")
        
        # Force a known word on the grid for testing
        # T E S T
        self.game.grid.set_tile(0, 0, 'T')
        self.game.grid.set_tile(1, 0, 'E')
        self.game.grid.set_tile(2, 0, 'S')
        self.game.grid.set_tile(3, 0, 'T')
        
        coords = [{'x': 0, 'y': 0}, {'x': 1, 'y': 0}, {'x': 2, 'y': 0}, {'x': 3, 'y': 0}]
        
        # Assuming "TEST" is in dictionary (explicitly allowed in game.py fallback)
        result = self.game.process_move("id1", coords)
        self.assertTrue(result['success'], f"Move failed: {result.get('message')}")
        
        # Check ownership
        self.assertEqual(self.game.grid.get_tile(0, 0).owner, p1)
        self.assertEqual(self.game.grid.get_tile(3, 0).owner, p1)
        
        # Check score
        # 4 letters * 10 pts = 40
        self.assertEqual(p1.score, 40)

if __name__ == '__main__':
    unittest.main()
