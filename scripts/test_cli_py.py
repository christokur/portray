#!/usr/bin/env python3
import subprocess
import os
import difflib
import shutil
import argparse
import re

# Paths to temporary directories
TMP_OLD = "/tmp/pdocs_test_old"
TMP_NEW = "/tmp/pdocs_test_new"
PYTHON_RC_PATH = "~/workspace/DLDInternet/rc/python.rc"

# List of commands to test: (description, argument list)
COMMANDS = [
    ("Show help for CLI", ["--help"]),
    ("Show CLI version", ["--version"]),
    ("Show help for as-html", ["as-html", "--help"]),
    ("Show help for as-markdown", ["as-markdown", "--help"]),
    ("Show help for server", ["server", "--help"]),
    ("Generate HTML docs (long opts)", ["as-html", "requests", "--output-dir", "{outdir}/html", "--overwrite"]),
    ("Generate HTML docs (short opts)", ["as-html", "requests", "-o", "{outdir}/html", "--overwrite"]),
    ("Generate HTML docs, exclude source", ["as-html", "requests", "--output-dir", "{outdir}/html", "--overwrite", "--exclude-source"]),
    ("Generate HTML docs, external links", ["as-html", "requests", "--output-dir", "{outdir}/html", "--overwrite", "--external-links"]),
    ("Generate Markdown docs (long opts)", ["as-markdown", "requests", "--output-dir", "{outdir}/md", "--overwrite"]),
    ("Generate Markdown docs (short opts)", ["as-markdown", "requests", "-o", "{outdir}/md", "--overwrite"]),
]

def run_command(impl_dir, args, out_dir, rc_path: str = PYTHON_RC_PATH):
    """
    Run a command in the implementation directory with the correct Python environment.
    Uses a shell command to source the Python environment and run the command.
    """
    # Replace {outdir} with the actual output dir for this run
    args = [a.replace("{outdir}", out_dir) for a in args]

    # Build the shell command that sources the Python environment
    rc_path = os.path.expanduser(rc_path)
    cmd_parts = [
        f"cd {impl_dir}",
        f"source {rc_path}",
        "pdocs " + " ".join(args)
    ]
    shell_cmd = " && ".join(cmd_parts)

    print(f"Running: {shell_cmd}")
    result = subprocess.run(shell_cmd, shell=True, capture_output=True, text=True)
    return result.returncode, result.stdout, result.stderr

def filter_output(text):
    """Filter out irrelevant lines from command output."""
    # Filter out pyenv initialization messages
    lines = text.splitlines()
    filtered_lines = [line for line in lines if not re.match(r'pyenv\.rc|pyenv init|pyenv virtualenv-init', line)]
    return '\n'.join(filtered_lines)

def normalize_content(content):
    """
    Normalize content to ignore irrelevant differences like memory addresses.
    """
    # Replace memory addresses (like <object object at 0x1042b81c0>)
    normalized = re.sub(r'at 0x[0-9a-f]+', 'at 0xMEMADDRESS', content)
    return normalized

