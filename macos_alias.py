#!/usr/bin/env python3

import subprocess
import sys

class ParentDirectoryNotFoundError(FileNotFoundError):
    pass

def main(args):
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
        case "test":
            if len(args) != 2:
                usage()
            run_test(args[1])
        case _:
            usage()


def run_make(link_to, link_at):
    try:
        res = make_alias(link_to, link_at)
    except (ValueError, FileNotFoundError, FileExistsError, ParentDirectoryNotFoundError) as e:
        print(f"Error: {e}")
        exit(2)
    print("Alias created")


def run_target(file):
    try:
        res = alias_target(file)
    except (ValueError, FileNotFoundError) as e:
        print(f"Error: {e}")
        exit(2)
    if res is None:
        print("Error: broken alias")
        exit(3)
    print(res)


def run_test(file):
    try:
        res = is_alias(file)
    except (ValueError, FileNotFoundError) as e:
        print(f"Error: {e}")
        exit(2)

    if res:
        print(f"{file} is an alias.")
        exit(0)
    else:
        print(f"{file} is not an alias.")
        exit(1)


def usage():
        print("Usage:")
        print("  macos_alias.py test <file>")
        print("  macos_alias.py target <file>")
        print("  macos_alias.py make <link_to> <link_at")
        exit(10)


def make_alias(link_to, link_at):
    result = subprocess.run(["make_alias", link_to, link_at], capture_output=True, text=True)
    match result.returncode:
        case 0: # Success
            pass
        case 1: 
            raise FileNotFoundError(f"{link_to} does not exist")
        case 2:
            raise ValueError(f"{link_to} is an alias. Cannot create aliases of aliases")
        case 3:
            raise FileExistsError(f"{link_at} already exists")
        case 4:
            raise ParentDirectoryNotFoundError(f"A parent directory of {link_at} does not exist")
        case _: # Unknown result or usage error (which shouldn't happen)
            raise RuntimeError(result.stdout.strip())


def alias_target(file):
    result = subprocess.run(["alias_target", file], capture_output=True, text=True)
    match result.returncode:
        case 0:
            return result.stdout.strip()
        case 1:
            raise ValueError(f"{file} is not an alias")
        case 2:
            return None
        case 3:
            raise FileNotFoundError(f"{file} not found")
        case _:
            raise RuntimeError(result.stdout.strip())


def is_alias(file):
    result = subprocess.run(["is_alias", file], capture_output=True, text=True)
    match result.returncode:
        case 0:
            return True
        case 1:
            return False
        case 3:
            raise FileNotFoundError(f"{file} not found")
        case _:
            raise ValueError(result.stdout.strip())


if __name__ == "__main__":
    main(sys.argv[1:])