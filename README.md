# Polygon converter

This package creates a copy of the tests, renames the tests and outputs a string that can be used
for the `Score Parameters` field (use `GroupMin` score type) for Contest Management System (CMS).
The renamed tests and the score parameters capture Polygon's subtasks (groups) and dependencies in CMS.

This code uses `problem.xml` in the Polygon **full** package (either Windows or Linux is fine) to retrieve information about subtasks.

## How To Use

- Install this package: `pip install polyconv`
- All groups must use the `COMPLETE_GROUP` points policy.
- Generate a **full** package on Polygon for your problem and download the Linux version.
- Run this file: `polyconv polygon_path`, where `polygon_path` is the path to the Polygon **full** package's root directory (where the folders `statements/` and `tests/` are). Add the `-f` flag to overwrite files if they exist.
- A new folder `cms_out` will be created in `polygon_path` (this can be changed with `-o`) containing the following:
  - A folder `tests/` containing renamed tests.
  - A `.zip` file `tests.zip` with the contents in the `tests/` folder above.
  - A `score_params.txt` file with the score parameters string. You should copy this to the Score Parameters field in CMS (use GroupMin score type).
- The string in `score_params.txt` will also be output to the standard output.
