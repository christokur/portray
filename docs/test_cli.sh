#!/bin/bash

# Test script to compare old and new CLI functionality with actual command execution
# This tests both help text AND actual command execution

# Track test failures
FAILURES=0
TESTS=0

# Function to check command result
check_result() {
    TESTS=$((TESTS+1))
    local cmd_name="$1"
    local expected_code="$2"
    local actual_code="$3"
    
    if [ "$actual_code" -eq "$expected_code" ]; then
        echo "✅ PASS: $cmd_name (exit code: $actual_code)"
    else
        echo "❌ FAIL: $cmd_name (expected: $expected_code, got: $actual_code)"
        FAILURES=$((FAILURES+1))
    fi
}

# Function to check if file exists
check_file_exists() {
    TESTS=$((TESTS+1))
    local file_path="$1"
    local description="$2"
    
    if [ -e "$file_path" ]; then
        echo "✅ PASS: $description - File exists: $file_path"
    else
        echo "❌ FAIL: $description - File does not exist: $file_path"
        FAILURES=$((FAILURES+1))
    fi
}

# Check if arguments are provided
if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <old_cli_dir> <new_cli_dir>"
    echo "Example: $0 /Users/christo/Dropbox/LVS/ws/SandsB2B/tools/pdocs-1.2.1 /Users/christo/Dropbox/LVS/ws/SandsB2B/tools/pdocs"
    exit 1
fi

OLD_CLI_DIR="$1"
NEW_CLI_DIR="$2"

# Verify directories exist
if [ ! -d "$OLD_CLI_DIR" ]; then
    echo "Error: Old CLI directory does not exist: $OLD_CLI_DIR"
    exit 1
fi

if [ ! -d "$NEW_CLI_DIR" ]; then
    echo "Error: New CLI directory does not exist: $NEW_CLI_DIR"
    exit 1
fi

# Create test directories
rm -rf /tmp/pdocs_test_old /tmp/pdocs_test_new
mkdir -p /tmp/pdocs_test_old/html
mkdir -p /tmp/pdocs_test_old/md
mkdir -p /tmp/pdocs_test_new/html
mkdir -p /tmp/pdocs_test_new/md

echo "===== TESTING OLD CLI (v1.2.1) ====="
cd "$OLD_CLI_DIR"
source $RC_DIR/python.rc

# Ensure requests is installed
pip install requests

MODULE="requests"

# Run tests

echo -e "\n1. Basic help:"
pdocs --help
RESULT=$?
check_result "Old CLI - Basic help" 1 $RESULT

echo -e "\n2. Version flag:"
pdocs --version
RESULT=$?
check_result "Old CLI - Version flag" 1 $RESULT

echo -e "\n3. as_html help:"
pdocs as_html --help
RESULT=$?
check_result "Old CLI - as_html help" 0 $RESULT

echo -e "\n4. as_markdown help:"
pdocs as_markdown --help
RESULT=$?
check_result "Old CLI - as_markdown help" 0 $RESULT

echo -e "\n5. server help:"
pdocs server --help
RESULT=$?
check_result "Old CLI - server help" 0 $RESULT

echo -e "\n6. ACTUAL COMMAND: Generate HTML docs for $MODULE:"
pdocs as_html $MODULE -o /tmp/pdocs_test_old/html --overwrite
RESULT=$?
check_result "Old CLI - Generate HTML docs" 0 $RESULT
check_file_exists "/tmp/pdocs_test_old/html/requests/index.html" "Old CLI - HTML index file"
ls -la /tmp/pdocs_test_old/html/requests

echo -e "\n7. ACTUAL COMMAND: Generate Markdown docs for $MODULE:"
pdocs as_markdown $MODULE -o /tmp/pdocs_test_old/md --overwrite
RESULT=$?
check_result "Old CLI - Generate Markdown docs" 0 $RESULT
check_file_exists "/tmp/pdocs_test_old/md/requests/index.md" "Old CLI - Markdown index file"
ls -la /tmp/pdocs_test_old/md/requests

echo -e "\n8. ACTUAL COMMAND: Run server (with timeout):"
timeout 3s pdocs server $MODULE
RESULT=$?
check_result "Old CLI - Server start (timeout)" 124 $RESULT

echo -e "\n\n===== TESTING NEW CLI (v2.0.0) ====="
cd "$NEW_CLI_DIR"
source $RC_DIR/python.rc

