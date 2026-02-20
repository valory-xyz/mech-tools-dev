# -*- coding: utf-8 -*-
"""Backward-compatible wrapper for metadata generation."""

from pathlib import Path

from mtd.services.metadata.generate import generate_metadata


ROOT_DIR = "./packages"
METADATA_FILE_PATH = "metadata.json"


def main() -> None:
    """Run the generate_metadata script."""
    generate_metadata(
        packages_dir=Path(ROOT_DIR), metadata_path=Path(METADATA_FILE_PATH)
    )


if __name__ == "__main__":
    main()