def compare_dirs(dir1, dir2):
    """Compare two directories and return a list of differences."""
    diffs = []

    # Check if directories exist
    if not os.path.exists(dir1) or not os.path.exists(dir2):
        if not os.path.exists(dir1):
            diffs.append(f"Directory {dir1} does not exist")
        if not os.path.exists(dir2):
            diffs.append(f"Directory {dir2} does not exist")
        return diffs

    # Get directory listings
    dir1_files = set(os.listdir(dir1))
    dir2_files = set(os.listdir(dir2))

    # Check for files only in dir1
    for name in dir1_files - dir2_files:
        diffs.append(f"Only in {dir1}: {name}")

    # Check for files only in dir2
    for name in dir2_files - dir1_files:
        diffs.append(f"Only in {dir2}: {name}")

    # Check common files and directories
    for name in dir1_files & dir2_files:
        path1 = os.path.join(dir1, name)
        path2 = os.path.join(dir2, name)

        # If both are directories, recursively compare
        if os.path.isdir(path1) and os.path.isdir(path2):
            sub_diffs = compare_dirs(path1, path2)
            diffs.extend(sub_diffs)
        # If both are files, compare content
        elif os.path.isfile(path1) and os.path.isfile(path2):
            try:
                with open(path1, 'r', encoding='utf-8', errors='replace') as f1, \
                     open(path2, 'r', encoding='utf-8', errors='replace') as f2:
                    content1 = f1.read()
                    content2 = f2.read()

                    # Normalize content to ignore irrelevant differences
                    norm_content1 = normalize_content(content1)
                    norm_content2 = normalize_content(content2)

                    if norm_content1 != norm_content2:
                        # For the diff, use the original content split into lines
                        diff = difflib.unified_diff(
                            content1.splitlines(True),
                            content2.splitlines(True),
                            fromfile=path1,
                            tofile=path2
                        )
                        diff_text = ''.join(diff)

                        # Add a note if the only differences are memory addresses
                        if normalize_content(diff_text) == normalize_content(diff_text):
                            diffs.append(f"Files {path1} and {path2} differ only in memory addresses (can be ignored)")
                        else:
                            diffs.append(diff_text)
            except Exception as e:
                diffs.append(f"Error comparing {path1} and {path2}: {str(e)}")
        # If one is a file and one is a directory
        else:
            diffs.append(f"Type mismatch: {path1} and {path2}")

    return diffs

def cleanup():
    """Clean up temporary directories."""
    shutil.rmtree(TMP_OLD, ignore_errors=True)
    shutil.rmtree(TMP_NEW, ignore_errors=True)
    os.makedirs(TMP_OLD, exist_ok=False)
    os.makedirs(TMP_NEW, exist_ok=False)

def main():
    parser = argparse.ArgumentParser(description="Compare old and new pdocs CLI outputs.")
    parser.add_argument("--old-dir", required=True, help="Path to old pdocs implementation directory")
    parser.add_argument("--new-dir", required=True, help="Path to new pdocs implementation directory")
    args = parser.parse_args()

    for desc, cmd_args in COMMANDS:
        print(f"\n=== {desc} === pdocs {cmd_args} ===")
        cleanup()

        # Run commands in their respective implementation directories
        rc_old, out_old, err_old = run_command(args.old_dir, cmd_args, TMP_OLD)
        rc_new, out_new, err_new = run_command(args.new_dir, cmd_args, TMP_NEW)

        # Filter out irrelevant output
        out_old = filter_output(out_old)
        out_new = filter_output(out_new)

        # Check for command failures
        if rc_old != 0:
            print(f"❌ Old CLI failed with exit code {rc_old}:")
            print(err_old if err_old else out_old)
        if rc_new != 0:
            print(f"❌ New CLI failed with exit code {rc_new}:")
            print(err_new if err_new else out_new)

        # Compare stdout/stderr
        if out_old != out_new:
            print("❌ FAIL: stdout differs")
            diff = difflib.unified_diff(out_old.splitlines(True), out_new.splitlines(True),
                                        fromfile="old_stdout", tofile="new_stdout")
            print(''.join(diff))
        else:
            print("✅ PASS: stdout identical")

        if err_old != err_new:
            print("❌ FAIL: stderr differs")
            diff = difflib.unified_diff(err_old.splitlines(True), err_new.splitlines(True),
                                        fromfile="old_stderr", tofile="new_stderr")
            print(''.join(diff))
        elif err_old:  # Only print if there's stderr content
            print("✅ PASS: stderr identical")

        # Compare output directories
        old_list = os.listdir(TMP_OLD)
        new_list = os.listdir(TMP_NEW)
        if old_list == new_list:
            diffs = compare_dirs(TMP_OLD, TMP_NEW)
            if diffs:
                print(f"❌ FAIL: Differences found:")
                for d in diffs:
                    print(d)
            else:
                print("✅ PASS: Output directories identical")
        else:
            print(
                f"❌ FAIL: old and new dir contents are not the same!\n"
                f"Old: {old_list}\nNew:{new_list}\n",
            )

        cleanup()

if __name__ == "__main__":
    main()
