# pdocs Project Rules

These rules apply to the `pdocs` project, a Python-based documentation generator for Python projects.

## A. Project Context

- Python tool for generating project documentation from source code and docstrings
- Core functionalities:
    - Parsing Python modules and extracting docstrings
    - Rendering documentation in HTML/Markdown formats
    - Supporting module/package navigation
    - Customizable templates and themes
    - CLI and programmatic usage
    - Integration with CI/CD pipelines

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
    ├── Makefile
    ├── README.md
    ├── VERSION
    ├── poetry.lock
    ├── pyproject.toml

    # Source Code
    src/
    └── pdocs/
        ├── __init__.py
        ├── __main__.py
        ├── cli.py
        ├── generator.py
        ├── parser.py
        ├── renderer.py
        ├── templates/
        └── utils.py

    # Tests
    tests/
    └── pdocs/
        ├── test_cli.py
        ├── test_generator.py
        ├── test_parser.py
        └── test_renderer.py

    # Documentation
    docs/
    ├── css/
    ├── js/
    └── examples/
    ```

- Keep related code together in appropriate modules
- Use proper Python packaging standards
- Maintain clear separation of concerns between components

## C. Testing Rules

1. When encountering test failures:
    - Assume the test is incorrect first, not the application code
    - Do not modify application code to fix a failing test without explicit discussion and approval
    - Focus on understanding and fixing the test itself before suggesting any application code changes

2. Test Workflow:
    - Use `poe test` or `pytest` to identify failing tests
    - Pick one failing test to focus on
    - Work on that specific test until it passes
    - Only then move on to the next failing test

## D. Development Workflow

- Use Poetry for dependency management
- Run tests with pytest
- Use ruff for linting
- Follow semantic versioning
- Maintain changelog

## E. Documentation

- Maintain clear docstrings for all public functions, classes, and modules
- Keep README up to date
- Document CLI commands and their options
- Include usage examples

## F. Git Usage

### Commit Message Prefixes

- "feat:" for new features
- "fix:" for bug fixes
- "test:" for adding or modifying tests
- "docs:" for documentation updates
- "refactor:" for code refactoring
- "style:" for formatting changes
- "chore:" for maintenance tasks

### Commit Rules

- Use conventional commits format
- Include clear descriptions
- Reference issue numbers when applicable

## G. Error Handling

- Use proper Python exception handling
- Provide clear error messages
- Implement proper logging
- Handle edge cases appropriately

## H. Security

- Follow security best practices
- Handle sensitive data appropriately
- Use secure dependencies
- Implement proper input validation

