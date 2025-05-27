#!/usr/bin/env python3  # noqa: N999, EXE001
"""Synchronize environment branches with a target branch.

This script synchronizes environment branches in a git repository with a target branch,
typically 'main' or 'master'. It handles manifest updates and supports worktrees.

Features:
- Syncs environment branches with target branch
- Updates manifest files
- Supports git worktrees
- Dry run mode for safe testing
- Verbose output for debugging
- Compare remote and local branches before sync
- Delete local branches that don't exist on remote

Usage:
    python sync-environment-branches.py <target-branch> [options]

Options:
    --dry-run            Show what would be done without making changes
    -v, --verbose       Increase verbosity (can be used multiple times)
    --debug             Enable debug mode with full tracebacks
    --sync/--no-sync    Compare and sync remote branches (default: enabled)
    --prune             Delete local branches that don't exist on remote

Environment Variables:
    DEBUG               If set, enables debug mode with full tracebacks

Example:
    python sync-environment-branches.py main --dry-run -v
"""
import contextlib
import io
import os
import pathlib
import re
import sys

import backoff
import git
import packaging.specifiers
import packaging.version
import typer
from git import GitCommandError
from toolbag.datastructures.formatting import yamlify
from toolbag.datastructures.mash import Mash
from toolbag.utils.errors import ToolbagFileError
from toolbag.utils.load_file import load_stream_structured

__version__ = "0.26.74"

WORKTREES_COLUMN_COUNT = 3
MFT_MIN_LEN = 2
SEGMENTS = 4

APP_MANIFEST_VERSION = "0.5.1"
VERSION = pathlib.Path("VERSION").read_text().strip()

# CLI Options
SYNC_OPTIONS = {
    "target": typer.Argument(
        ...,
        help="Target branch to sync with",
        show_default=False,
    ),
    "dry_run": typer.Option(
        False,
        "--dry-run",
        help="Show what would be done without making changes",
    ),
    "verbose": typer.Option(
        0,
        "-v",
        "--verbose",
        count=True,
        help="Increase verbosity (can be used multiple times)",
    ),
    "debug": typer.Option(
        False,
        "--debug",
        help="Enable debug mode",
    ),
    "sync": typer.Option(
        True,
        "--sync/--no-sync",
        help="Compare and sync remote branches (default: enabled)",
    ),
    "prune": typer.Option(
        False,
        "--prune",
        help="Delete local branches that don't exist on remote",
    ),
}

DEFAULT_MANIFESTS = [
    Mash(
        {
            "name": "client",
            "version": APP_MANIFEST_VERSION,
        },
    ),
    Mash(
        {
            "name": "ldx",
            "version": APP_MANIFEST_VERSION,
        },
    ),
]
DEFAULT_COMPATIBILITY = Mash(
    {
        "application-manifest": f">={APP_MANIFEST_VERSION}",
        "b2b": ">=0.34.24",
        "environment": ">=0.32.4",
    },
)
DEFAULT_DEPLOYMENT_TEMPLATES = [
    "ldx-namespaces",
    "ldx-applicationset",
    "ldx-helm",
    "ldx-values",
    "ldx-sinks",
    "ldx-postgres-hack",
    "ldx-database-admin",
    "client-baccarat",
    "client-fablackjack",
    "client-roulettes",
]
EXTRA_DEPLOYMENT_TEMPLATES = [
    "ldx-database-admin",
]
REPOS_AND_BRANCHES_TXT = "cicd/rc/repos_and_branches.txt"
#
# features:
#   database-admin:
#     enabled: true
#     kustomize_version: v0.5.0
#     version: '{ldx.features.version}'
#     is_deployment: false
#   reset:
#     edge: false
#     enabled: false
#     studio: false
#     version: '{ldx.version}'
#
FEATURE_DATABASE_ADMIN = {
    "enabled": "true",
    "kustomize_version": "v0.5.0",
    "version": "{ldx.features.version}",
}
FEATURE_RESET = {
    "enabled": False,
    "edge": False,
    "studio": False,
    "version": "'{ldx.version}'",
}

THROTTLED_BACKOFF_MAX_TIME = 5
THROTTLED_BACKOFF_MAX_TRIES = 3


def write_file(file: str, text: str) -> None:
    """
    Write the given text to a file.

    Args:
        file (str): The path to the file to write.
        text (str): The content to write to the file.

    Returns:
        None

    """
    pathlib.Path(file).write_text(text)


