#!/usr/bin/env python3  # noqa: N999
"""Expand a manifest file with Jinja2 templates."""
from __future__ import annotations

import argparse
import os
import pathlib
import sys

import toolbag.version
from toolbag.datastructures import yamlify
from toolbag.utils.helpers import to_boolean, want_version
from toolbag.utils.template_expander import prepare_template_environment

want_version("python-toolbag", toolbag.version.__version__, ">=0.26.19")

__version__ = "0.26.74"

# Set up argument parsing
parser = argparse.ArgumentParser(description="Expand a manifest file with Jinja2 templates.")
parser.add_argument("filename", help="The manifest file to expand")
parser.add_argument("--search-path", "-s", help="Additional search paths for templates (colon-separated)")
args = parser.parse_args()

path = pathlib.Path(args.filename).resolve().absolute()
if not path.exists():
    sys.stderr.write(f"File not found: {args.filename} (cwd: {pathlib.Path.cwd()})")
    sys.exit(2)

# Default search paths
search_paths = [
    str(path.parent),
    str(path.parent.parent),
    str(pathlib.Path.cwd().resolve().absolute()),
]

# Add user-provided search paths if specified
if args.search_path:
    # Prepend user paths so they take precedence
    user_paths = args.search_path.split(":")
    search_paths = user_paths + search_paths

print(f"Search paths: {':'.join(search_paths)}")

try:
    yaml_data = prepare_template_environment(
        args.filename,
        search_path=":".join(search_paths),
        kind="application_manifest",
    )

    print(yamlify(yaml_data.__dict__))
except Exception as exc:
    pytest = any(k for k, _ in os.environ.items() if k.startswith("PYTEST"))
    pycharm = any(k for k, _ in os.environ.items() if k.startswith("PYCHARM"))
    is_debug = not pytest and (pycharm or to_boolean(os.getenv("DEBUG", "true")))
    if is_debug:
        import traceback

        traceback.print_exception(exc.__class__, exc, exc.__traceback__)
    sys.stderr.write(f"Exception: {exc}")
    sys.stderr.write(f"Search path: {search_paths}")
    sys.exit(3)
