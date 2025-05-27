

## Implementation Details

#### Detailed Implementation Steps

1. **Analyze Current Server Behavior**:
    - Document exact behavior of hug-based server
    - Identify all configuration options and their effects
    - Note any special request handling or routing

2. **Implement http.server Solution**:
    - Use `http.server.HTTPServer` with custom request handler
    - Maintain same parameter interface as original function
    - Preserve startup behavior (ASCII art, browser opening)

3. **Integration**:
    - Replace hug imports and decorators in `pdocs/api.py`
    - Test server functionality thoroughly
    - Ensure backward compatibility

The migration will be performed in phases to ensure a controlled transition and allow for thorough testing at each stage.

### Phase 1: Replace CLI Implementation (pdocs/cli.py)

The primary goal of this phase is to replace the `hug`-based CLI with a `typer`-based one, ensuring complete backward compatibility in terms of commands, arguments, and help output.

1.  **Setup Typer Application**:
*   In `pdocs/cli.py`, initialize a `typer.Typer()` app instance (e.g., `app = typer.Typer()`).
*   Configure the main app's help text using `typer.Typer(help="...")` or by adding a callback. This should incorporate `pdocs.logo.ascii_art` (if available as a string) and version information. A `--version` option will be added using `typer`'s built-in mechanisms.
2.  **Implement `as_html` command**:
*   Define a Python function for the `as_html` command within `pdocs/cli.py`.
*   Decorate this function with `@app.command(help="Produces HTML formatted output...")`.
*   Replicate all parameters (arguments and options) from the original `pdocs.api.as_html` function signature. This includes names, types, default values, and help texts. `typer.Argument(...)` and `typer.Option(...)` will be used. Help texts for parameters will be sourced from the original function's docstrings or observed `hug` behavior.
*   The command function will import and call `pdocs.api.as_html` with the arguments received from `typer`.
3.  **Implement `as_markdown` command**:
*   Similar to the `as_html` command, create a `typer` command function that calls `pdocs.api.as_markdown`.
*   Ensure its signature and help text match the `hug` version (`@app.command(help="Produces Markdown formatted output...")`).
4.  **Implement `server` command**:
*   Similar to the `as_html` command, create a `typer` command function that calls `pdocs.api.server`.
*   Ensure its signature and help text match the `hug` version (`@app.command(help="Runs a development webserver...")`).
*   **Note**: In this phase, this `typer` command will still invoke the *existing* `hug`-based `pdocs.api.server` function. The internal rewrite of `pdocs.api.server` is deferred to Phase 2.
5.  **Update Entry Point**:
*   Ensure the `pyproject.toml` script entry point `pdocs = "pdocs.cli:app"` correctly points to the `typer.Typer()` instance in `pdocs/cli.py`.
6.  **Update CLI Tests**:
*   Adapt `tests/test_cli.py` to use `typer.testing.CliRunner`.
*   Update tests to verify:
    *   Correct invocation of subcommands.
    *   Accurate passing of arguments and options to the underlying API functions.
    *   Help output for the main command and each subcommand (`pdocs --help`, `pdocs as_html --help`, etc.) matches the `hug` version's structure and content.
    *   Version output (`pdocs --version`).
    *   Error handling for missing/invalid arguments matches or improves upon `hug`'s behavior.

### Phase 2: Update Server Function in api.py

This phase focuses on removing the `hug` dependency from the `pdocs.api.server` function by reimplementing its web server functionality using Python's standard `http.server` module.

1.  **Analyze Current `pdocs.api.server` Behavior**:
*   Based on answers to clarifying questions, document the exact behavior of the `hug`-based server:
    *   Default and configurable host/port.
    *   Mechanism for specifying the directory to serve (e.g., from CLI arguments passed to `api.server`).
    *   Content serving logic (e.g., `index.html` resolution, MIME types).
    *   Any live-reload or dynamic regeneration features (if any).
    *   Specific routes or custom request handling.
2.  **Implement `http.server`-based Solution**:
*   In `pdocs/api.py` (or a new helper module like `pdocs/webserver.py` if the logic is substantial), create a new server implementation.
*   Use `http.server.HTTPServer` and a custom request handler class derived from `http.server.SimpleHTTPRequestHandler` or `http.server.BaseHTTPRequestHandler`.
*   The custom handler will be responsible for serving files from the specified documentation output directory.
*   Ensure the new server can be configured with host, port, and the directory to serve, based on parameters passed to the `pdocs.api.server` function.
3.  **Integrate New Server into `pdocs.api.server`**:
*   Modify the `pdocs.api.server` function in `pdocs/api.py`.
*   Remove all `hug`-related code for server setup and request handling.
*   Instantiate and run the new `http.server`-based implementation, passing necessary configurations (host, port, directory) received from its function arguments (which are, in turn, passed by the `typer` CLI command).