def read_file(file: pathlib.Path | str) -> str:
    """
    Read the content of a file.

    Args:
        file (str): The path to the file to read.

    Returns:
        str: The content of the file.

    Raises:
        typer.Exit: If the file contains unresolved merge conflicts.
        Exception: If there is an error reading the file.
    """
    try:
        path = pathlib.Path(file) if isinstance(file, str) else file
        manifest = path.read_text()

        if (
            "<<<<<<<" in manifest
            and ">>>>>>>" in manifest
            and "=======" in manifest
            and str(path.resolve()) != __file__
        ):
            typer.echo(f"Unmerged file: {file}", err=True)
            raise typer.Exit(1)
        return manifest
    except Exception as exc:
        typer.echo(f"Failed to read {file}: {exc}", err=True)
        raise exc


def convert_booleans(data: dict | Mash) -> dict:
    """Convert string boolean values to actual boolean types in a dictionary or Mash object.

    Recursively traverses the dictionary and converts string values 'true' and 'false'
    to their corresponding boolean values. This is useful for handling YAML files where
    boolean values may be parsed as strings.

    Args:
        data: The dictionary or Mash object to process. Can contain nested dictionaries.

    Returns:
        dict: The processed dictionary with string boolean values converted to actual booleans.
    """
    if not isinstance(data, (dict, Mash)):
        return data
    for key, value in data.items():
        if isinstance(value, (dict, Mash)):
            data[key] = convert_booleans(value)
        elif isinstance(value, (list, tuple)):
            data[key] = [convert_booleans(item) for item in value]
        elif isinstance(value, (str,)):
            v = value.lower()
            if v == "true":
                data[key] = True
            elif v == "false":
                data[key] = False
            else:
                data[key] = value
    return data


def parse_repos_and_branches(filename: str) -> dict | None:
    """
    Parse the repository and branch information from a file.

    Args:
        filename (str): The path to the file containing repository and branch information.

    Returns:
        dict | None: A dictionary mapping repository names to branch names, or None
        if the file contains deprecated information.

    Raises:
        FileNotFoundError: If the specified file does not exist.
        ToolbagFileError: If the file contains invalid lines.

    """
    file_path = pathlib.Path(filename)
    if not file_path.exists():
        typer.echo(f"File '{filename}' does not exist.", err=True)
        raise FileNotFoundError(filename)

    lines = file_path.read_text().splitlines()

    if any(line for line in lines if "deprecated" in line.lower()):
        return None

    repos_and_branches = {}
    for line in lines:
        values = line.strip().split(":")
        match len(values):
            case 2:
                repo, branch = values
            case _:
                raise ToolbagFileError(f"Invalid line: {line}")
        repos_and_branches[repo.strip()] = branch.strip()

    return repos_and_branches


def validate_manifest(data: Mash, spec: packaging.specifiers.SpecifierSet) -> tuple[list, list]:
    """Validate manifest data against version specifications.

    Validates each manifest in the data against version requirements and naming conventions.
    A manifest is considered valid if it:
    1. Has at least MFT_MIN_LEN fields
    2. Has a non-numeric name
    3. Has a valid semantic version number
    4. Version matches the specified version constraints

    Args:
        data: Mash object containing manifests to validate
        spec: Version specifier to validate manifest versions against

    Returns:
        tuple: Contains:
            - list: Valid manifests meeting all criteria
            - list: Invalid manifests that failed validation
    """
    good_manifests = [
        mft
        for mft in data.manifests
        if len(mft) >= MFT_MIN_LEN
        and not re.match(r"^(\d+\.?)+$", mft.get("name", ""))
        and re.match(r"^(\d+\.?)+$", mft.get("version", ""))
        and spec.contains(mft.version)
    ]

    bad_manifests = [
        mft
        for mft in data.manifests
        if len(mft) < MFT_MIN_LEN or re.match(r"^(\d+\.?)+$", mft.get("name", APP_MANIFEST_VERSION))
    ]

    return good_manifests, bad_manifests


def process_ldx_features(data: Mash) -> None:
    """Process LDX-specific features in manifest data.

    Handles special feature flags and configurations for LDX:
    1. Removes deprecated database_reset settings
    2. Initializes default feature configuration if missing
    3. Sets up reset feature with safe defaults

    Args:
        data: Mash object containing LDX configuration
    """
    # Data reset feature; OFF by default and remove old implementation
    for tier in ("edge", "studio"):
        if data.get("ldx", {}).get(tier, {}).get("database_reset", None) is not None:
            with contextlib.suppress(KeyError):
                del data.ldx[tier]["database_reset"]

    if data.get("ldx", {}) and data.ldx.get("features", None) is None:
        with contextlib.suppress(KeyError):
            data.ldx.features = Mash(
                {
                    "is_deployment": False,
                    "reset": {
                        "enabled": False,
                        "edge": False,
                        "studio": False,
                        "version": "{ldx.version}",
                    },
                },
            )


