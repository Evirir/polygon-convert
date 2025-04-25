"""Creates a folder and zip file containing tests in CMS format and
outputs the Score Parameters string."""

import json
import os
import shutil
import sys
import xml.etree.ElementTree as ET
from string import Template

OLD_TESTS_DIR = "tests"
NEW_TESTS_DIR = "cms_tests"
POLYGON_INPUT_TEMPLATE = Template("$id")
POLYGON_OUTPUT_TEMPLATE = Template("$id.a")
CMS_INPUT_TEMPLATE = Template("input.${id}_$group")
CMS_OUTPUT_TEMPLATE = Template("output.${id}_$group")
GROUPS_REGEX = Template(".*_(?:$groups)")


def dfs(dependencies: dict[str, set[str]], visited: set[str], group: str) -> None:
    """Helper function for copy_children_prereqs."""
    if group in visited:
        return
    visited.add(group)
    new_prereqs = dependencies[group].copy()
    new_prereqs.add(group)
    for prereq in dependencies[group]:
        dfs(dependencies, visited, prereq)
        new_prereqs |= dependencies[prereq]
    dependencies[group] = new_prereqs


def copy_children_prereqs(dependencies: dict[str, set[str]]):
    """Add all dependencies of children recursively."""
    visited = set()
    for group in dependencies:
        dfs(dependencies, visited, group)


def parse_dependencies(groups: list[ET.Element]) -> dict[str, list[str]]:
    """Returns a dictionary mapping group names to prerequisites."""
    dependencies: dict[str, set[str]] = {}

    for group in groups:
        name = group.get("name")
        prereqs = group.find("dependencies")
        if prereqs is not None:
            prereqs = prereqs.findall("dependency")
        else:
            prereqs = []
        dependencies[name] = {prereq.get("group") for prereq in prereqs}

    copy_children_prereqs(dependencies)

    for group, prereqs in dependencies.items():
        dependencies[group] = sorted(prereqs)
    return dependencies


def rename_tests(tests: list[ET.Element]):
    """Create a copy of tests from Polygon and rename them to CMS format with groups appended,
    in a zip file."""

    # Check if cms_tests/ exists, delete if true
    if os.path.exists(NEW_TESTS_DIR) and os.path.isdir(NEW_TESTS_DIR):
        shutil.rmtree(NEW_TESTS_DIR)
    shutil.copytree(OLD_TESTS_DIR, NEW_TESTS_DIR, dirs_exist_ok=True)

    width = len(str(len(tests)))
    for test_id, test in enumerate(tests):
        test_id_str = str(test_id + 1).zfill(width)
        group = test.get("group")

        polygon_input_name = os.path.join(
            NEW_TESTS_DIR,
            POLYGON_INPUT_TEMPLATE.substitute(id=test_id_str, group=group),
        )
        polygon_output_name = os.path.join(
            NEW_TESTS_DIR,
            POLYGON_OUTPUT_TEMPLATE.substitute(id=test_id_str, group=group),
        )
        cms_input_name = os.path.join(
            NEW_TESTS_DIR, CMS_INPUT_TEMPLATE.substitute(id=test_id_str, group=group)
        )
        cms_output_name = os.path.join(
            NEW_TESTS_DIR, CMS_OUTPUT_TEMPLATE.substitute(id=test_id_str, group=group)
        )

        os.rename(polygon_input_name, cms_input_name)
        os.rename(polygon_output_name, cms_output_name)

    shutil.make_archive("cms_tests", "zip", root_dir=NEW_TESTS_DIR)


def get_score_params(
    groups: list[ET.Element], dependencies: dict[str, list[str]]
) -> str:
    """Returns CMS's Score Parameters string."""
    score_params = []
    for group in groups:
        name = group.get("name")
        points = group.get("points")
        if points is None:
            points = 0
        points = int(float(points))
        groups_str = "|".join(dependencies[name])
        score_params.append([points, GROUPS_REGEX.substitute(groups=groups_str)])
    return json.dumps(score_params)


def to_cms():
    """Main function."""
    if len(sys.argv) != 2:
        print("Usage: rename.py [path to Polygon package root]")
        return

    os.chdir(sys.argv[1])

    tree = ET.parse("problem.xml")
    groups = tree.find("judging/testset/groups").findall("group")
    tests = tree.find("judging/testset/tests")

    dependencies = parse_dependencies(groups)
    rename_tests(tests)
    score_params = get_score_params(groups, dependencies)
    with open("score_params.txt", "w", encoding="UTF-8") as file:
        file.write(f"{score_params}")
    print(f"CMS Score Parameters:\n{score_params}")

if __name__ == "__main__":
    to_cms()
