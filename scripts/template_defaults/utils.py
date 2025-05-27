"""Utility functions for template-defaults."""

import pathlib
import re
import sys

import typer

from .constants import VERBOSITY_1, VERBOSITY_2, VERBOSITY_3


def resolve_output_path(output_path: pathlib.Path, output_type: str) -> pathlib.Path:
    """Resolve the output path based on the output type.

    Args:
        output_path (pathlib.Path): Path to resolve.
        output_type (str): Type of output file ("cookiecutter" or "cruft").

    Returns:
        pathlib.Path: The resolved output path. If output_path is a directory
            or doesn't exist and has no suffix, appends the appropriate filename:
            - cookiecutter -> cookiecutter.json
            - cruft -> .cruft.json
    """
    if output_path.is_dir() or (not output_path.exists() and not output_path.suffix):
        filename = ".cruft.json" if output_type == "cruft" else "cookiecutter.json"
        return output_path / filename
    return output_path


def validate_types(
    *,
    source_data: dict,
    dest_data: dict,
    dry_run: bool = False,
    verbose: int = 0,
    debug: bool = False,
) -> tuple[dict, dict]:
    """Validate that the types match between source and destination.

    Args:
        source (dict): Source configuration dictionary.
        dest (dict): Destination configuration dictionary.

    Raises:
        SystemExit: If there are type conflicts between source and destination.
    """
    source = {
        k: ",".join(v) if (not k.startswith("_") and isinstance(v, (list, tuple, set))) else v
        for k, v in source_data.items()
    }
    dest = {
        k: ",".join(v) if (not k.startswith("_") and isinstance(v, (list, tuple, set))) else v
        for k, v in dest_data.items()
    }
    check_conflicts(
        dest,
        source,
        dry_run=dry_run,
        debug=debug,
        verbose=verbose,
    )

    return source, dest


def check_conflicts(
    dest: dict,
    source: dict,
    dry_run: bool = False,  # noqa: ARG001
    verbose: int = 0,  # noqa: ARG001
    debug: bool = False,  # noqa: ARG001
) -> None:
    """Check for type conflicts between source and destination."""
    conflicts = []
    for key in set(source.keys()) & set(dest.keys()):
        if type(source[key]) is not type(dest[key]):
            conflicts.append((key, type(source[key]).__name__, type(dest[key]).__name__))
        if not key.startswith("_") and (
            isinstance(source[key], (list, tuple, set)) or isinstance(dest[key], (list, tuple, set))
        ):
            conflicts.append((key, type(source[key]).__name__, type(dest[key]).__name__))
    if conflicts:
        typer.echo("Type conflicts detected:", err=True)
        for key, src_type, dst_type in conflicts:
            typer.echo(f"  Key '{key}': source type={src_type}, destination type={dst_type}", err=True)
        sys.exit(1)


def apply_overrides_and_extras(  # noqa: C901, PLR0912
    merged_data: dict,
    destination_data: dict,
    overrides: list[str],
    extras: list[str],
    dry_run: bool = False,  # noqa: ARG001
    verbose: int = 0,
    debug: bool = False,  # noqa: ARG001
) -> dict:
    """Apply overrides and extras to the merged data.

    Args:
        merged_data (dict): The merged data.
        destination_data (dict): The source data.
        overrides (dict): The overrides to apply.
        extras (dict): The extras to apply.

    Returns:
        dict: The updated merged data.
    """
    import more_itertools

    mdd = {**merged_data}
    # Apply overrides
    if overrides:
        from deepmerge import always_merger

        # overrides = "_manifest"
        overrides_l = [re.split(r"\s*[,;:]\s*", override) for override in overrides]
        if verbose >= VERBOSITY_2:
            typer.echo(f"Overrides: {overrides} == {overrides_l}")
        overrides_l_ = list(more_itertools.flatten(overrides_l))
        if verbose >= VERBOSITY_2 and overrides_l_ != overrides_l:
            typer.echo(f"Overrides: {overrides_l} -> {overrides_l_}")
        overrides_l = overrides_l_
        if verbose >= VERBOSITY_1 and verbose < VERBOSITY_2:
            typer.echo(f"Overrides: {overrides} == {overrides_l}")
        # overrides_l = ["_manifest"]
        overrides_y = 0
        overrides_n = 0
        for override in overrides_l:
            # source_data["_manifest"] or {}
            sd = destination_data.get(override, {})
            if verbose >= VERBOSITY_2:
                typer.echo(f"Override: {override}: {type(sd)}")
            if isinstance(sd, (tuple)):
                sd = list(sd)
            if verbose >= VERBOSITY_3:
                typer.echo(f"Override: {override}: {type(sd)}: {sd}")
            if isinstance(sd, (dict, list, set)):
                # mdd |= source_data["_manifest"] e.g.
                # mdd["poetry_include"] = source_data["_manifest"]["poetry_include"] etc.
                mdd = always_merger.merge(mdd, sd)
                overrides_y += 1
            else:
                typer.echo(f"Override '{override}' is not a dictionary, list, or set. Skipping.", err=True)
                overrides_n += 1
        if verbose >= VERBOSITY_1:
            typer.echo(
                f"Applied {len(overrides_l)} override blocks: {overrides_l}; "
                f"Items: {overrides_y} successful, {overrides_n} skipped.",
            )
    elif verbose >= VERBOSITY_1:
        typer.echo("No overrides to apply.")

    # Apply extras
    if extras:
        if verbose >= VERBOSITY_1:
            typer.echo(f"Extras: {extras}")
        # extras == "key1=vale1,key2=value2"
        extras_l: list[str] = list(more_itertools.flatten([re.split(r"\s*[,;:]\s*", extra) for extra in extras]))
        # extra = "key1=value1"
        extras_d: dict[str, str] = dict([re.split(r"\s*=\s*", extra) for extra in extras_l])
        if verbose >= VERBOSITY_2:
            typer.echo(f"Extras: {extras} == {extras_l} -> {extras_d}")
        for key, val in extras_d.items():
            if verbose >= VERBOSITY_3:
                typer.echo(f"\tExtra: {key}={val}")
            mdd[key] = val
        if verbose >= VERBOSITY_1:
            typer.echo(f"Applied {len(extras_d)} extras.")
    elif verbose >= VERBOSITY_1:
        typer.echo("No extras to apply.")

    return mdd
