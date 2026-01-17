import os
import pytest

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

ALLOWED_ROOT_FILES = {
    "README.md", "LICENSE", "pyproject.toml", ".gitignore", "ghostty_game.conf"
}

def test_root_structure():
    """Fail if there are loose files in root that should be moved."""
    files = [f for f in os.listdir(ROOT_DIR) if os.path.isfile(os.path.join(ROOT_DIR, f))]
    
    violations = []
    for f in files:
        if f in ALLOWED_ROOT_FILES:
            continue
        if f.startswith("."): # hidden files
            continue
        
        # Check specific types that should be moved
        if f.endswith(".sh"):
            violations.append(f"{f} should be in scripts/")
        elif f.endswith(".py"):
            violations.append(f"{f} should be in tests/, scripts/ or a package")
        elif f.endswith(".md") and f not in ALLOWED_ROOT_FILES:
             violations.append(f"{f} should be in docs/")
             
    assert not violations, f"Found structural violations:\n" + "\n".join(violations)
