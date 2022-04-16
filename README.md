# Polygon to CMS Converter

This file creates a copy of the tests, renames the tests and outputs a string that can be used
for the `Score Parameters` field (use `GroupMin` score type) for Contest Management System (CMS).
The renamed tests and the score parameters simulates Polygon's subtask (groups) system in CMS.

This code uses `problem.xml` in the Polygon **full** package (tested on Windows only tbh) to retrieve information about subtasks.

- TODO: Generalize this to take the Polygon package's path as a parameter.

## How To Use
- Put this file in the Polygon **full** package's root directory (where the folders `statements/` and `tests` are).
- Run this file.
- A new folder `cms_tests` and a `.zip` file `cms.tests.zip` containing renamed tests will be created.
- A string will also be outputted to the standard output and a new file `score_params.txt`. You should copy this to 
the Score Parameters field in CMS (use GroupMin score type).