# Ensure requests is installed
pip install requests

# Run tests

echo -e "\n1. Basic help:"
pdocs --help
RESULT=$?
check_result "New CLI - Basic help" 0 $RESULT

echo -e "\n2. Version flag:"
pdocs --version
RESULT=$?
check_result "New CLI - Version flag" 0 $RESULT

echo -e "\n3. as-html help:"
pdocs as-html --help
RESULT=$?
check_result "New CLI - as-html help" 0 $RESULT

echo -e "\n4. as-markdown help:"
pdocs as-markdown --help
RESULT=$?
check_result "New CLI - as-markdown help" 0 $RESULT

echo -e "\n5. server help:"
pdocs server --help
RESULT=$?
check_result "New CLI - server help" 0 $RESULT

echo -e "\n6. ACTUAL COMMAND: Generate HTML docs for $MODULE:"
pdocs as-html $MODULE --output-dir /tmp/pdocs_test_new/html --overwrite
RESULT=$?
check_result "New CLI - Generate HTML docs" 0 $RESULT
check_file_exists "/tmp/pdocs_test_new/html/requests/index.html" "New CLI - HTML index file"
ls -la /tmp/pdocs_test_new/html/requests

echo -e "\n7. ACTUAL COMMAND: Generate Markdown docs for $MODULE:"
pdocs as-markdown $MODULE --output-dir /tmp/pdocs_test_new/md --overwrite
RESULT=$?
check_result "New CLI - Generate Markdown docs" 0 $RESULT
check_file_exists "/tmp/pdocs_test_new/md/requests/index.md" "New CLI - Markdown index file"
ls -la /tmp/pdocs_test_new/md/requests

echo -e "\n8. ACTUAL COMMAND: Run server (with timeout):"
timeout 3s pdocs server $MODULE
RESULT=$?
check_result "New CLI - Server start (timeout)" 124 $RESULT

echo -e "\n9. ACTUAL COMMAND: Test other flags:"
echo "External links flag:"
pdocs as-html $MODULE --output-dir /tmp/pdocs_test_new/html --overwrite --external-links
RESULT=$?
check_result "New CLI - External links flag" 0 $RESULT

echo "Exclude source flag:"
pdocs as-html $MODULE --output-dir /tmp/pdocs_test_new/html --overwrite --exclude-source
RESULT=$?
check_result "New CLI - Exclude source flag" 0 $RESULT

echo -e "\n===== COMPARING OUTPUT FILES ====="
echo "Checking HTML output differences:"
diff -q /tmp/pdocs_test_old/html/requests/index.html /tmp/pdocs_test_new/html/requests/index.html
DIFF_RESULT=$?
if [ $DIFF_RESULT -eq 0 ]; then
    echo "✅ PASS: HTML outputs are identical (as expected for requests)"
else
    echo "❌ FAIL: HTML outputs differ (unexpected for requests)"
    echo "--- Unified diff (first 40 lines) ---"
    diff -u /tmp/pdocs_test_old/html/requests/index.html /tmp/pdocs_test_new/html/requests/index.html | head -40
    echo "--- End of diff preview ---"
    FAILURES=$((FAILURES+1))
fi
TESTS=$((TESTS+1))

echo -e "\nChecking Markdown output differences:"
diff -q /tmp/pdocs_test_old/md/requests/index.md /tmp/pdocs_test_new/md/requests/index.md
DIFF_RESULT=$?
if [ $DIFF_RESULT -eq 0 ]; then
    echo "✅ PASS: Markdown outputs are identical (as expected for requests)"
else
    echo "❌ FAIL: Markdown outputs differ (unexpected for requests)"
    echo "--- Unified diff (first 40 lines) ---"
    diff -u /tmp/pdocs_test_old/md/requests/index.md /tmp/pdocs_test_new/md/requests/index.md | head -40
    echo "--- End of diff preview ---"
    FAILURES=$((FAILURES+1))
fi
TESTS=$((TESTS+1))

echo -e "\n===== TEST SUMMARY ====="
echo "Total tests: $TESTS"
echo "Failures: $FAILURES"

if [ $FAILURES -eq 0 ]; then
    echo "✅ ALL TESTS PASSED"
    exit 0
else
    echo "❌ SOME TESTS FAILED"
    exit 1
fi
