"""The command line interface for polygon_convert. The command is `polyconv`."""

import sys
from argparse import ArgumentParser, Namespace
from pathlib import Path

from polyconv.test_data import DEFAULT_OUT_DIR, generate_cms_tests


def make_parser() -> ArgumentParser:
    """Create the command line parser for the polygon_convert CLI.

    Returns:
        ArgumentParser: _description_
    """
    parser = ArgumentParser()
    parser.add_argument("polygon_path", help="Path to the Polygon package folder.")
    parser.add_argument(
        "--force", "-f", action="store_true", help="Force overwrite existing tests."
    )
    parser.add_argument(
        "--out",
        "-o",
        type=str,
        default=None,
        help=f"Path to the output folder. Defaults to <polygon_path>/{DEFAULT_OUT_DIR}.",
    )
    return parser


def generate_test_data(args: Namespace):
    """Generate test data and score parameters for CMS from Polygon tests."""
    polygon_path = Path(args.polygon_path).resolve()
    score_params = generate_cms_tests(
        polygon_path, output_path=args.out, overwrite=args.force
    )
    print(f"CMS Score Parameters:\n{score_params}")


def main():
    """Main function to run the CLI."""
    try:
        parser = make_parser()
        args = parser.parse_args()
        generate_test_data(args)
    except (FileExistsError, ValueError) as e:
        print(f"Error: {e}")
        sys.exit(1)
