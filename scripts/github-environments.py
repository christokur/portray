#!/usr/bin/env python3  # noqa: EXE001, N999
"""List GitHub environments."""
import os

from ghapi.all import GhApi

__version__ = "0.26.74"

# Initialize the API with authentication
api = GhApi(owner="SandsB2B", repo="ldx_deploy", token=os.getenv("GITHUB_TOKEN"))

# List environments
environments = api.repos.get_all_environments(owner="SandsB2B", repo="ldx_deploy")
print(environments)
