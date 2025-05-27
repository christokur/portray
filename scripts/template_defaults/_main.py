"""Main application logic for template-defaults."""

import os
import pathlib
import sys

import click.exceptions
import typer
from deepmerge import always_merger
from toolbag.datastructures.formatting import jsonify, tomlify, yamlify

from . import config, utils
from ._options import TEMPLATE_DEFAULTS_OPTIONS
from .constants import VERBOSITY_1, VERBOSITY_2, VERBOSITY_3

app = typer.Typer()

VERSION_path = pathlib.Path(__file__).parent.parent.parent / "VERSION"
VERSION = VERSION_path.read_text().strip() if VERSION_path.is_file() else "0.0.0"


@app.command()
def version() -> None:
    """
    Show version information.

    This command displays the current version of the template-defaults application.
    """
    typer.echo(f"template-defaults {VERSION}")


@app.command()
def update(
    input_arg: pathlib.Path = TEMPLATE_DEFAULTS_OPTIONS["input"],
    output: pathlib.Path = TEMPLATE_DEFAULTS_OPTIONS["output"],
    input_type: str = TEMPLATE_DEFAULTS_OPTIONS["input_type"],
    output_type: str = TEMPLATE_DEFAULTS_OPTIONS["output_type"],
    overrides: list[str] = TEMPLATE_DEFAULTS_OPTIONS["overrides"],
    extras: list[str] = TEMPLATE_DEFAULTS_OPTIONS["extras"],
    dry_run: bool = TEMPLATE_DEFAULTS_OPTIONS["dry_run"],
    verbose: int = TEMPLATE_DEFAULTS_OPTIONS["verbose"],
    debug: bool = TEMPLATE_DEFAULTS_OPTIONS["debug"],
) -> None:
    """
    Merge configuration files while maintaining their structure based on type.

    This command merges the configuration files from the input file to the output file,
    preserving the structure based on the input and output types.

    Args:
        input_arg (pathlib.Path): Path to the input file.
        output (pathlib.Path): Path to the output file.
        input_type (str): Input file type (cookiecutter or cruft).
        output_type (str): Output file type (cookiecutter or cruft).
    """
    # Load source configuration
    source_data, file_type = config.load_config(
        file_path=input_arg,
        input_type=input_type,
        dry_run=dry_run,
        debug=debug,
        verbose=verbose,
    )

    # Prepare output structure
    output = utils.resolve_output_path(output, output_type)
    dest_data = config.prepare_output(
        output_path=output,
        output_type=output_type,
        dry_run=dry_run,
        debug=debug,
        verbose=verbose,
    )

    # Validate types before merging
    source_data, dest_data = utils.validate_types(
        source_data=source_data,
        dest_data=dest_data,
        dry_run=dry_run,
        debug=debug,
        verbose=verbose,
    )

    # Merge configurations
    merged_data = {**dest_data}
    merged_data = always_merger.merge(merged_data, source_data)

    if verbose >= 1:
        typer.echo(f"Source file: {input_arg} ({input_type}) - {len(source_data)} keys")
        typer.echo(f"Source type: {input_type}({file_type})")
        typer.echo(f"Destination file: {output} ({output_type}) - {len(dest_data)} keys")
        typer.echo(f"Destination type: {output_type}({file_type})")

    merged_data = utils.apply_overrides_and_extras(
        merged_data,
        dest_data,
        overrides=overrides,
        extras=extras,
        dry_run=dry_run,
        debug=debug,
        verbose=verbose,
    )
    utils.check_conflicts(
        dest=merged_data,
        source=source_data,
        dry_run=dry_run,
        debug=debug,
        verbose=verbose,
    )

    # Calculate diffs
    new_keys = set(merged_data.keys()) - set(dest_data.keys())
    changed_keys = {k for k, v in merged_data.items() if k in dest_data and v != dest_data[k]}

    if verbose >= VERBOSITY_1:
        typer.echo(f"New keys in diff: {len(new_keys)}")
        typer.echo(f"Changed keys in diff: {len(changed_keys)}")

    if verbose >= VERBOSITY_2:
        typer.echo(f"Source keys: {list(source_data.keys())}")
        typer.echo(f"Destination keys: {list(dest_data.keys())}")
        typer.echo(f"New keys in diff: {list(new_keys)}")
        typer.echo(f"Changed keys in diff: {list(changed_keys)}")

    if verbose >= VERBOSITY_3:
        typer.echo("\nSource data:")
        match file_type:
            case "json":
                typer.echo(jsonify(source_data))
            case "toml":
                typer.echo(tomlify(source_data))
            case _:
                typer.echo(yamlify(source_data))

        typer.echo("\nDestination data:")
        match output_type:
            case "json":
                typer.echo(jsonify(dest_data))
            case "toml":
                typer.echo(tomlify(dest_data))
            case _:
                typer.echo(yamlify(dest_data))

        typer.echo(f"New keys in diff: {list(new_keys)}")
        typer.echo(f"Changed keys in diff: {list(changed_keys)}")

    if dry_run:
        typer.echo("Dry run - no changes made")
        return

    # Save the result
    config.save_config(data=merged_data, output_path=output, output_type=output_type)
    typer.echo(f"Successfully merged configurations from {input_arg} to {output}")


def main() -> None:
    """Application entry point.

    This function is the main entry point for the template-defaults application.
    It handles the command-line interface and exception handling.
    """
    try:
        try:
            app(prog_name="template-defaults", standalone_mode=False)
        except click.exceptions.NoSuchOption as exc:
            match exc.option_name:
                case "--version" | "-V":
                    app(prog_name="template-defaults", standalone_mode=False, args=["version"])
                case _:
                    raise exc
    except (
        click.exceptions.NoSuchOption,
        click.exceptions.UsageError,
    ) as exc:  # pylint: disable=broad-exception-caught
        print(str(exc), file=sys.stderr)
        sys.exit(1)
    except Exception as exc:  # pylint: disable=broad-exception-caught
        # TRACEBACK_PATTERN_MAIN
        pytest = any(k for k, _ in os.environ.items() if k.startswith("PYTEST"))
        pycharm = any(k for k, _ in os.environ.items() if k.startswith("PYCHARM"))
        is_debug = not pytest and (pycharm or os.getenv("DEBUG") or "--debug" in sys.argv)
        if is_debug:  # pragma: no cover
            import traceback  # pragma: no cover

            traceback.print_exception(exc.__class__, exc, exc.__traceback__, file=sys.stderr)  # pragma: no cover

        from toolbag.utils.helpers import to_boolean

        ignored = exc.__class__.__name__ in ("KeyboardInterrupt", "SystemExit")
        _capture = not ignored and not is_debug
        capture = _capture and to_boolean(os.getenv("SENTRY_ENABLED", "false"))
        if capture:
            from sentry_sdk import capture_exception

            capture_exception(exc)

        print(f"Unhandled exception: {exc.__class__.__name__}:{exc}; captured: {capture}", file=sys.stderr)
        sys.exit(1)
