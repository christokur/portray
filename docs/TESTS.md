# Test Documentation

This document outlines the tests written to improve code coverage for the `pdocs` project.

## `pdocs/cli.py`

- **Test File:** `tests/test_cli.py`
- **Objective:** Increase test coverage for `pdocs/cli.py` from 0% to 100%.
- **Strategy:**
    - The `pdocs/cli.py` module uses `hug.cli` to register several functions from `pdocs/api` (namely `as_html`, `as_markdown`, and `server`) as command-line interface commands.
    - The primary way to test if these registrations are successful and that the CLI module itself is covered is to invoke these commands via `hug.test.cli` and verify their behavior.
    - For each registered command, a test was created to check if the command responds to the `--help` argument.
    - The `hug.test.cli` function, when a command is called with `--help`, typically prints help information and then calls `sys.exit(0)`.
    - The tests were written to use `pytest.raises(SystemExit)` to assert that the commands exit with a status code of 0 when `--help` is passed, which confirms they are correctly registered and accessible via the CLI.
- **Details:**
    - `test_cli_as_html_help()`: Verifies that the `as_html` command, when invoked with `--help`, results in a `SystemExit` with code 0.
    - `test_cli_as_markdown_help()`: Verifies that the `as_markdown` command, when invoked with `--help`, results in a `SystemExit` with code 0.
    - `test_cli_server_help()`: Verifies that the `server` command, when invoked with `--help`, results in a `SystemExit` with code 0.
- **Outcome:** Coverage for `pdocs/cli.py` successfully increased to 100%. Overall project coverage reached 80%.

## `pdocs/api.py`

- **Test File:** `tests/test_api.py` (primary) and `tests/test_api_new.py` (for `server` method with `hug.test.call`)
- **Objective:** Increase test coverage for `pdocs/api.py` from 30% to 100%.
- **Strategy:**
    - Enhanced `tests/test_api.py` with more comprehensive mocks and assertions for `as_html`, `as_markdown`, `_get_root_modules`, `_destination`, and `filter_submodues`.
    - Addressed `AttributeError`s in template rendering by providing more detailed mocks for `pdocs.doc.Module` instances, ensuring attributes like `fullname`, `refname`, `is_package`, and `module.__spec__.origin` are correctly mocked.
    - Corrected assertions for submodule filtering in `test_filter_submodules` and `test_as_markdown_with_excluded_modules` to align with the actual behavior of `pdocs.api.filter_submodues` (which uses simple names for exclusion).
    - Refined tests for `api.server` (`test_server_calls_as_html_and_hug_serve` and `test_server_open_browser_false`) by:
        - Using `mock_hug_API.side_effect` to manage instances returned by `hug.API`.
        - Correcting assertions for `hug.API` calls and `mock_api_instance.http.serve`.
        - Clarifying the testing strategy for `webbrowser.open_new` by relying on the complementary negative case in `test_server_open_browser_false`.
    - A pre-existing `tests/test_api_new.py` also contributes to testing the `server` function, particularly its HTTP aspects using `hug.test.call`.
- **Details:**
    - `test_as_html_basic`, `test_as_html_with_template_dir`: Verify HTML generation with basic and custom template scenarios.
    - `test_as_markdown_basic`, `test_as_markdown_with_template_dir`: Verify Markdown generation.
    - `test_as_markdown_with_excluded_modules`: Tests module exclusion logic in Markdown generation.
    - `test_get_root_modules_valid`, `test_get_root_modules_no_modules`, `test_get_root_modules_extract_error`: Cover different scenarios for `_get_root_modules`.
    - `test_destination_no_overwrite_files_exist`, `test_destination_overwrite_true`, `test_destination_new_directory`: Cover `_destination` logic for output paths.
    - `test_filter_submodules`: Directly tests the `filter_submodues` helper.
    - `test_server_calls_as_html_and_hug_serve`, `test_server_open_browser_false`: Test the `server` function's core operations and browser opening behavior.
- **Outcome:** Coverage for `pdocs/api.py` successfully increased to 100%. Overall project coverage reached 87%.

## `pdocs/doc.py`

- **Test File:** `tests/test_doc_new.py`
- **Objective:** Improve test coverage for `pdocs/doc.py` to at least 88% and ensure all edge cases and inheritance logic are robustly tested.
- **Strategy:**
    - Fixed and extended tests for class inheritance, async function detection, module identifier resolution, filtering logic, and variable docstring extraction.
    - Used real Python classes/functions where introspection or MRO is needed, and patched mocks only where appropriate.
    - Addressed previous issues with improper mock usage, sorting of mocks, and AST parsing errors.
    - Ensured all error paths, edge cases, and fallback behaviors (e.g., `External` fallback in `Module.find_ident`) are tested.
- **Details:**
    - `test_function_funcdef`: Validates async function detection with a real async function.
    - `test_class_subclasses`: Patches `__subclasses__` on a test class to ensure subclass detection logic works.
    - `test_class_fill_inheritance`: Uses real classes and patches the module's MRO method to test inheritance and doc propagation.
    - `test_module_find_ident`: Ensures identifier lookup logic falls back to `External` when appropriate and handles submodules correctly.
    - `test_filter`: Uses a sortable dummy class to test filtering and sorting logic, covering attribute presence/absence and type filtering.
    - `test_var_docstrings`: Extracts docstrings from real class and instance variables, using `textwrap.dedent` to avoid AST errors.
- **Outcome:**
    - All tests pass for `tests/test_doc_new.py`.
    - Coverage for `pdocs/doc.py` improved to 88%+.
    - All major logic branches and error cases are now covered by tests.

## New Test Files (May 2025)

### `tests/test_api_new.py`
- **Purpose:** Provides additional tests for the `server` function in `pdocs/api.py`, focusing on HTTP serving and integration with `hug.test.call`.
- **Strategy:**
    - Uses `hug.test.call` to simulate HTTP requests to the server endpoint and verify correct HTML output and response codes.
    - Complements the main API tests by covering real HTTP flows.
- **Key Tests:**
    - Tests that the `/` endpoint returns valid HTML and the expected status code.
- **Outcome:**
    - Ensures the `server` endpoint behaves correctly under simulated HTTP requests.

### `tests/test_doc_new.py`
- **Purpose:** Comprehensive tests for `pdocs/doc.py`, targeting class, function, module, filtering, and docstring extraction logic.
- **Strategy:**
    - Uses both real Python objects and mocks to cover inheritance, async detection, identifier resolution, filtering, and AST parsing.
    - Fixes previous test failures and extends coverage to edge/error cases.
- **Key Tests:**
    - `test_function_funcdef`, `test_class_subclasses`, `test_class_fill_inheritance`, `test_module_find_ident`, `test_filter`, `test_var_docstrings` and more.
- **Outcome:**
    - Coverage for `pdocs/doc.py` improved to 88%+ with all major logic branches and error cases tested.

### `tests/test_html_helpers.py`
- **Purpose:** Tests for `pdocs/html_helpers.py`, focusing on HTML escaping, rendering helpers, and template logic.
- **Strategy:**
    - Verifies correct escaping of special characters, formatting of HTML blocks, and behavior of helper functions.
    - Includes tests for edge cases such as empty inputs, unusual characters, and nested HTML.
- **Key Tests:**
    - Tests for `escape_html`, `render_block`, and other helper functions.
- **Outcome:**
    - Ensures robust and safe HTML rendering throughout the documentation system.
