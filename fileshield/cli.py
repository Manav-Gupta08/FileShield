"""Command-line interface for FileShield."""

import argparse
import json
import sys
import hashlib
from pathlib import Path
from getpass import getpass

from fileshield.file_info import FileInformation
from fileshield.hashing import compute_hashes
from fileshield.detection import detect_file
from fileshield.images import image_metadata, transform_image
from fileshield.archives import analyze_archive
from fileshield.protection import protect_file


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
        print(json.dumps(detect_file(args.file_path), indent=2))
    except FileNotFoundError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except IsADirectoryError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except PermissionError as e:
        print(f"Permission denied: {e}")
        sys.exit(1)
    except (OSError, ValueError) as e:
        print(f"Error: {e}")
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


def cmd_engine(args):
    try:
        if args.command == "metadata":
            result = image_metadata(args.file_path)
        elif args.command == "archives":
            result = analyze_archive(args.file_path)
        elif args.command in {"protect", "decrypt"}:
            password = getpass("Existing password: " if args.command == "decrypt" else "Encryption password: ")
            result = protect_file(args.file_path, args.output, password, args.command == "decrypt")
        elif args.command == "sanitize":
            source = Path(args.file_path)
            output = args.output or str(source.with_name(source.stem + ".cleaned.png"))
            result = transform_image(args.file_path, output, args.format)
            result["output"] = output
        else:
            result = {"detection": detect_file(args.file_path), "hashes": compute_hashes(args.file_path)}
        print(json.dumps(result, indent=2, default=str))
    except (OSError, ValueError, RuntimeError) as error:
        print(f"Error: {error}", file=sys.stderr)
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

    for command in ("metadata", "analyze", "archives", "sanitize", "protect", "decrypt"):
        command_parser = sub.add_parser(command, help=f"{command.capitalize()} a local file")
        command_parser.add_argument("file_path")
        if command == "sanitize":
            command_parser.add_argument("--output")
            command_parser.add_argument("--format", choices=("png", "jpeg", "webp", "tiff"), default="png")
        elif command in {"protect", "decrypt"}:
            command_parser.add_argument("--output", required=True)
        command_parser.set_defaults(func=cmd_engine)

    args = parser.parse_args(argv)
    if not hasattr(args, "func"):
        parser.print_help()
        sys.exit(1)
    args.func(args)


if __name__ == "__main__":
    main()
