#!/usr/bin/env python3

import subprocess
import sys

def main(args):
    if len(args) != 1:
        print("Usage: is_alias.py <file>")
        exit(1)
    try:
        res = is_alias(args[0])
    except ValueError as e:
        print(f"Error: {e}")
        exit(2)

    if res:
        print(f"{args[0]} is an alias.")
        exit(0)
    else:
        print(f"{args[0]} is not an alias.")
        exit(1)

def is_alias(file):
    result = subprocess.run(["is_alias", file], capture_output=True, text=True)
    match result.returncode:
        case 0:
            return True
        case 1:
            return False
        case _:
            raise ValueError(result.stdout.strip())


if __name__ == "__main__":
    main(sys.argv[1:])