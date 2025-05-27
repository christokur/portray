#!/usr/bin/env python3
"""Parse the profiles and accounts information from a file."""
import pathlib
import sys

# import toolbag.version
# from toolbag.utils.helpers import want_version
# from toolbag.utils.template_expander import prepare_template_environment
#
# want_version("python-toolbag", toolbag.version.__version__, ">=0.24.14")
__version__ = "0.26.74"


def parse_profiles_and_accounts(filename: str) -> str:
    """
    Parse the profiles and accounts information from a file.

    Args:
        filename (str): The path to the file containing profiles and accounts information.

    Returns:
        str: A string containing the profiles and accounts information in the format 'repo:branch'.

    Raises:
        SystemExit: If an error occurs during parsing, the function will print the error and exit the program.

    """
    # path = pathlib.Path(filename).resolve().absolute()
    # from collections import OrderedDict
    #
    # search_path = list(
    #     OrderedDict.fromkeys(
    #         [
    #             str(path.parent),
    #             str(path.parent.parent),
    #             str(pathlib.Path.cwd().resolve().absolute()),
    #         ]
    #     )
    # )
    try:
        # yaml_data = prepare_template_environment(
        #     filename,
        #     search_path=":".join(search_path),
        #     kind="environment_manifest",
        # )
        import yaml

        yaml_data = yaml.safe_load(pathlib.Path(filename).read_text())

        profiles_and_accounts = yaml_data["metadata"]["deployment"].get("profiles_and_accounts")
        if not profiles_and_accounts:
            return ""
        # Build the output string
        paca = []
        for prof, acc in profiles_and_accounts.items():
            paca.append(f"{prof}:{acc}")

        return "\n".join(sorted(paca))
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
    """
    Convert string boolean values to actual boolean types in a dictionary or Mash object.

    Args:
        data (dict | Mash): The dictionary or Mash object to process.

    Returns:
        dict: The processed dictionary with string boolean values converted to actual booleans.

    """
    try:
        filename = sys.argv[1]
    except IndexError:
        print("Usage: profiles-and-accounts.py <filename>")
        sys.exit(1)
    profiles_and_accounts = parse_profiles_and_accounts(filename)
    print(profiles_and_accounts)


if __name__ == "__main__":
    main()