### Phase 3: Testing, Verification, and Documentation

1.  **Run Automated Tests**:
*   Execute the complete test suite (`pytest` or equivalent).
*   Fix any issues that arise in `tests/test_cli.py` or any tests related to the server functionality.
*   If server-specific tests exist, adapt them to test the new `http.server` implementation (e.g., by making HTTP requests to `localhost` and verifying responses). If they don't exist, consider adding basic tests for the server.
2.  **Manual Testing**:
*   **CLI**:
    *   Test `pdocs --help` for overall structure, logo, and command list.
    *   Test `pdocs --version`.
    *   For each command (`as_html`, `as_markdown`, `server`):
    *   Test `<command> --help` for correct parameter descriptions.
    *   Test with valid arguments to ensure correct operation.
    *   Test with missing required arguments.
    *   Test with invalid argument values.
    *   Verify output (generated files for `as_html`/`as_markdown`, server startup messages for `server`).
*   **Server**:
    *   Run `pdocs server [options]` (e.g., specifying a custom port or output directory if supported).
    *   Access the server from a web browser.
    *   Verify that documentation pages are served correctly.
    *   Check for 404 errors for non-existent pages.
    *   Confirm any specific behaviors (like serving `index.html` for a directory request) are maintained.
3.  **Update Documentation**:
*   Review and update `README.md` if any user-facing aspects of the CLI have changed (though the goal is 100% backward compatibility).
*   Ensure all help texts within the CLI itself (main help, command help, argument help) are accurate, clear, and match the previous `hug` output as closely as possible.
*   Update any internal developer documentation regarding the CLI or server implementation.

#### Automated Testing
1. **Update Test Suite**:
    - Convert all hug-based tests to typer equivalents
    - Add new tests for edge cases
    - Ensure test coverage is maintained or improved

2. **Integration Testing**:
    - Test complete CLI workflows
    - Verify server functionality with real documentation generation
    - Test error handling scenarios

#### Manual Testing Checklist
1. **CLI Commands**:
    - `pdocs --help` - verify structure, logo, and command list
    - `pdocs --version` - verify version display
    - `pdocs as-html --help` - verify parameter descriptions
    - `pdocs as-markdown --help` - verify parameter descriptions
    - `pdocs server --help` - verify parameter descriptions
    - Test each command with valid arguments
    - Test error handling for invalid arguments

2. **Server Functionality**:
    - Start server with default settings
    - Start server with custom host/port
    - Verify documentation pages are served correctly
    - Test 404 handling for non-existent pages
    - Verify browser auto-opening (if enabled)

#### Cleanup and Documentation
1. **Remove hug Dependency**:
    - Update `pyproject.toml` to remove hug
    - Verify no remaining hug imports in codebase
    - Update lock files

2. **Update Documentation**:
    - Review and update README.md if needed
    - Ensure help texts are accurate and complete
    - Update any developer documentation

## Risk Assessment and Mitigation

### Low Risk
- **CLI parameter compatibility**: Typer auto-detects from function signatures
- **Basic command registration**: Straightforward typer functionality
- **Test updates**: Well-documented typer testing approach

### Medium Risk
- **ASCII art integration**: May require callback function approach
- **Server implementation**: http.server has different capabilities than hug
- **Error handling consistency**: Different error patterns between frameworks

**Mitigation**: Extensive testing and comparison with original behavior

### High Risk
- **Complex server features**: Potential for missing hug-specific functionality
- **Performance differences**: http.server may perform differently

**Mitigation**: Thorough analysis of current server behavior before implementation

## Success Criteria

1. ✅ All existing CLI commands work identically
2. ✅ Server functionality maintains same behavior
3. ✅ All tests pass with updated testing framework
4. ✅ No new dependencies added beyond typer
5. ✅ Performance equivalent or better
6. ✅ ASCII art displays correctly in help output
7. ✅ Help text functionality preserved
8. ✅ Error handling matches or improves original behavior

## Rollback Plan

1. **Maintain hug dependency** during development and testing
2. **Create feature branch** for all migration work
3. **Extensive testing** before removing hug from dependencies
4. **Document any differences** found during testing for future reference

## Implementation Notes

- **Function Signatures**: Keep API function signatures unchanged to ensure parameter compatibility
- **Testing Priority**: Focus on CLI compatibility first, then server functionality
- **Incremental Approach**: Complete Phase 1 fully before starting Phase 2
- **Performance Monitoring**: Compare performance before/after migration
- **Error Handling**: Document any differences in error behavior between hug and typer

## Example CLI Usage (Target Output)

The new typer implementation should produce output identical to the original:

