"""Command-line interface for FileShield."""

import argparse
import json
import sys
import hashlib

from fileshield.file_info import FileInformation
from fileshield.hashing import compute_hashes


def parse_algorithms(value: str):
    """Parse comma-separated algorithm names and validate availability.

    Returns a tuple of algorithm names to pass to `compute_hashes`.
    Raises ValueError if any algorithm is not supported by hashlib.
    """
    names = [s.strip().lower() for s in value.split(",") if s.strip()]
    if not names:
        raise ValueError("No algorithms specified")

    # Validate by attempting to create a new hasher
    valid = []
    for name in names:
        try:
            hashlib.new(name)
            valid.append(name)
        except (ValueError, TypeError):
            raise ValueError(f"Unsupported hash algorithm: {name}")
    return tuple(valid)


def cmd_info(args):
    try:
        fi = FileInformation(args.file_path)
        fi.display()
    except FileNotFoundError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except IsADirectoryError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except PermissionError as e:
        print(f"Permission denied: {e}")
        sys.exit(1)


def cmd_hash(args):
    try:
        FileInformation(args.file_path)

        algorithms = parse_algorithms(args.algorithms) if args.algorithms else ("sha256", "sha512")

        digests = compute_hashes(args.file_path, algorithms=algorithms)

        if args.json:
            out = {"file": args.file_path, "hashes": digests}
            print(json.dumps(out, indent=2))
        else:
            print("\n" + "=" * 60)
            print("FILE HASH")
            print("=" * 60)
            for name, value in digests.items():
                print(f"{name.upper()}: {value}")
            print("=" * 60 + "\n")

    except FileNotFoundError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except IsADirectoryError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except PermissionError as e:
        print(f"Permission denied: {e}")
        sys.exit(1)
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)


def main(argv=None):
    parser = argparse.ArgumentParser(prog="fileshield")
    sub = parser.add_subparsers(dest="command")

    p_info = sub.add_parser("info", help="Show basic file information")
    p_info.add_argument("file_path", help="Path to the file")
    p_info.set_defaults(func=cmd_info)

    p_hash = sub.add_parser("hash", help="Compute cryptographic hashes for a file")
    p_hash.add_argument("file_path", help="Path to the file")
    p_hash.add_argument("--algorithms", "-a", help="Comma-separated algorithms (default: sha256,sha512)")
    p_hash.add_argument("--json", action="store_true", help="Output results in JSON format")
    p_hash.set_defaults(func=cmd_hash)

    args = parser.parse_args(argv)
    if not hasattr(args, "func"):
        parser.print_help()
        sys.exit(1)
    args.func(args)


if __name__ == "__main__":
    main()
