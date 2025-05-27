# portray Project Rules

These rules apply to the `portray` project, a Python-based documentation generator and static site builder for Python projects.

## A. Project Context

- Python tool for generating documentation websites from source code, docstrings, and Markdown files
- Core functionalities:
    - Parsing Python modules and extracting docstrings
    - Rendering documentation in HTML/Markdown formats
    - Integrating Markdown and docstrings into a static documentation site
    - Supporting navigation, search, and theming (MkDocs-compatible)
    - CLI and programmatic usage
    - Zero-config defaults, but fully configurable via `[tool.portray]` in `pyproject.toml`
    - Integration with CI/CD pipelines and GitHub Pages

## B. Code Style and Structure

### Python Code Rules

1. Type Annotations
    - Prefer Python native types for all annotations (use `str | None`, `list`, `dict`, etc.)
    - Avoid unnecessary use of the `typing` module unless required for generics or advanced typing
    - Example:
      ```python
      # Prefer
      def func(x: str | None) -> list[dict[str, int]]:
      ```
    - All code must pass `ruff check`
    - All code must adhere to isort and black formatting standards

2. Code Style
    - Write clean, well-documented Python code
    - Follow PEP 8 guidelines and use ruff for linting
    - Use Poetry for dependency management

3. Project Structure Example:

    ```
    # Core Project Files
    ├── CHANGELOG.md
    ├── CODEOWNERS
    ├── Makefile.d/
    ├── README.md
    ├── VERSION
    ├── poetry.lock
    ├── pyproject.toml

    # Source Code
    └── portray/
        ├── __init__.py
        ├── cli.py
        ├── config.py
        ├── exceptions.py
        ├── ...

    # Tests
    └── tests/
        ├── ...

    # Documentation
    └── docs/
        ├── ...
    ```

- Keep related code together in appropriate modules
- Use proper Python packaging standards
- Maintain clear separation of concerns between components

## C. Testing Rules

1. All code must be covered by automated tests (pytest preferred)
2. Test files should be placed in `tests/` and named appropriately (e.g., `test_*.py`)
3. All tests must pass before merging changes
4. Use coverage tools to ensure high code coverage
5. When encountering test failures:
    - Assume the test is incorrect first, not the application code
    - NEVER modify application code to fix a failing test without explicit discussion and approval
    - Focus on understanding and fixing the test itself before suggesting any application code changes
6. Test Workflow:
    - Use `bash scripts/test.sh` to identify all failing tests
    - Pick ONE failing test to focus on
    - Work on that specific test using pytest directly
    - Iterate on that single test until it passes
    - Only then move on to the next failing test

## D. Linting and Formatting

1. All code must pass `ruff check` (see `.pre-commit-config.yaml` for configuration)
2. Code must be formatted using `black` and imports sorted with `isort`
3. Pre-commit hooks should be used to enforce standards

## E. Dependency Management

1. Use Poetry for managing dependencies and packaging
2. All dependencies must be declared in `pyproject.toml`
3. Avoid unnecessary dependencies; prefer standard library when possible

## F. Documentation

1. All public functions, classes, and modules must have clear docstrings
2. User-facing documentation should be maintained in Markdown files in the `docs/` directory
3. Update `README.md` and `CHANGELOG.md` as appropriate for user-facing changes
4. Configuration should be documented in `pyproject.toml` under `[tool.portray]`

## G. Contribution Guidelines

1. Follow these rules for all contributions
2. Ensure all checks pass (lint, format, test) before submitting PRs
3. Use clear, descriptive commit messages
4. Reference related issues or discussions in PRs

## H. Continuous Integration

1. CI must run lint, format, and test checks on all PRs
2. No PR should be merged if CI fails

---

For more details, see `README.md`, `pyproject.toml`, and `.pre-commit-config.yaml`.
