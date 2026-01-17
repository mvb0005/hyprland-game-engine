import unittest
import os

class TestLexigraphMigration(unittest.TestCase):
    def test_controller_files_exist(self):
        """Ensure critical controller files were migrated."""
        base_path = "lexigraph_py/static/controller"
        required_files = ["main.ts", "index.html", "ControllerGrid.ts"]
        
        for f in required_files:
            path = os.path.join(base_path, f)
            self.assertTrue(os.path.exists(path), f"Missing migrated file: {path}")

if __name__ == '__main__':
    unittest.main()
