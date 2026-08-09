#!/usr/bin/env python3

import mac_alias
import struct
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
        case "read":
            if len(args) != 2:
                usage()
            run_read(args[1])
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


def run_read(file):
    target = read_alias_target(file)
    print(target)
    


def run_target(file):
    try:
        res = alias_target(file)
    except (ValueError, FileNotFoundError) as e:
        print(f"Error: {e}")
        exit(2)
    if res is None:
        print(f"Error: broken alias for {read_alias_target(file)}")
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


def read_alias_target(file):
    with open(file, "rb") as f:
        magic1, magic2 = struct.unpack(b">4sxxxx4s", f.read(12))
        if magic1 != b"book" or magic2 != b"mark":
            # Invalid bookmark
            return None
        _ = f.read(60) # Read to start of target file path section
        count = 0
        path = []
        while True:
            segment_length = int.from_bytes(f.read(1), byteorder="big")
            _ = f.read(4) # Read to end of path flag
            end_of_path_flag = int.from_bytes(f.read(1), byteorder="big")
            if end_of_path_flag != 1: # End of path seems to be marked 06
                break
            # Not at end of path yet
            _ = f.read(2) # Read to start of path string
            segment = f.read(segment_length).decode("ascii")
            path.append(segment)
            # read to the next half-word boundary
            skip_length = 3 - ((segment_length-1) % 4)
            _ = f.read(skip_length)

        full_path = "".join(["/" + segment for segment in path])
    return full_path


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