"""Command-line interface for FileShield."""

import sys
from fileshield.file_info import FileInformation


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
    else:
        print("Usage: fileshield info <file_path>")
        sys.exit(1)


if __name__ == "__main__":
    main()
