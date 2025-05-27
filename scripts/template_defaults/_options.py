import typer

TEMPLATE_DEFAULTS_OPTIONS = {
    "input": typer.Option(..., "-i", "--input", help="Path to the input file"),
    "output": typer.Option(..., "-o", "--output", help="Path to the output file"),
    "input_type": typer.Option(
        "cookiecutter",
        "-s",
        "--input-type",
        help="Input file type (cookiecutter or cruft)",
    ),
    "output_type": typer.Option(
        "cookiecutter",
        "-t",
        "--output-type",
        help="Output file type (cookiecutter or cruft)",
    ),
    "overrides": typer.Option(
        [],
        "-O",
        "--overrides",
        help="Overrides from the destination for output data.",
    ),
    "extras": typer.Option([], "-e", "--extra", help="Overrides from the destination for output data."),
    "dry_run": typer.Option(False, "--dry-run", help="Show what would be changed without making changes"),
    "verbose": typer.Option(
        0,
        "-v",
        "--verbose",
        count=True,
        help="Increase verbosity (can be used multiple times)",
    ),
    "debug": typer.Option(False, "--debug", help="Enable debug mode"),
}