def process_deployment_templates(metadata: Mash) -> None:
    """Process deployment templates in metadata.

    Validates and normalizes deployment template configuration:
    1. Ensures deployment_templates is a list
    2. Validates all entries are strings
    3. Adds required templates from EXTRA_DEPLOYMENT_TEMPLATES
    4. Removes duplicates and sorts the final list

    Args:
        metadata: Mash object containing deployment configuration

    Raises:
        ValueError: If deployment_templates is not a list
    """
    if dtpls := metadata.get("deployment", {}).get("deployment_templates", []):
        if not isinstance(dtpls, (list, tuple)):
            raise ValueError(
                f"deployment_templates is not a list: {metadata.deployment.deployment_templates.__class__}",
            )
        try:
            non_string = []
            are_string = []
            for entry in metadata.deployment.deployment_templates:
                if isinstance(entry, str):
                    are_string.append(entry)
                else:
                    non_string.append(entry)
            if set(EXTRA_DEPLOYMENT_TEMPLATES) - set(are_string):
                are_string.extend(EXTRA_DEPLOYMENT_TEMPLATES)
                deployment_templates = sorted(set(are_string))
                deployment_templates.extend(non_string)
                # metadata.deployment.deployment_templates = deployment_templates
        except Exception as exc:
            raise exc


def fix_manifest(  # noqa: C901
    file: str,
    repo: git.Repo,
    target: str | None = None,
    verbose: int = 0,
    dry_run: bool = False,
) -> str:
    """
    Fix and update the manifest file for the given repository.

    This function reads the manifest file, validates and updates its content,
    and commits the changes to the repository.

    Args:
        file (str): The path to the manifest file.
        repo (git.Repo): The git repository object.
        target (str | None): The target branch name.

    Returns:
        str: The updated manifest content.

    Raises:
        Exception: If there is an error while processing the manifest file.
    """
    try:
        is_ldx = not any(name for name in ["assets"] if name in file)
        manifest = read_file(file)
        fh = io.StringIO(manifest)
        data = Mash(load_stream_structured(file, fh, hint="yaml"))
        data.manifests = data.get("manifests", DEFAULT_MANIFESTS)

        # Validate manifests
        spec = packaging.specifiers.SpecifierSet(f">={APP_MANIFEST_VERSION}")
        good_manifests, bad_manifests = validate_manifest(data, spec)

        if good_manifests and verbose:
            typer.echo(f"Good manifests: {good_manifests}")

        # Handle LDX specific logic
        if is_ldx:
            if bad_manifests:
                typer.echo(f"Bad manifests: {bad_manifests}", err=True)
                data.manifests = DEFAULT_MANIFESTS
            for mft in data.manifests:
                if not spec.contains(mft.version):
                    mft.version = APP_MANIFEST_VERSION

        # Process metadata
        metadata = data.get("metadata", Mash())
        with contextlib.suppress(KeyError):
            del metadata["compatibility"]

        short_name = pathlib.Path(file).stem.split("--", 4)
        short_name = f"{short_name[1]}{short_name[2]}"

        if is_ldx:
            process_ldx_features(data)

            metadata.deployment = metadata.get(
                "deployment",
                Mash(
                    {
                        "application_name": f"live-dealer-{short_name}",
                        "deployment_templates": DEFAULT_DEPLOYMENT_TEMPLATES,
                        "project_name": "live-dealer",
                    },
                ),
            )

            process_deployment_templates(metadata)

        metadata.notes = [
            """"updated:" only interpreted by humans or used to trigger a deployment run""",
            "date -Iseconds | tr -d '\\n' | pbcopy",
        ]
        metadata.version = VERSION

        if metadata.get("deployment_sources", None):
            del metadata["deployment_sources"]

        data.metadata = metadata

        # Write all changes back to the manifest
        unspecial = {key: sect for key, sect in data.items() if key not in ("metadata", "manifests")}
        text = yamlify(convert_booleans(unspecial))
        if "manifests" in data:
            text += yamlify({"manifests": convert_booleans(data.manifests)})
        text += yamlify({"metadata": convert_booleans(data.metadata)})

        if not dry_run:
            write_file(file, text)
        run_git(repo, "add", file, target=target)
        run_git(repo, "commit", f"--message='Sync {file} to {target}'", "--no-verify", target=target)
        return text

    except Exception as exc:
        typer.echo(f"Failed to fix {file}: {exc}", err=True)
        raise exc


