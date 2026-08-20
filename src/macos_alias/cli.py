#!/usr/bin/env python3

import sys
from pathlib import Path

from macos_alias.alias import MacOSAliasHandler


def main(argv=sys.argv):
    args = argv[1:]
    if len(args) == 0:
        usage()

    match args[0].lower():
        case "make":
            if len(args) != 3:
                usage()
            run_make(args[1], args[2])
        case "target":
            if len(args) != 2:
                usage()
            run_target(args[1])
        case _:
            usage()


def run_make(link_to, link_at):
    res = MacOSAliasHandler.update_alias(Path(link_at), Path(link_to))
    if res:
        print("Alias made")
    else:
        print("Failed to make alias")


def run_target(file):
    target = MacOSAliasHandler.read_target(Path(file))
    print(target)


def usage():
    print("Usage:")
    print("  macos_alias.py target <file>")
    print("  macos_alias.py make <link_to> <link_at>")
    sys.exit(10)


if __name__ == "__main__":
    main(sys.argv)
