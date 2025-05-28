We are working on modernizing this portray project.

We are working on removing the dependency on the `hug` package and using the `typer` package instead to implement the CLI.

## Current State Analysis

The current implementation uses `hug` in two main places:

1. **CLI Implementation**: In `portray/cli.py`, hug is used to create a command-line interface that exposes the following functions from `portray.api`:
   - `as_html`
   - `in_browser`
   - `server`
   - `project_configuration`
   - `on_github_pages`

2. **Server Function**: In `portray/api.py`, the `server()` function does not directly use hug but relies on livereload's Server class for the web server functionality.

## Migration Plan

### Phase 1: Replace CLI Implementation (portray/cli.py)

1. **Create New CLI Implementation with Typer**:
   - Replace the current hug-based CLI with a new Typer-based implementation
   - Ensure all command parameters are preserved exactly as they are
   - Set up the same command structure to maintain backward compatibility

2. **Update Entry Point**:
   - Modify `pyproject.toml` to use the new Typer app if needed

3. **Update Tests**:
   - Adapt any CLI tests to use Typer's testing utilities instead of hug's

### Phase 2: Review Server Function in api.py

1. **Review Server Implementation**:
   - Unlike pdocs, portray's server function uses livereload rather than hug
   - Ensure the Server implementation works with the updated CLI
   - No major changes needed for the server implementation itself

### Phase 3: Testing and Verification

1. **Run Tests**:
   - Run all tests to ensure functionality is maintained
   - Fix any issues that arise

2. **Manual Testing**:
   - Test the CLI commands manually to verify they work as expected
   - Test the server functionality to ensure it still works properly

## Implementation Details

### CLI Implementation

The current CLI is very simple and just registers API functions with hug. Here's how we'll migrate it to Typer:

```python
# Current implementation (hug-based)
import hug
from portray import api, logo

cli = hug.cli(api=hug.API(__name__, doc=logo.ascii_art))
cli(api.as_html)
cli.output(pprint)(api.project_configuration)
cli(api.server)
cli(api.in_browser)
cli(api.on_github_pages)
```

The new implementation will use Typer:

```python
# New implementation (typer-based)
import typer
from pprint import pprint
from typing import Optional, List

from portray import api, logo

app = typer.Typer(help=logo.ascii_art)

@app.command()
def as_html(
    directory: str = typer.Argument("", help="The root folder of your project."),
    config_file: str = typer.Option("pyproject.toml", help="The TOML formatted config file you wish to use."),
    output_dir: str = typer.Option("site", help="The directory to place the generated HTML into."),
    overwrite: bool = typer.Option(False, help="If set to True any existing documentation output will be removed before generating new documentation."),
    modules: Optional[List[str]] = typer.Option(None, help="One or more modules to render reference documentation for"),
) -> None:
    """Produces HTML documentation for a Python project placing it into output_dir."""
    api.as_html(directory=directory, config_file=config_file, output_dir=output_dir, overwrite=overwrite, modules=modules)

@app.command()
def project_configuration(
    directory: str = typer.Argument("", help="The root folder of your project."),
    config_file: str = typer.Option("pyproject.toml", help="The TOML formatted config file you wish to use."),
    modules: Optional[List[str]] = typer.Option(None, help="One or more modules to include in the configuration for reference rendering"),
    output_dir: Optional[str] = typer.Option(None, help="The directory to place the generated HTML into."),
) -> None:
    """Returns the configuration associated with a project."""
    config = api.project_configuration(directory=directory, config_file=config_file, modules=modules, output_dir=output_dir)
    pprint(config)

@app.command()
def server(
    directory: str = typer.Argument("", help="The root folder of your project."),
    config_file: str = typer.Option("pyproject.toml", help="The TOML formatted config file you wish to use."),
    open_browser: bool = typer.Option(False, help="If true a browser will be opened pointing at the documentation server"),
    port: Optional[int] = typer.Option(None, help="The port to expose your documentation on (defaults to: 8000)"),
    host: Optional[str] = typer.Option(None, help="The host to expose your documentation on (defaults to 127.0.0.1)"),
    modules: Optional[List[str]] = typer.Option(None, help="One or more modules to render reference documentation for"),
    reload: bool = typer.Option(False, help="If true the server will live load any changes"),
) -> None:
    """Runs a development webserver enabling you to browse documentation locally."""
    api.server(directory=directory, config_file=config_file, open_browser=open_browser, 
               port=port, host=host, modules=modules, reload=reload)

@app.command()
def in_browser(
    directory: str = typer.Argument("", help="The root folder of your project."),
    config_file: str = typer.Option("pyproject.toml", help="The TOML formatted config file you wish to use."),
    port: Optional[int] = typer.Option(None, help="The port to expose your documentation on (defaults to: 8000)"),
    host: Optional[str] = typer.Option(None, help="The host to expose your documentation on (defaults to 127.0.0.1)"),
    modules: Optional[List[str]] = typer.Option(None, help="One or more modules to render reference documentation for"),
    reload: bool = typer.Option(False, help="If true the server will live load any changes"),
) -> None:
    """Opens your default webbrowser pointing to a locally started development webserver."""
    api.in_browser(directory=directory, config_file=config_file, port=port, 
                  host=host, modules=modules, reload=reload)

@app.command()
def on_github_pages(
    directory: str = typer.Argument("", help="The root folder of your project."),
    config_file: str = typer.Option("pyproject.toml", help="The TOML formatted config file you wish to use."),
    message: Optional[str] = typer.Option(None, help="The commit message to use when uploading your documentation."),
    force: bool = typer.Option(False, help="Force the push to the repository."),
    ignore_version: bool = typer.Option(False, help="Ignore check that build is not being deployed with an old version."),
    modules: Optional[List[str]] = typer.Option(None, help="One or more modules to render reference documentation for"),
) -> None:
    """Regenerates and deploys the documentation to GitHub pages."""
    api.on_github_pages(directory=directory, config_file=config_file, message=message,
                       force=force, ignore_version=ignore_version, modules=modules)

if __name__ == "__main__":
    app()
```

## Example CLI Usage

After migration, the CLI should maintain the same functionality and command structure, but with the improved help formatting and type checking that Typer provides:

```
$ portray --help
                                                                                 
                                                           /███                  
                                                          |  ███                 
                                         /██ /███████     /██████    /███████    
                                        | ██/ ███   ███  |   ███/   /███    ███  
                                        | ███ ███   ███   /███ /███| ███    █████
                                        | ███ ███   ███  /███ |  ███| ███   █████
                                        | ███| ███████ /|  ██████/██| █████████  
                                        | ███| ███  ███ |     ███/███| ███    ███
                                        | ███| ███\  ██ |     ███| ███| ███    ███
                                        | ███| ███ \  ██|     ███| ███| ███    ███
                                        | ███| ███  \  ██     ███| ███| ███    ███
                                        |/    |/     \//      \//  \// | //     \//

Usage: portray [OPTIONS] COMMAND [ARGS]...

  ASCII art logo here

Options:
  --help  Show this message and exit.

Commands:
  as-html              Produces HTML documentation for a Python project placing it into
                       output_dir.
  in-browser           Opens your default webbrowser pointing to a locally started
                       development webserver.
  on-github-pages      Regenerates and deploys the documentation to GitHub pages.
  project-configuration  Returns the configuration associated with a project.
  server               Runs a development webserver enabling you to browse
                       documentation locally.
```