class GitBackoff:
    """Git operation retry handler with exponential backoff.

    Provides retry functionality for git operations that may fail transiently.
    Uses exponential backoff to gradually increase wait time between retries.
    Includes callbacks for monitoring retry status and handling failures.
    """

    @classmethod
    def _on_success(cls: type, details: dict) -> None:
        """Handle successful git operation after retry.

        Args:
            details: Dictionary containing retry attempt details:
                elapsed: Total time elapsed
                tries: Number of attempts made
                target: Function that was called
                args: Arguments passed to function
                kwargs: Keyword arguments passed to function
        """

    @classmethod
    def _on_backoff(cls: type, details: dict) -> None:
        """Handle git operation retry attempt.

        Args:
            details: Dictionary containing retry attempt details:
                wait: Time to wait before next attempt
                elapsed: Total time elapsed
                tries: Number of attempts made
                target: Function that was called
                args: Arguments passed to function
                kwargs: Keyword arguments passed to function
        """
        typer.echo(
            "Backoff {wait:0.1f} seconds ({elapsed:0.2f} elapsed) after "
            "{tries} tries calling {target}(*{args}, **{kwargs})".format(**details),
            err=True,
        )

    @classmethod
    def _on_giveup(cls: type, details: dict) -> None:
        """Handle git operation retry failure.

        Called when maximum retries are exhausted or operation fails permanently.

        Args:
            details: Dictionary containing retry attempt details:
                elapsed: Total time elapsed
                tries: Number of attempts made
                target: Function that was called
                args: Arguments passed to function
                kwargs: Keyword arguments passed to function
                exception: The last exception that occurred
        """
        args = [*details.get("args", ())]
        args = args[1:] if args else []
        kwargs = details.get("kwargs", {})
        with contextlib.suppress(KeyError, AttributeError):
            kwargs["repo"] = kwargs["repo"].name
        name = details["target"]
        module = "UNKNOWN"
        with contextlib.suppress(KeyError, AttributeError):
            name = details["target"].__name__
        with contextlib.suppress(KeyError, AttributeError):
            module = details["target"].__module__
            name = details["target"].__code__.co_qualname
        with contextlib.suppress(KeyError, AttributeError):
            typer.echo(f'{module}.{name}: {details["exception"].body}', err=True)
        typer.echo(
            f"Backoff giving up after {details['elapsed']:0.2f} seconds and {details['tries']} tries calling "
            f"{module}.{name}(*{args}, **{kwargs})",
            err=True,
        )


@backoff.on_exception(
    backoff.expo,
    GitCommandError,
    max_time=THROTTLED_BACKOFF_MAX_TIME,
    max_tries=THROTTLED_BACKOFF_MAX_TRIES,
    on_backoff=GitBackoff._on_backoff,
    on_giveup=GitBackoff._on_giveup,
    on_success=GitBackoff._on_success,
    logger=None,
)
def run_git_cmd(
    repo: git.Repo,
    cmd: str,
    *args,
    dry_run: bool = False,  # noqa: ARG001
    verbose: int = 0,
    **kwargs,  # noqa: ARG001
) -> tuple[int, str, str]:
    """Run a raw git command on the repository.

    Executes a git command directly using the git binary. This is useful for
    commands that are not supported by the GitPython library or need special handling.

    Args:
        repo: Git repository to run command on
        cmd: Git command to run (e.g. "fetch", "push")
        *args: Additional arguments for the git command
        **kwargs: Additional keyword arguments for git command execution

    Returns:
        tuple: Contains:
            - int: Return code (0 for success)
            - str: Command output (stdout)
            - str: Error output (stderr)

    Example:
        >>> rc, out, err = run_git_cmd(repo, "status", "--porcelain")
    """
    stream = io.StringIO()
    with contextlib.redirect_stdout(stream):
        rc, out, err = getattr(repo.git, cmd)(
            *args,
            as_process=False,
            universal_newlines=True,
            with_stdout=True,
            strip_newline_in_stdout=False,
            with_extended_output=True,
            with_exceptions=False,
        )
    if verbose:
        print(stream.getvalue(), end="", flush=True)
    return rc, out, err


