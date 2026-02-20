# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
#
#   Copyright 2025-2026 Valory AG
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
# ------------------------------------------------------------------------------

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
