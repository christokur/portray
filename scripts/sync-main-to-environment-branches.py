#!/usr/bin/env python3  # noqa: N999, EXE001
"""Sync main to environment branches.

version: 0.2.0
"""
import pathlib
import sys

import git
import sh

__version__ = "0.26.74"

MAX_UNMERGED_LEVELS = 10
prefix = "ld--"
target = "main"

# fetch --all
repo = git.Repo(".", search_parent_directories=True)


def run_git(
    repo: git.Repo,
    cmd: str,
    *args,
    check_rc: bool = True,
    exit_on_error: bool = True,
    fail_on: list[str] | None = None,
    **kwargs,  # noqa: ARG001
) -> int:
    """Run git command."""
    rc, out, err = getattr(repo.git, cmd)(
        *args,
        as_process=False,
        universal_newlines=True,
        with_stdout=True,
        strip_newline_in_stdout=False,
        with_extended_output=True,
        with_exceptions=False,
    )
    if check_rc and rc != 0:
        if out:
            print(out)
            if fail_on and any(fail in out for fail in fail_on):
                print(f"Failed on {fail_on}")
                if exit_on_error:
                    sys.exit(1)
        if err:
            print(f"Failed to {cmd} {target}")
            print(err, file=sys.stderr)
            if exit_on_error:
                sys.exit(1)
    return rc


def find_unmerged_files(start: str | pathlib.Path = ".", depth: int = 0) -> None:
    """Find unmerged files."""
    if depth > MAX_UNMERGED_LEVELS:
        print(f"Too deep: {start}")
        return
    for entry in pathlib.Path(start).glob("**/*"):
        if entry.name in (
            ".gitignore",
            ".gitattributes",
            ".gitmodules",
            ".gitkeep",
            ".git",
            ".pytest_cache",
            "__pycache__",
            ".vscode",
            ".idea",
            "tmp",
            "sync-environment-branches.py",
            "sync-main-to-environment-branches.py",
        ):
            continue
        if entry.is_file() and entry.stat().st_size > 0:
            try:
                text = entry.read_text()
                if isinstance(text, bytes):
                    text = text.decode()
                if "<<<<<<<" in text and ">>>>>>>" in text and "=======" in text and str(entry.resolve()) != __file__:
                    print(f"Unmerged file: {entry}")
                    sys.exit(1)
            except UnicodeDecodeError as exc:
                print(f"Binary file?: {entry}; {exc}", file=sys.stderr)
        elif entry.is_dir():
            find_unmerged_files(entry, depth=depth + 1)


run_git(repo, "fetch", "--all")

print(f"{repo.active_branch.name=}")
print("\nBranches:\n")
# noinspection PyTypeChecker
for ref in repo.refs:
    if isinstance(ref, (git.RemoteReference,)):
        remote, *branch = ref.name.split("/")
        branch = "/".join(branch) if isinstance(branch, (list, tuple)) else branch
        # print(f"{ref.name} -> {remote} {branch}")
        try:
            # noinspection PyUnresolvedReferences
            repo.branches[branch]
        except IndexError:
            print(f"Creating branch {branch} from {ref.name}")
            run_git(repo, "checkout", branch, check_rc=False)
    elif isinstance(ref, (git.Head,)):
        print(f"Existing branch: {ref.name}")

print(f"{repo.active_branch.name=}")
print(f"\nSync {target}:\n")
run_git(repo, "checkout", target)
run_git(repo, "pull")
run_git(repo, "pull", "--tags", "--force")
disabled_environments = pathlib.Path("disabled-environments.txt").read_text()
try:
    # noinspection PyTypeChecker
    for ref in repo.refs:
        if (
            isinstance(ref, git.Head)
            and not isinstance(ref, git.RemoteReference)
            and ref.name != target
            and ref.name.startswith(prefix)
        ):
            print(f"Sync {ref.name}")
            assert ref.name in disabled_environments, f"Environment {ref.name} is not disabled"
            find_unmerged_files()
            rc = run_git(repo, "checkout", ref.name, exit_on_error=False)
            if rc != 0:
                continue
            rc = run_git(repo, "pull", "--rebase=false", exit_on_error=False)
            if rc != 0:
                continue
            rc = run_git(repo, "pull", "--tags", "--force", exit_on_error=False)
            if rc != 0:
                continue
            print(f"{repo.active_branch.name=}")
            if repo.active_branch.name != ref.name:
                print(f"Failed to checkout {ref.name}")
                continue
            find_unmerged_files()
            # Merge the target branch into the current branch
            run_git(
                repo,
                "merge",
                target,
                "--strategy-option=theirs",
                f"--message='chore: Merge {target}'",
                "--no-verify",
                fail_on=["merge failed"],
            )
            find_unmerged_files()
            # noinspection PyUnresolvedReferences
            rc = sh.python("scripts/bumpversion-cfg-environment-manifests.py")
            if isinstance(rc, str):
                print(rc)
            pathlib.Path("disabled-environments.txt").write_text(disabled_environments, encoding="utf-8")
            run_git(repo, "add", "-A")
            run_git(repo, "commit", f"--message='chore: Merge {target}'", "--no-verify")
            run_git(repo, "push")
            run_git(repo, "push", "--tags")
            print(f"Done {ref.name}\n------------------\n")
    # end for
    run_git(repo, "checkout", target)
except BaseException as exc:
    print(f"Early exit: {exc}")
    raise
print("==================\n    Done all\n==================\n")
