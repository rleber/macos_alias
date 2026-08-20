#!/usr/bin/env python3

import argparse
import sys
from pathlib import Path

from macos_alias import __version__
from macos_alias.alias import make_alias, target_of


def run_make(args: argparse.Namespace) -> int:
    """Executes the 'make' subcommand to create or update a Finder Alias."""
    success = make_alias(Path(args.link_at), Path(args.link_to))
    if success:
        print("Alias made")
        return 0
    print("Failed to make alias")
    return 1


def run_target(args: argparse.Namespace) -> int:
    """Executes the 'target' subcommand to resolve an alias path."""
    target = target_of(Path(args.file))
    print(target)
    return 0


def build_parser() -> argparse.ArgumentParser:
    """Constructs the CLI argument parser, configures subcommands, and adds version flag."""
    parser = argparse.ArgumentParser(
        prog="macos_alias",
        description="CLI tool for managing macOS Finder Alias (BookmarkData) files.",
    )

    # Built-in version action; exits with 0 upon printing version string
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
        help="Show program's version number and exit.",
    )

    subparsers = parser.add_subparsers(
        dest="command",
        title="subcommands",
        description="Valid operations",
        required=True,
    )

    # Subcommand: make <link_to> <link_at>
    make_parser = subparsers.add_parser(
        "make", help="Create or update an alias file referencing a target path."
    )
    make_parser.add_argument("link_to", help="Target path that the alias points to.")
    make_parser.add_argument(
        "link_at", help="Destination path where the alias file is created."
    )
    make_parser.set_defaults(func=run_make)

    # Subcommand: target <file>
    target_parser = subparsers.add_parser(
        "target", help="Resolve and print the target path of an alias file."
    )
    target_parser.add_argument("file", help="Path to the macOS Finder Alias file.")
    target_parser.set_defaults(func=run_target)

    return parser


def main(argv: list[str] | None = None) -> int:
    """CLI entrypoint accepting explicit argument vectors for testing capability."""
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