@backoff.on_exception(
    backoff.expo,
    GitCommandError,
    max_time=THROTTLED_BACKOFF_MAX_TIME,
    max_tries=THROTTLED_BACKOFF_MAX_TRIES,
    on_backoff=GitBackoff._on_backoff,
    on_giveup=GitBackoff._on_giveup,
    on_success=GitBackoff._on_success,
    logger=None,
)
def run_git(
    repo: git.Repo,
    cmd: str,
    *args,
    check_rc: bool = True,
    exit_on_error: bool = True,
    fail_on: list[str] | None = None,
    target: str | None = None,
    dry_run: bool = False,
    verbose: int = 0,
    **kwargs,
) -> int:
    """Run a git command with error handling and retries.

    Executes a git command with proper error handling, output processing,
    and automatic retries for transient failures.

    Args:
        repo: Git repository to run command on
        cmd: Git command to run (e.g. "fetch", "push")
        *args: Additional arguments for the git command
        check_rc: If True, verify command return code indicates success
        exit_on_error: If True, exit script on command failure
        fail_on: List of strings to check in output to determine failure
        target: Target branch name for error messages
        **kwargs: Additional keyword arguments for git command execution

    Returns:
        int: Command return code (0 for success)

    Raises:
        GitCommandError: If command fails and exit_on_error is False
        typer.Exit: If command fails and exit_on_error is True
    """
    rc, out, err = run_git_cmd(
        repo,
        cmd,
        *args,
        dry_run=dry_run,
        verbose=verbose,
        **kwargs,
    )
    if verbose:
        typer.echo(out)
    if check_rc and rc != 0:
        if out and fail_on and any(fail in out for fail in fail_on):
            typer.echo(f"Failed on {fail_on}", err=True)
            if exit_on_error:
                raise typer.Exit(1)
        if err:
            typer.echo(f"Failed to {cmd} {target}", err=True)
            typer.echo(err, err=True)
            raise GitCommandError(f"Failed to {cmd} {target}", rc, out, err)
    return rc


# === Main ===
def parse_worktrees(out: str) -> dict[str, pathlib.Path]:
    """Parse the output of 'git worktree list' command.

    Processes the output of 'git worktree list' and creates a mapping of
    branch names to their corresponding worktree paths.

    Args:
        out: Raw output string from 'git worktree list' command.
            Expected format: one worktree per line with path and branch info.

    Returns:
        dict[str, pathlib.Path]: Mapping of branch names to worktree paths.
            Keys are branch names (without remote prefix).
            Values are absolute paths to worktree directories.
    """
    worktrees = {}
    for line in out.splitlines():
        parts = line.split()
        if len(parts) == WORKTREES_COLUMN_COUNT:
            # There are three columns generally: path, hash, and branch
            path = pathlib.Path(parts[0])
            # The branch name is in the third column, and it can be enclosed in square brackets
            # We need to remove the square brackets if present
            branch = parts[2]
            if branch.startswith("["):
                branch = branch[1:-1]
            worktrees[branch] = path
    return worktrees


def initialize_repo(
    target: str,
    verbose: int = 0,
) -> tuple[git.Repo, dict[str, pathlib.Path]]:
    """Initialize repository and get worktrees.

    Initializes the git repository, validates the target branch exists,
    and gets a list of all worktrees in the repository.

    Args:
        target: Target branch name to validate
        verbose: Verbosity level (0-3). Higher values show more details:
            1: Shows repository info
            2: Shows worktree details
            3: Shows detailed debug info

    Returns:
        tuple: Contains:
            - git.Repo: Initialized repository object
            - dict[str, pathlib.Path]: Mapping of branch names to worktree paths

    Raises:
        typer.Exit: If repository initialization fails or target branch is invalid
    """
    try:
        repo = git.Repo(".", search_parent_directories=True)

        # Get worktrees
        rc, out, err = run_git_cmd(repo, "worktree", "list")
        if rc:
            typer.echo(err, err=True)
            raise typer.Exit(rc)
        worktrees = parse_worktrees(out)

        # Validate target branch exists
        try:
            repo.branches[target]
        except IndexError:
            typer.echo(f"Invalid branch: {target}", err=True)
            raise typer.Exit(1) from None

        if verbose:
            typer.echo(f"Repository: {repo.working_dir}")
            typer.echo(f"Worktrees: {len(worktrees)}")

        return repo, worktrees

    except git.InvalidGitRepositoryError:
        typer.echo("Not a git repository", err=True)
        raise typer.Exit(1) from None


def sync_target_branch(
    repo: git.Repo,
    target: str,
    dry_run: bool = False,
    verbose: int = 0,
    worktrees: dict[str, pathlib.Path] | None = None,
) -> None:
    """Sync target branch with remote.

    Args:
        repo: Git repository to sync
        target: Target branch name
        dry_run: If True, show what would be done without making changes
        verbose: Verbosity level (0-3)
        worktrees: Dictionary of worktree paths
    """
    if verbose:
        typer.echo(f"Syncing branch: {target}")

    if dry_run:
        typer.echo(f"Would sync {target} with remote")
        return

    # Check if branch is in a worktree
    if worktrees and target in worktrees:
        worktree_path = worktrees[target]
        if verbose:
            typer.echo(f"Using worktree at {worktree_path} for {target}")

        # Create a new repo instance for the worktree
        worktree_repo = git.Repo(worktree_path)

        # Sync the worktree safely
        run_git(worktree_repo, "fetch", "--all", "--tags", target=target)
        run_git(worktree_repo, "pull", "--rebase=false", target=target)
        return

    # If not in worktree, try to sync in main repo
    try:
        run_git(repo, "fetch", "--all", "--tags", target=target)
        run_git(repo, "checkout", target, target=target)
        run_git(repo, "pull", "--rebase=false", target=target)
    except Exception as exc:
        if "is already used by worktree" in str(exc):
            typer.echo(f"Branch {target} is in use by a worktree but not found in worktree list", err=True)
        raise


