"""This module defines CLI interaction when using `portray`.

This is powered by [typer](https://typer.tiangolo.com/) which provides a modern,
type-annotated CLI interface while maintaining 1:1 compatibility with the programmatic API
definition in the [API module](/reference/portray/api)

- `portray as-html`: Renders the project as HTML into the `site` or other specified output directory
- `portray in-browser`: Runs a server with the rendered documentation pointing a browser to it
- `portray server`: Starts a local development server (by default at localhost:8000)
- `portray project-configuration`: Returns back the project configuration as determined by` portray`
- `portray on-github-pages`: Regenerates and deploys the documentation to GitHub pages
"""

import sys
from pprint import pprint
from typing import List, Optional

import typer

from portray import api, logo
from portray._version import __version__


# Create a custom CLI class to handle help display with ASCII art
class PortrayCLI(typer.Typer):
    def __call__(self, *args, **kwargs):
        # Display ASCII art for help commands
        if len(sys.argv) <= 1 or sys.argv[1] in ["-h", "--help"]:
            print(logo.ascii_art)

        return super().__call__(*args, **kwargs)


# Create the main typer application with our custom class
app = PortrayCLI(no_args_is_help=True)


def version_callback(value: bool):
    """Callback for the --version option."""
    if value:
        typer.echo(f"portray version {__version__}")
        raise typer.Exit()


# Add version option to the main app
@app.callback()
def main(
    version: bool = typer.Option(False, "--version", help="Show version and exit", callback=version_callback),
):
    """Your Project with Great Documentation."""
    pass


opt_modules = typer.Option(None, help="One or more modules to render reference documentation for")


@app.command()
def as_html(
    directory: str = typer.Argument("", help="The root folder of your project."),
    config_file: str = typer.Option("pyproject.toml", help="The TOML formatted config file you wish to use."),
    output_dir: str = typer.Option("site", help="The directory to place the generated HTML into."),
    overwrite: bool = typer.Option(
        False,
        help="If set to True any existing documentation output will be removed before generating new documentation.",
    ),
    modules: Optional[List[str]] = opt_modules,
) -> None:
    """Produces HTML documentation for a Python project placing it into output_dir."""
    api.as_html(
        directory=directory, config_file=config_file, output_dir=output_dir, overwrite=overwrite, modules=modules
    )


@app.command()
def project_configuration(
    directory: str = typer.Argument("", help="The root folder of your project."),
    config_file: str = typer.Option("pyproject.toml", help="The TOML formatted config file you wish to use."),
    modules: Optional[List[str]] = opt_modules,
    output_dir: Optional[str] = typer.Option(None, help="The directory to place the generated HTML into."),
) -> None:
    """Returns the configuration associated with a project."""
    config = api.project_configuration(
        directory=directory, config_file=config_file, modules=modules, output_dir=output_dir
    )
    pprint(config)


@app.command()
def server(
    directory: str = typer.Argument("", help="The root folder of your project."),
    config_file: str = typer.Option("pyproject.toml", help="The TOML formatted config file you wish to use."),
    open_browser: bool = typer.Option(
        False, help="If true a browser will be opened pointing at the documentation server"
    ),
    port: Optional[int] = typer.Option(None, help="The port to expose your documentation on (defaults to: 8000)"),
    host: Optional[str] = typer.Option(None, help="The host to expose your documentation on (defaults to 127.0.0.1)"),
    modules: Optional[List[str]] = opt_modules,
    reload: bool = typer.Option(False, help="If true the server will live load any changes"),
) -> None:
    """Runs a development webserver enabling you to browse documentation locally."""
    api.server(
        directory=directory,
        config_file=config_file,
        open_browser=open_browser,
        port=port,
        host=host,
        modules=modules,
        reload=reload,
    )


@app.command()
def in_browser(
    directory: str = typer.Argument("", help="The root folder of your project."),
    config_file: str = typer.Option("pyproject.toml", help="The TOML formatted config file you wish to use."),
    port: Optional[int] = typer.Option(None, help="The port to expose your documentation on (defaults to: 8000)"),
    host: Optional[str] = typer.Option(None, help="The host to expose your documentation on (defaults to 127.0.0.1)"),
    modules: Optional[List[str]] = opt_modules,
    reload: bool = typer.Option(False, help="If true the server will live load any changes"),
) -> None:
    """Opens your default webbrowser pointing to a locally started development webserver."""
    api.in_browser(directory=directory, config_file=config_file, port=port, host=host, modules=modules, reload=reload)


@app.command()
def on_github_pages(
    directory: str = typer.Argument("", help="The root folder of your project."),
    config_file: str = typer.Option("pyproject.toml", help="The TOML formatted config file you wish to use."),
    message: Optional[str] = typer.Option(None, help="The commit message to use when uploading your documentation."),
    force: bool = typer.Option(False, help="Force the push to the repository."),
    ignore_version: bool = typer.Option(
        False, help="Ignore check that build is not being deployed with an old version."
    ),
    modules: Optional[List[str]] = opt_modules,
) -> None:
    """Regenerates and deploys the documentation to GitHub pages."""
    api.on_github_pages(
        directory=directory,
        config_file=config_file,
        message=message,
        force=force,
        ignore_version=ignore_version,
        modules=modules,
    )


if __name__ == "__main__":
    app()
