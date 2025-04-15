#!/usr/bin/env python3
"""
Script to switch .cursorrules file between frontend and backend configurations.
Usage: python switch_cursorrules.py [frontend|backend]
"""

import os
import shutil
import sys
from pathlib import Path


def main():
    """
    Main function to handle command line arguments and switch .cursorrules file.
    """
    if len(sys.argv) != 2 or sys.argv[1] not in ["frontend", "backend"]:
        print(
            "Error: Please provide either 'frontend' or 'backend' as the only argument."
        )
        print("Usage: python switch_cursorrules.py [frontend|backend]")
        sys.exit(1)

    package = sys.argv[1]
    root_dir = Path(__file__).parent
    package_dir = root_dir / "packages" / package

    source_file = package_dir / ".cursorrules"
    destination_file = root_dir / ".cursorrules"

    # Verify source file exists
    if not source_file.exists():
        raise FileNotFoundError(f"Could not find .cursorrules file in {package_dir}")

    # Verify destination directory exists
    if not destination_file.parent.exists():
        raise FileNotFoundError(f"Root directory does not exist: {root_dir}")

    # Copy the file
    shutil.copy2(source_file, destination_file)
    print(f"Successfully copied {package} .cursorrules to root directory.")


if __name__ == "__main__":
    main()