def print_environment_branches(
    repo: git.Repo,
    verbose: int = 0,
) -> None:
    """Print information about environment branches in the repository.

    Lists all branches in the repository and filters for environment branches
    based on naming convention. Segments branch names to identify components.

    Args:
        repo: Git repository to inspect
        verbose: Verbosity level (0-3). Higher values show more details:
            1: Shows active branch
            2: Shows ignored branches
            3: Shows branch segments
    """
    if verbose:
        typer.echo(f"Active branch: {repo.active_branch.name}")
        typer.echo("\nBranches:\n")

    for ref in repo.branches:
        segments = []
        with contextlib.suppress(Exception):
            segments = ref.name.split("--", maxsplit=3)
        if len(segments) == SEGMENTS:
            typer.echo(f"Existing branch: {ref.name}")
        elif verbose:
            typer.echo(f"Ignoring ref: {ref.name}")


def process_branch(  # noqa: C901, PLR0912
    repo: git.Repo,
    ref: git.RemoteReference | git.Head,
    branch: str,
    worktrees: dict[str, pathlib.Path],
    target: str,
    dry_run: bool = False,
    verbose: int = 0,
) -> None:
    """Process a single branch.

    Args:
        repo: Git repository
        ref: Git reference to process
        branch: Branch name
        worktrees: Dictionary of worktree paths
        target: Target branch name
        dry_run: If True, show what would be done without making changes
        verbose: Verbosity level (0-3). Higher values show more details:
            1: Shows basic operations
            2: Shows git commands
            3: Shows detailed output
    """
    path = None

    # Handle worktree case
    if branch in worktrees and worktrees[branch] != repo.working_dir:
        if verbose:
            typer.echo(f"Worktree: {branch}")
        path = worktrees[branch]

    # Handle normal branch case
    else:
        if isinstance(ref, git.RemoteReference):
            try:
                _ = repo.branches[branch]
                if verbose:
                    typer.echo(f"Existing branch: {branch}")
            except IndexError:
                if dry_run:
                    typer.echo(f"Would create branch: {branch} from {ref.name}")
                else:
                    typer.echo(f"Creating branch: {branch} from {ref.name}")
                    run_git(repo, "checkout", branch, target=target)
        elif isinstance(ref, git.Head) and verbose:
            typer.echo(f"Existing branch: {branch}")

        if verbose:
            typer.echo(f"Sync {branch}")

        if dry_run:
            typer.echo(f"Would sync branch: {branch}")
            return

        # Sync branch
        rc = run_git(repo, "checkout", branch, error_on_fail=False, target=target)
        if rc != 0:
            return

        rc = run_git(repo, "pull", "--rebase=false", error_on_fail=False, target=target)
        if rc != 0:
            return

        run_git(repo, "pull", "--tags", "--force", target=target, dry_run=dry_run, verbose=verbose)

        if repo.active_branch.name != branch:
            typer.echo(f"Failed to checkout {branch}", err=True)
            return

        path = pathlib.Path(repo.working_dir)

    # Handle manifest
    manifest_file = f"config/{branch}.yaml"
    if path and (path / manifest_file).exists():
        if dry_run:
            typer.echo(f"Would update manifest: {manifest_file}")
        else:
            manifest = read_file(path / manifest_file)
            rc = run_git(repo, "checkout", target, error_on_fail=False, target=target)
            if rc != 0:
                return
            update_manifest(manifest, manifest_file, repo, target, dry_run, verbose)
    else:
        typer.echo(f"Error: {target} does not have {manifest_file}", err=True)


