import unittest
from game_state import BoggleGame

class TestBoggleLogic(unittest.TestCase):
    def setUp(self):
        self.game = BoggleGame()
        
    def test_board_generation(self):
        board = self.game.generate_board()
        self.assertEqual(len(board), 4)
        self.assertEqual(len(board[0]), 4)
        
        # Check that we have valid letters
        all_chars = [c for row in board for c in row]
        self.assertEqual(len(all_chars), 16)
        
    def test_game_flow(self):
        self.game.add_player("Alice")
        self.game.add_player("Bob")
        
        self.assertEqual(self.game.state, "LOBBY")
        
        self.game.start_game()
        self.assertEqual(self.game.state, "PLAYING")
        self.assertGreater(self.game.timer_end, 0)
        
        # Submission logic
        self.assertTrue(self.game.submit_word("Alice", "TEST"))
        self.assertFalse(self.game.submit_word("Alice", "A")) # Too short
        self.assertFalse(self.game.submit_word("Charlie", "TEST")) # Unknown player
        
        # Check scoring logic
        # Force game end
        self.game.timer_end = 0
        self.game.get_time_remaining() # Triggers scoring
        
        self.assertEqual(self.game.state, "SCORING")
        self.assertEqual(self.game.players["Alice"].score, 1) # "TEST" is 4 chars = 1 pt
        
    def test_unique_scoring(self):
        self.game.add_player("Alice")
        self.game.add_player("Bob")
        self.game.start_game()
        
        # Both find the same word
        self.game.submit_word("Alice", "SHARED")
        self.game.submit_word("Bob", "SHARED")
        
        # Alice finds unique
        self.game.submit_word("Alice", "UNIQUE")
        
        self.game.timer_end = 0
        self.game.score_round()
        
        # If shared words are disqualified (0 pts), scores should reflect that.
        # My implementation currently just counts occurrences.
        # Logic: if counts[w] == 1: score it.
        
        # SHARED count is 2 -> 0 pts
        # UNIQUE count is 1 -> pts
        
        # "UNIQUE" is 6 chars -> 3 pts
        self.assertEqual(self.game.players["Alice"].score, 3)
        self.assertEqual(self.game.players["Bob"].score, 0)

if __name__ == '__main__':
    unittest.main()
