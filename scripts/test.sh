#!/bin/bash
set -euxo pipefail

poetry run poe lint
poetry run pytest -s --cov=portray/ --cov=tests --cov-report=term-missing ${@-} --cov-report html
