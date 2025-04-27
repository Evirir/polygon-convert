"""Creates a folder and zip file containing tests in CMS format and
outputs the Score Parameters string."""

import json
import shutil
import xml.etree.ElementTree as ET
from pathlib import Path
from string import Template

POLYGON_TESTS_DIR = "tests"
DEFAULT_CMS_TESTS_DIR = "cms_tests"
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


def rename_tests(
    tests: ET.Element[str],
    polygon_path: Path,
    output_path: Path,
    overwrite: bool = False,
) -> None:
    """Create a copy of tests from Polygon and rename them to CMS format with groups appended,
    in a zip file.

    Args:
        tests (ET.Element): The tests element from the XML tree.
        polygon_path (Path): The path to the Polygon package folder.
        output_path (Path): The path to the output folder.
        overwrite (bool, optional): If True, overwrite the existing tests. If not, raise an error
            if the folder already exists. Defaults to False.
    """

    # Check if cms_tests/ exists, delete if true
    if output_path.exists():
        if not overwrite:
            raise FileExistsError(
                "The output folder already exists. Delete it or use the --force flag to overwrite."
            )

        shutil.rmtree(output_path)
    shutil.copytree(polygon_path / POLYGON_TESTS_DIR, output_path, dirs_exist_ok=True)

    cms_tests_dir = output_path / DEFAULT_CMS_TESTS_DIR

    width = len(str(len(tests)))
    for test_id, test in enumerate(tests):
        test_id_str = str(test_id + 1).zfill(width)
        group = test.get("group")

        polygon_input_name = cms_tests_dir / POLYGON_INPUT_TEMPLATE.substitute(
            id=test_id_str, group=group
        )
        polygon_output_name = cms_tests_dir / POLYGON_OUTPUT_TEMPLATE.substitute(
            id=test_id_str, group=group
        )
        cms_input_name = cms_tests_dir / CMS_INPUT_TEMPLATE.substitute(
            id=test_id_str, group=group
        )
        cms_output_name = cms_tests_dir / CMS_OUTPUT_TEMPLATE.substitute(
            id=test_id_str, group=group
        )

        polygon_input_name.rename(cms_input_name)
        polygon_output_name.rename(cms_output_name)

    shutil.make_archive("cms_tests", "zip", root_dir=cms_tests_dir)


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


def generate_cms_tests(
    polygon_path: Path, output_path: Path = None, overwrite: bool = False
) -> str:
    """Copy and rename tests from Polygon to CMS format. Create a folder with the tests
    and a zip file with the tests. Returns the Score Parameters string.

    The tests are renamed to CMS format with groups appended. The Score Parameters string implements
    Polygon's subtask dependencies.

    Args:
        polygon_path (Path): The path to the Polygon package folder.
        output_path (Path, optional): The path to the output folder. If None, this will be
            `<polygon_path>/cms_out`. Defaults to None.
        overwrite (bool, optional): If True, overwrite the existing tests. Defaults to False.
    """
    if output_path is None:
        output_path = polygon_path / "cms_out"

    tree = ET.parse(polygon_path / "problem.xml")
    groups = tree.find("judging/testset/groups").findall("group")
    tests = tree.find("judging/testset/tests")
    if tests is None:
        raise ValueError("No tests found in problem.xml.")

    dependencies = parse_dependencies(groups)
    rename_tests(tests, polygon_path, output_path, overwrite=overwrite)
    score_params = get_score_params(groups, dependencies)
    with open("score_params.txt", "w", encoding="UTF-8") as file:
        file.write(f"{score_params}")
    return score_params
