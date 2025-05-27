#!/usr/bin/env python3  # noqa: N999
"""Driver script for template_defaults."""

import sys
from pathlib import Path

# Add scripts directory to Python path
scripts_dir = Path(__file__).parent
if str(scripts_dir) not in sys.path:
    sys.path.insert(0, str(scripts_dir))

from template_defaults import main  # noqa: E402

if __name__ == "__main__":
    main()
