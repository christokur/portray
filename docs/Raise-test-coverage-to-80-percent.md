Here is the result of running tests

↳ poetry run poe lint
↳ poetry run pytest -s --cov=portray/ --cov=tests --cov-report=term-missing ${@-} --cov-report html


Note how the total coverage percentage and any files that have less than 80% coverage.

Here is what I want you to do:
  - Identify the files with less than 80% coverage.
  - Write tests to increase the coverage of those files to at least 80%.
  - Pick ONE file with < 80% coverage and create new tests to increase the coverage by creating NEW test files in /tests.
  - DO NOT modify existing tests and DO NOT modify code in /pdocs.
  - Run the tests again to verify that the coverage has been increased to at least 80%.
  - Document any changes made to the code or tests in TESTS.md.
  - Update the coverage report to reflect the new coverage levels.
  - Ensure that all tests pass successfully after the changes.
  - If any tests fail, debug and fix the issues before finalizing the changes.
  - Commit the changes to the repository with a clear commit message indicating the increase in test coverage.
  - Always run the tests with ./scripts/test.sh from the project root to ensure that the coverage is correctly reported.
  - NEVER ask me "do I want to proceed?" or similar questions. Just proceed with the tasks as outlined.
  - YOU MAY NEVER MODIFY THE APP or API code to fix tests !!!!!
   