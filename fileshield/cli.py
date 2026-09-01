"""Command-line interface for FileShield."""

import sys
from fileshield.file_info import FileInformation
from fileshield.hashing import compute_hashes


def main():
    """Main CLI entry point."""
    if len(sys.argv) < 2:
        print("Usage: fileshield info <file_path>")
        sys.exit(1)

    command = sys.argv[1]

    if command == "info" and len(sys.argv) == 3:
        file_path = sys.argv[2]
        try:
            file_info = FileInformation(file_path)
            file_info.display()
        except FileNotFoundError as e:
            print(f"Error: {e}")
            sys.exit(1)
        except IsADirectoryError as e:
            print(f"Error: {e}")
            sys.exit(1)
    elif command == "hash" and len(sys.argv) == 3:
        file_path = sys.argv[2]
        try:
            # Reuse FileInformation validation
            FileInformation(file_path)
            digests = compute_hashes(file_path, algorithms=("sha256", "sha512"))
            print("\n" + "=" * 60)
            print("FILE HASH")
            print("=" * 60)
            print(f"SHA-256: {digests.get('sha256')}")
            print(f"SHA-512: {digests.get('sha512')}")
            print("=" * 60 + "\n")
        except FileNotFoundError as e:
            print(f"Error: {e}")
            sys.exit(1)
        except IsADirectoryError as e:
            print(f"Error: {e}")
            sys.exit(1)
    else:
        print("Usage: fileshield info <file_path>")
        sys.exit(1)


if __name__ == "__main__":
    main()
