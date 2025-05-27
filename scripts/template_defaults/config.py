"""Configuration handling for template-defaults."""

import pathlib
import sys

import toolbag.version
import typer
from toolbag.utils.helpers import want_version
from toolbag.utils.load_file import load_file
from toolbag.utils.save_file import save_file

want_version("python-toolbag", toolbag.version.__version__, ">=0.26.6")


def load_config(
    *,
    file_path: pathlib.Path,
    input_type: str,
    dry_run: bool = False,  # noqa: ARG001
    verbose: int = 0,  # noqa: ARG001
    debug: bool = False,  # noqa: ARG001
) -> tuple[dict, str]:
    """Load configuration from file.

    Args:
        file_path (pathlib.Path): Path to the configuration file to load.
        input_type (str): Type of input file ("cookiecutter" or "cruft").

    Returns:
        tuple[dict, str]: A tuple containing the loaded configuration data and
            the file type (extension).

    Raises:
        SystemExit: If the file cannot be loaded or has invalid structure.
    """
    if not file_path.exists():
        typer.echo(f"Error: Input file {file_path} not found", err=True)
        sys.exit(1)

    try:
        data = load_file(file_path)
        file_type = file_path.suffix.lstrip(".").lower()  # Store the file type for saving later

        if input_type == "cruft":
            if not isinstance(data, dict) or "context" not in data or "cookiecutter" not in data["context"]:
                typer.echo(f"Error: Invalid cruft file structure in {file_path}", err=True)
                sys.exit(1)
            return data["context"]["cookiecutter"], file_type
        return data, file_type
    except Exception as e:
        typer.echo(f"Error loading {file_path}: {e}", err=True)
        sys.exit(1)


def prepare_output(
    *,
    output_path: pathlib.Path,
    output_type: str,
    dry_run: bool = False,  # noqa: ARG001
    verbose: int = 0,  # noqa: ARG001
    debug: bool = False,  # noqa: ARG001
) -> dict:
    """Prepare output configuration.

    Args:
        output_path (pathlib.Path): Path to the output file.
        output_type (str): Type of output file ("cookiecutter" or "cruft").

    Returns:
        dict: The prepared output configuration data.

    Raises:
        SystemExit: If the output file exists but cannot be loaded.
    """
    if output_path.exists():
        try:
            data = load_file(output_path)
            if output_type == "cruft":
                if not isinstance(data, dict):
                    data = {"context": {"cookiecutter": {}}}
                elif "context" not in data:
                    data["context"] = {"cookiecutter": {}}
                elif "cookiecutter" not in data["context"]:
                    data["context"]["cookiecutter"] = {}
                return data["context"]["cookiecutter"]
            return data
        except Exception as e:
            typer.echo(f"Error loading output file {output_path}: {e}", err=True)
            sys.exit(1)

    if output_type == "cruft":
        return {}
    return {}


def save_config(*, data: dict, output_path: pathlib.Path, output_type: str) -> None:
    """Save configuration to file.

    Args:
        data (dict): Configuration data to save.
        output_path (pathlib.Path): Path where to save the configuration.
        output_type (str): Type of output file ("cookiecutter" or "cruft").

    Raises:
        SystemExit: If there's an error while saving.
    """
    if output_type == "cruft":
        data = {"context": {"cookiecutter": data}}

    try:
        save_file(data, output_path)
    except Exception as e:
        typer.echo(f"Error saving to {output_path}: {e}", err=True)
        sys.exit(1)
