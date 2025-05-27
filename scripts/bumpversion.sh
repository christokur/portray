#! /usr/bin/env bash

CWD=$(pwd)
PROJECT_ROOT_PATH=$(git rev-parse --show-toplevel)

cd "$PROJECT_ROOT_PATH"

currentVersion="`cat VERSION`"

bumpversion --commit --current-version $currentVersion ${1:-"patch"}


cd "$CWD"
