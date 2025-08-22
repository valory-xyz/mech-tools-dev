#!/usr/bin/env bash

cd mech
# Find the build directory (assumes only one matching directory exists)
build_dir=$(find . -maxdepth 1 -type d -name 'abci_build_*' -print -quit)

# Check if build_dir was found
if [ -z "$build_dir" ]; then
    echo "Failed to find build directory starting with abci_build_ in $(pwd)"
    exit 1
fi

echo "Found deployment build directory: $build_dir"

# Stop the deployment using the found build directory
autonomy deploy stop --build-dir "$build_dir"
