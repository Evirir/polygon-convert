# Polygon to CMS Converter

This file creates a copy of the tests, renames the tests and outputs a string that can be used
for the `Score Parameters` field (use `GroupMin` score type) for Contest Management System (CMS).
The renamed tests and the score parameters simulates Polygon's subtask (groups) system in CMS.

This code uses `problem.xml` in the Polygon **full** package (either Windows or Linux is fine) to retrieve information about subtasks.

## How To Use
- Generate a **full** package on Polygon for your problem and download the Linux version.
- Run this file: `python rename.py root_path`, where `root_path` is the path to the Polygon **full** package's root directory (where the folders `statements/` and `tests/` are).
- A new folder `cms_tests` and a `.zip` file `cms_tests.zip` containing renamed tests will be created in `root_path`.
- A string will also be outputted to the standard output and a new file `score_params.txt`. You should copy this to
the Score Parameters field in CMS (use GroupMin score type).
