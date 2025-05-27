#!/usr/bin/env python3
"""Extracts the profiles and accounts from the input and outputs them as a matrix."""
import json
import os
import pathlib
import sys

import yaml

__version__ = "0.26.74"

# Manifest may be set in environment variable MANIFEST
manifest = os.getenv("MANIFEST", "")
# Get the input profiles_and_accounts
config_input = os.getenv("PROFILES_AND_ACCOUNTS", "")
is_text = False
matrix = []

manifest_path = pathlib.Path(manifest) if manifest else None
config_path = pathlib.Path(config_input)

# Step 0: Check if manifest file hasprofiles_and_accounts
if manifest_path and manifest_path.exists():
    print(f"Manifest found: {manifest_path}")
    from profiles_and_accounts import parse_profiles_and_accounts

    try:
        config_input = parse_profiles_and_accounts(manifest)
        if config_input.strip():
            is_text = True
            config_path = None
    except Exception as e:
        print(f"Failed to parse manifest: {e}", file=sys.stderr)
        sys.exit(1)
else:
    print("No manifest found. Proceeding with config input.")

# Step 1: Check if input is a file path
if config_path and config_path.exists():
    print(f"Input detected as a file path: {config_input}")
    with config_path.open("r") as file:
        raw_content = file.read()

    # Determine if the file is plain text
    if not config_input.endswith((".yaml", ".yml", ".json")):
        is_text = True
        config_input = raw_content
    else:
        config_input = raw_content  # Load content as string for parsing
else:
    print("Input is not a file path. Proceeding as direct input.")

if not config_input:
    print("No input found. Trying manifest ...")
    config_input = os.getenv("MANIFEST", "")
    config_path = pathlib.Path(config_input)
    if config_path and config_path.exists():
        try:
            with config_path.open("r") as file:
                raw_content = file.read()
            config = yaml.safe_load(raw_content)
            config_input = yaml.safe_dump(
                {"profiles_and_accounts": config["metadata"]["deployment"]["profiles_and_accounts"]},
            )
            is_text = False
        except Exception as e:
            print(f"Failed to load manifest: {e}", file=sys.stderr)

# Step 2: Parse the string
try:
    if is_text:
        print("Parsing input as plain text...")
        # Parse plain text as colon-separated values
        matrix = [
            {"profile": line.split(":")[0].strip(), "account_id": line.split(":")[1].strip()}
            for line in config_input.splitlines()
            if ":" in line
        ]
    else:
        print("Parsing input as YAML...")
        # Try YAML parsing first
        config = yaml.safe_load(config_input)
        if isinstance(config, dict) and "profiles_and_accounts" in config:
            matrix = [
                {"profile": item["profile"], "account_id": item["account_id"]}
                for item in config["profiles_and_accounts"]
            ]
        else:
            raise ValueError("Input is not valid YAML with 'profiles_and_accounts'")
except (yaml.YAMLError, ValueError):
    try:
        print("Parsing input as JSON...")
        # Try JSON parsing as a fallback
        config = json.loads(config_input)
        if isinstance(config, dict) and "profiles_and_accounts" in config:
            matrix = [
                {"profile": item["profile"], "account_id": item["account_id"]}
                for item in config["profiles_and_accounts"]
            ]
        else:
            raise ValueError("Input is not valid JSON with 'profiles_and_accounts'")
    except json.JSONDecodeError:
        print("Failed to parse input. Input is not valid text, YAML, or JSON. Exiting with empty matrix.")

# Handle empty matrix
if not matrix:
    print("No profiles and accounts found.")
else:
    print(f"Loaded profiles and accounts: {matrix}")

output_name = "matrix"
output_value = json.dumps(matrix)

# Retrieve the path to the GITHUB_OUTPUT file
github_output = os.getenv("GITHUB_OUTPUT")

if github_output:
    # Write the output to the GITHUB_OUTPUT file
    with pathlib.Path(github_output).open("a") as output_file:
        output_file.write(f"{output_name}={output_value}\n")
else:
    print("GITHUB_OUTPUT environment variable is not set.")
    print(f"{output_name}={output_value}\n")
