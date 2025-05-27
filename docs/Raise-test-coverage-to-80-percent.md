Here is the result of running tests

↳ poetry run pytest --cov=pdocs --cov=tests --cov-report=term-missing ${@} --cov-report html tests --capture=no --color=yes
=============================================================================================================================================================================================================================== test session starts ================================================================================================================================================================================================================================
platform darwin -- Python 3.8.20, pytest-5.4.3, py-1.11.0, pluggy-0.13.1
rootdir: /Users/christo/Dropbox/LVS/ws/SandsB2B/tools/pdocs
plugins: cov-2.12.1, mock-1.13.0
collected 56 items

tests/test_doc.py ..
tests/test_extract.py .......................................
tests/test_parse_docstring.py ....
tests/test_pdoc.py .
tests/test_render.py ..
tests/test_static.py ......../Users/christo/.pyenv/versions/3.8.20/envs/pdocs/lib/python3.8/site-packages/coverage/report_core.py:115: CoverageWarning: Couldn't parse '/Users/christo/Dropbox/LVS/ws/SandsB2B/tools/pdocs/tests/_css_mako': No source for code: '/Users/christo/Dropbox/LVS/ws/SandsB2B/tools/pdocs/tests/_css_mako'. (couldnt-parse)
coverage._warn(msg, slug="couldnt-parse")
/Users/christo/.pyenv/versions/3.8.20/envs/pdocs/lib/python3.8/site-packages/coverage/report_core.py:115: CoverageWarning: Couldn't parse '/Users/christo/Dropbox/LVS/ws/SandsB2B/tools/pdocs/tests/_html_frame_mako': No source for code: '/Users/christo/Dropbox/LVS/ws/SandsB2B/tools/pdocs/tests/_html_frame_mako'. (couldnt-parse)
coverage._warn(msg, slug="couldnt-parse")
/Users/christo/.pyenv/versions/3.8.20/envs/pdocs/lib/python3.8/site-packages/coverage/report_core.py:115: CoverageWarning: Couldn't parse '/Users/christo/Dropbox/LVS/ws/SandsB2B/tools/pdocs/tests/_html_index_mako': No source for code: '/Users/christo/Dropbox/LVS/ws/SandsB2B/tools/pdocs/tests/_html_index_mako'. (couldnt-parse)
coverage._warn(msg, slug="couldnt-parse")
/Users/christo/.pyenv/versions/3.8.20/envs/pdocs/lib/python3.8/site-packages/coverage/report_core.py:115: CoverageWarning: Couldn't parse '/Users/christo/Dropbox/LVS/ws/SandsB2B/tools/pdocs/tests/_html_module_mako': No source for code: '/Users/christo/Dropbox/LVS/ws/SandsB2B/tools/pdocs/tests/_html_module_mako'. (couldnt-parse)
coverage._warn(msg, slug="couldnt-parse")
/Users/christo/.pyenv/versions/3.8.20/envs/pdocs/lib/python3.8/site-packages/coverage/report_core.py:109: CoverageWarning: Couldn't parse Python file '/Users/christo/Dropbox/LVS/ws/SandsB2B/tools/pdocs/tests/onpath/malformed_syntax.py' (couldnt-parse)
coverage._warn(msg, slug="couldnt-parse")


---------- coverage: platform darwin, python 3.8.20-final-0 ----------
Name                                       Stmts   Miss  Cover   Missing
------------------------------------------------------------------------
pdocs/__init__.py                              2      0   100%
pdocs/_version.py                              1      0   100%
pdocs/api.py                                  56     39    30%   45-57, 79-92, 96-100, 126-150, 154-159, 163-166
pdocs/cli.py                                   6      6     0%   1-8
pdocs/defaults.py                              6      0   100%
pdocs/doc.py                                 374     81    78%   30-31, 53-60, 70, 101, 115, 160-161, 244, 274, 278-291, 306, 328-333, 356-358, 393, 463-466, 504-506, 514, 517, 528, 534, 574-575, 609-611, 615, 623-625, 699, 714-715, 729-730, 734-738, 757, 768-781, 784, 791, 818, 868, 872
pdocs/extract.py                              92      4    96%   104, 121, 141, 152
pdocs/html_helpers.py                         83     28    66%   31, 58, 67-72, 84, 99-111, 123, 127, 148-151, 153, 156, 167
pdocs/logo.py                                  3      0   100%
pdocs/render.py                               29      6    79%   40-42, 85-87
pdocs/static.py                               53     20    62%   36, 49, 52, 63-75, 84-89
tests/docstring_parser/example_google.py      33     12    64%   39, 51-52, 67-76, 84, 89, 94
tests/docstring_parser/example_numpy.py       29     12    59%   37, 53-54, 74-83, 93, 98, 103
tests/modules/dirmod/__init__.py               2      1    50%   5
tests/modules/index/__init__.py                1      0   100%
tests/modules/index/index.py                   1      0   100%
tests/modules/index/two/__init__.py            0      0   100%
tests/modules/one.py                           2      1    50%   5
tests/modules/submods/__init__.py              2      1    50%   5
tests/modules/submods/three/__init__.py        0      0   100%
tests/modules/submods/two.py                   0      0   100%
tests/onpath/__init__.py                       0      0   100%
tests/onpath/simple.py                         2      1    50%   2
tests/test_doc.py                             26      4    85%   15, 19, 23, 28
tests/test_extract.py                         30      0   100%
tests/test_parse_docstring.py                137      2    99%   17, 53
tests/test_pdoc.py                             3      0   100%
tests/test_render.py                          12      0   100%
tests/test_static.py                          28      0   100%
tests/tutils.py                                8      0   100%
------------------------------------------------------------------------
TOTAL                                       1021    218    79%
Coverage HTML written to dir htmlcov


================================================================================================================================================================================================================================ 56 passed in 0.73s ================================================================================================================================================================================================================================


Note how the total coverage is 79% but there are several files that have less than 79% coverage.

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
   