def process_remote_refs(
    repo: git.Repo,
    target: str,
    worktrees: dict[str, pathlib.Path],
    dry_run: bool = False,
    verbose: int = 0,
) -> None:
    """Process all remote references.

    Args:
        repo: Git repository
        target: Target branch name
        worktrees: Dictionary of worktree paths
        dry_run: If True, show what would be done without making changes
        verbose: Verbosity level (0-3). Higher values show more details:
            1: Shows basic operations
            2: Shows git commands
            3: Shows detailed output

    """
    if verbose:
        typer.echo("Processing remote references...")
    existing_branches = {ref.name for ref in repo.branches}
    all_refs = [ref for ref in repo.refs if isinstance(ref, git.RemoteReference)]

    for ref in all_refs:
        if (
            isinstance(ref, (git.Head, git.RemoteReference))
            and ref.name != target
            and ref.name not in existing_branches
        ):
            branch = ref.name
            if "/" in branch:
                remote, *branch = branch.split("/")
                branch = "/".join(branch) if isinstance(branch, (list, tuple)) else branch

            segments = []
            with contextlib.suppress(Exception):
                segments = branch.split("--", maxsplit=3)

            if len(segments) == SEGMENTS:
                typer.echo(f"{target} <- {branch}")
                process_branch(repo, ref, branch, worktrees, target, dry_run, verbose)
            elif verbose:
                typer.echo(f"Ignore {ref.name}")


def update_manifest(
    manifest: str | None,
    manifest_file: str,
    repo: git.Repo,
    target: str,
    dry_run: bool = False,
    verbose: int = 0,
) -> None:
    """Update manifest file and sync changes.

    Args:
        manifest: Manifest content to write, or None to just fix existing
        manifest_file: Path to manifest file
        repo: Git repository
        target: Target branch name
        dry_run: If True, show what would be done without making changes
        verbose: Verbosity level (0-3). Higher values show more details:
            1: Shows basic operations
            2: Shows git commands
            3: Shows detailed output

    """
    if verbose:
        typer.echo(f"Active branch: {repo.active_branch.name}")
        typer.echo(f"Updating manifest: {manifest_file}")

    if dry_run:
        typer.echo(f"Would update manifest: {manifest_file}")
        return

    # typer.echo(f"{repo.active_branch.name=}")
    # environment_manifest = load_templated_config_file(
    #     manifest_file,
    #     search_path=str(pathlib.Path.cwd().resolve().absolute()),
    #     kind="environment_manifest",
    # )
    # environment_manifest = load_file(manifest_file)
    if manifest:
        write_file(manifest_file, manifest)
    _ = fix_manifest(manifest_file, repo=repo, target=target, verbose=verbose, dry_run=dry_run)


def get_branch_shortname(branch_name: str) -> str:
    """Get the short name of a branch without remote prefix.

    Args:
        branch_name: Full branch name (e.g. 'origin/feature/xyz')

    Returns:
        str: Short branch name (e.g. 'feature/xyz')
    """
    parts = branch_name.split("/", 1)
    return parts[1] if len(parts) > 1 else branch_name


def compare_branches(
    repo: git.Repo,
    dry_run: bool = False,  # noqa: ARG001
    verbose: int = 0,
) -> tuple[set[str], set[str], set[str]]:
    """Compare remote and local branches.

    Fetches latest remote state and compares remote branches with local branches.
    Uses short branch names (without remote prefix) for comparison.

    Args:
        repo: Git repository to analyze
        dry_run: If True, show what would be done without making changes
        verbose: Verbosity level (0-3)

    Returns:
        tuple: Contains:
            - set[str]: Branches that exist both locally and remotely
            - set[str]: Branches that exist only remotely
            - set[str]: Branches that exist only locally

    """
    if verbose:
        typer.echo("Comparing remote and local branches...")

    # Fetch latest remote state
    run_git(repo, "fetch", "--all", "--prune")

    # Get remote and local branches
    remote_branches = {get_branch_shortname(ref.name) for ref in repo.remote().refs if not ref.name.endswith("HEAD")}
    local_branches = {ref.name for ref in repo.heads if not ref.name.endswith("HEAD")}

    # Compare branches
    common = remote_branches & local_branches
    remote_only = remote_branches - local_branches
    local_only = local_branches - remote_branches

    if verbose:
        typer.echo("\nBranch comparison results:")
        typer.echo(f"Common branches: {len(common)}")
        typer.echo(f"Remote-only branches: {len(remote_only)}")
        typer.echo(f"Local-only branches: {len(local_only)}")

        if verbose > 1:
            if remote_only:
                typer.echo("\nBranches only on remote:")
                for branch in sorted(remote_only):
                    typer.echo(f"  {branch}")
            if local_only:
                typer.echo("\nBranches only local:")
                for branch in sorted(local_only):
                    typer.echo(f"  {branch}")

    return common, remote_only, local_only


