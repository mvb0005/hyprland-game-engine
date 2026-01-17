# Structure Specification

To make the repository more user-friendly and organized, we enforce the following structure:

1.  **No loose files in root**: With the exception of `README.md`, `LICENSE`, `pyproject.toml`, configuration files (e.g., `.gitignore`, `*.conf`), and folder roots.
2.  **Scripts**: All shell scripts (`.sh`) and utility scripts must be in `scripts/`.
3.  **Tests**: All test files (`test_*.py`) must be in `tests/` (or within their respective package's `tests/` folder).
4.  **Documentation**: `DESIGN.md`, `STANDARDS.md`, `TODO.md` should be moved to `docs/`.
