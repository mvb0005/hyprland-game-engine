# Coding Standards

This project follows modern Python practices. All AI assistants working on this codebase MUST adhere to these rules.

## 1. Type Hinting
*   **Strict Typing**: All functions, methods, and class attributes must have type hints.
*   **Mypy Compliance**: Code must pass `mypy --strict`.
*   **No `Any`**: Avoid `Any` where possible. Use precise types or `Protocol` for structural typing.

## 2. Style & Linting
*   **Ruff**: Use `ruff` for linting and formatting.
*   **Imports**: Imports must be sorted (Ruff `I` rules).
*   **Line Length**: 100 characters.

## 3. Project Structure
*   **Modules**: Keep logic modular in `engine/`.
*   **Entry Points**: Scripts (like `demo_boggle.py`) should be thin wrappers around engine logic.
*   **Virtual Environment**: Always run within the project's `.venv`.

## 4. Development Workflow
*   **Hot Reloading**: Use the provided `dev.py` script for development to auto-restart on changes.
*   **Clean Slate**: Ensure all window management code handles cleanup (orphaned windows) gracefully.