def prune_local_branches(
    repo: git.Repo,
    local_only: set[str],
    dry_run: bool = False,
    verbose: int = 0,
) -> None:
    """Delete local branches that don't exist on remote.

    Args:
        repo: Git repository to operate on
        local_only: Set of branch names that exist only locally
        dry_run: If True, show what would be done without making changes
        verbose: Verbosity level (0-3)

    """
    if not local_only:
        if verbose:
            typer.echo("No local-only branches to prune")
        return

    if verbose:
        typer.echo("\nPruning local-only branches...")

    for branch in local_only:
        if dry_run:
            typer.echo(f"Would delete local branch: {branch}")
            continue

        if verbose:
            typer.echo(f"Deleting local branch: {branch}")

        try:
            run_git(repo, "branch", "-D", branch)
        except Exception as exc:
            typer.echo(f"Failed to delete branch {branch}: {exc}", err=True)


def sync_branches(
    target: str = SYNC_OPTIONS["target"],
    dry_run: bool = SYNC_OPTIONS["dry_run"],
    verbose: int = SYNC_OPTIONS["verbose"],
    debug: bool = SYNC_OPTIONS["debug"],
    sync: bool = SYNC_OPTIONS["sync"],
    prune: bool = SYNC_OPTIONS["prune"],
) -> None:
    """
    Synchronize environment branches with the target branch.

    This function orchestrates the synchronization process by:
    1. Comparing remote and local branches if --sync is enabled
    2. Creating local branches for remote-only branches if --sync is enabled
    3. Pruning local-only branches if --prune is enabled
    4. Initializing the repository and getting worktrees
    5. Syncing the target branch with remote
    6. Processing environment branches
    7. Updating manifests as needed

    Args:
        target: Target branch to sync with
        dry_run: If True, show what would be done without making changes
        verbose: Verbosity level (0-3). Higher values show more details:
            1: Shows basic operations
            2: Shows git commands
            3: Shows detailed output
        debug: Enable debug mode
        sync: Compare remote and local branches before sync
        prune: Delete local branches that don't exist on remote

    """
    try:
        if verbose and dry_run:
            typer.echo("Dry run mode - no changes will be made")

        repo, worktrees = initialize_repo(target, verbose)

        # Handle sync and prune operations first
        if sync or prune:
            common, remote_only, local_only = compare_branches(repo, dry_run, verbose)

            if prune:
                prune_local_branches(repo, local_only, dry_run, verbose)

        sync_target_branch(repo, target, dry_run, verbose, worktrees)
        print_environment_branches(repo, verbose)

        if verbose:
            typer.echo(f"Active branch: {repo.active_branch.name}")
            typer.echo(f"\nSync to {target}:\n")

        # Process remote refs only when sync is enabled
        if sync:
            process_remote_refs(repo, target, worktrees, dry_run, verbose)

        # Update target manifest if not main/master
        manifest_file = f"config/{target}.yaml"
        if target not in ("main", "master") and pathlib.Path(manifest_file).exists():
            update_manifest(None, manifest_file, repo, target, dry_run, verbose)
        else:
            typer.echo(f"Error: {target} branch does not have {manifest_file}", err=True)

    except Exception as exc:
        # Handle debug mode
        is_debug = debug or os.getenv("DEBUG")
        if is_debug:
            import traceback

            traceback.print_exception(exc.__class__, exc, exc.__traceback__, file=sys.stderr)

        # Print error and exit
        typer.echo(f"Error: {exc}", err=True)
        raise typer.Exit(1) from None


app = typer.Typer(add_completion=False)


@app.command()
def main(
    target: str = SYNC_OPTIONS["target"],
    dry_run: bool = SYNC_OPTIONS["dry_run"],
    verbose: int = SYNC_OPTIONS["verbose"],
    debug: bool = SYNC_OPTIONS["debug"],
    sync: bool = SYNC_OPTIONS["sync"],
    prune: bool = SYNC_OPTIONS["prune"],
) -> None:
    """Sync environment branches with target branch."""
    try:
        sync_branches(target, dry_run, verbose, debug, sync, prune)
    except Exception as exc:
        import os

        from toolbag.utils.helpers import to_boolean

        pytest = any(k for k, _ in os.environ.items() if k.startswith("PYTEST"))
        pycharm = any(k for k, _ in os.environ.items() if k.startswith("PYCHARM"))
        is_debug = not pytest and (pycharm or to_boolean(os.getenv("DEBUG")) or "--debug" in sys.argv)
        if is_debug:  # pragma: no cover
            # import sys  # pragma: no cover
            import traceback  # pragma: no cover

            traceback.print_exception(exc.__class__, exc, exc.__traceback__, file=sys.stderr)  # pragma: no cover

        raise typer.Exit(1) from None


if __name__ == "__main__":
    app()
