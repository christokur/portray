#!/usr/bin/env python3  # noqa: N999, EXE001
"""Parse the deployment manifest and return a list of repositories and branches."""

import pathlib
import sys

import toolbag.version
from toolbag.utils.helpers import want_version
from toolbag.utils.template_expander import prepare_template_environment

want_version("python-toolbag", toolbag.version.__version__, ">=0.24.14")

__version__ = "0.26.74"


def parse_repos_and_branches(filename: str) -> str:
    """Parse the deployment manifest and return a list of repositories and branches."""
    # with open(filename, 'r') as file:
    #     yaml_data = yaml.safe_load(file)
    path = pathlib.Path(filename).resolve().absolute()
    search_path = {str(path.parent), str(path.parent.parent), str(pathlib.Path.cwd().resolve().absolute())}
    try:
        yaml_data = prepare_template_environment(
            filename,
            search_path=":".join(search_path),
            kind="environment_manifest",
        )

        deployment_sources = yaml_data["metadata"]["deployment"].get("deployment_sources")
        repositories = (
            deployment_sources["repositories"] if deployment_sources and "repositories" in deployment_sources else {}
        )

        # default_branch = deployment_sources.get("default")

        # Build the output string
        repos_and_branches = []
        for repo, branch in repositories.items():
            repos_and_branches.append(f"{repo}:{branch}")

        return "\n".join(sorted(repos_and_branches))
    except Exception as exc:
        # TRACEBACK_PATTERN_MAIN
        import os

        pytest = any(k for k, _ in os.environ.items() if k.startswith("PYTEST"))
        pycharm = any(k for k, _ in os.environ.items() if k.startswith("PYCHARM"))
        is_debug = not pytest and (pycharm or os.getenv("DEBUG") or "--debug" in sys.argv)
        if is_debug:  # pragma: no cover
            # import sys  # pragma: no cover
            import traceback  # pragma: no cover

            traceback.print_exception(exc.__class__, exc, exc.__traceback__, file=sys.stderr)  # pragma: no cover
        # from toolbag.utils.helpers import to_boolean
        #
        # ignored = exc.__class__.__name__ in ("KeyboardInterrupt", "SystemExit")
        # _capture = not ignored and not is_debug
        # capture = _capture and to_boolean(os.getenv("SENTRY_ENABLED", "true"))
        # if capture:
        #     from sentry_sdk import capture_exception
        #
        #     capture_exception(exc)
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


def main() -> None:
    """Entry point."""
    try:
        filename = sys.argv[1]
    except IndexError:
        print("Usage: repos-and-branches.py <filename>")
        sys.exit(1)
    repos_and_branches = parse_repos_and_branches(filename)
    print(repos_and_branches)


if __name__ == "__main__":
    main()
