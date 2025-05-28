# Portray: Replacing Hug with Typer Implementation Plan

## Implementation Details

#### Detailed Implementation Steps

1. **Analyze Current CLI Structure**:
   - Document exact behavior of hug-based CLI commands
   - Identify all parameters and their defaults
   - Note any special formatting or output handling

2. **Implement Typer Solution**:
   - Create a Typer app to replace hug's CLI interface
   - Maintain identical parameter interfaces for all commands
   - Preserve ASCII art logo and output formatting

3. **Integration**:
   - Replace hug imports and decorators in `portray/cli.py`
   - Test CLI functionality thoroughly
   - Ensure backward compatibility

The migration will be performed in phases to ensure a controlled transition and allow for thorough testing at each stage.

### Phase 1: Replace CLI Implementation (portray/cli.py)

The primary goal of this phase is to replace the `hug`-based CLI with a `typer`-based one, ensuring complete backward compatibility in terms of commands, arguments, and help output.

1. **Setup Typer Application**:
   * In `portray/cli.py`, initialize a `typer.Typer()` app instance (e.g., `app = typer.Typer()`).
   * Configure the main app's help text using `typer.Typer(help="...")` to incorporate `portray.logo.ascii_art`.
   * Add a `--version` option using `typer`'s built-in mechanisms.

2. **Implement `as_html` command**:
   * Define a Python function for the `as_html` command within `portray/cli.py`.
   * Decorate this function with `@app.command()`.
   * Replicate all parameters (arguments and options) from the original `portray.api.as_html` function signature:
     * `directory`: The root folder of your project.
     * `config_file`: The TOML formatted config file you wish to use.
     * `output_dir`: The directory to place the generated HTML into.
     * `overwrite`: If set to True any existing documentation output will be removed before generating new documentation.
     * `modules`: One or more modules to render reference documentation for
   * The command function will call `portray.api.as_html` with the arguments received from `typer`.

3. **Implement `project_configuration` command**:
   * Create a `typer` command function that calls `portray.api.project_configuration`.
   * Ensure its signature matches the original function, with parameters:
     * `directory`: The root folder of your project.
     * `config_file`: The TOML formatted config file you wish to use.
     * `modules`: One or more modules to include in the configuration for reference rendering
     * `output_dir`: The directory to place the generated HTML into.
   * Use `pprint` to display the configuration output, similar to the current implementation.

4. **Implement `server` command**:
   * Create a `typer` command function that calls `portray.api.server`.
   * Ensure its signature matches the original function, with parameters:
     * `directory`: The root folder of your project.
     * `config_file`: The TOML formatted config file you wish to use.
     * `open_browser`: If true a browser will be opened pointing at the documentation server
     * `port`: The port to expose your documentation on
     * `host`: The host to expose your documentation on
     * `modules`: One or more modules to render reference documentation for
     * `reload`: If true the server will live load any changes

5. **Implement `in_browser` command**:
   * Create a `typer` command function that calls `portray.api.in_browser`.
   * Maintain the same parameter interface as the original function.

6. **Implement `on_github_pages` command**:
   * Create a `typer` command function that calls `portray.api.on_github_pages`.
   * Maintain the same parameter interface as the original function, with parameters:
     * `directory`: The root folder of your project.
     * `config_file`: The TOML formatted config file you wish to use.
     * `message`: The commit message to use when uploading your documentation.
     * `force`: Force the push to the repository.
     * `ignore_version`: Ignore check that build is not being deployed with an old version.
     * `modules`: One or more modules to render reference documentation for

7. **Update Entry Point**:
   * Ensure the entry point in `pyproject.toml` correctly points to the `typer.Typer()` instance in `portray/cli.py`.

8. **Update CLI Tests**:
   * If CLI tests exist, adapt them to use `typer.testing.CliRunner`.
   * Update tests to verify:
     * Correct invocation of commands
     * Accurate passing of arguments and options
     * Help output for the main command and each subcommand matches the original

### Phase 2: Review Server Implementation

Unlike pdocs, portray's server functionality doesn't directly use hug but relies on livereload's Server class. This simplifies our migration process.

1. **Review Current Server Implementation**:
   * The `server()` function in `portray/api.py` uses livereload's Server class
   * No direct changes to the server implementation are needed as part of the hug removal

2. **Integration Testing**:
   * Verify that the livereload server works properly when called from the new typer CLI
   * Test with different parameters (host, port, open_browser, etc.)
   * Ensure the livereload functionality still works with the CLI changes

### Phase 3: Testing, Verification, and Documentation

1. **Run Automated Tests**:
   * Execute the complete test suite
   * Fix any issues that arise in CLI-related tests
   * Ensure server functionality works properly with the new CLI

2. **Manual Testing**:
   * **CLI**:
     * Test `portray --help` for overall structure, logo, and command list
     * Test `portray --version`
     * For each command (`as_html`, `in_browser`, `server`, etc.):
       * Test `<command> --help` for correct parameter descriptions
       * Test with valid arguments to ensure correct operation
       * Test with missing required arguments
       * Test with invalid argument values
   * **Server**:
     * Run `portray server [options]`
     * Run `portray in_browser [options]`
     * Access the server from a web browser
     * Verify that documentation pages are served correctly
     * Test the live reload functionality if enabled

3. **Update Documentation**:
   * Review and update `README.md` if any user-facing aspects of the CLI have changed
   * Ensure all help texts within the CLI itself are accurate and clear
   * Update any internal developer documentation regarding the CLI implementation
