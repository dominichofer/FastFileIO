#!/bin/bash
set -e  # Exit immediately if a command exits with a non-zero status.

# Build binaries
./build.sh

# Install the python packages
rm -rf test_env
python -m venv test_env
if [[ "$OSTYPE" == "msys"* || "$OSTYPE" == "win32" ]]; then
  source test_env/Scripts/activate
else
  source test_env/bin/activate
fi
pip install ./python

# Remove existing log file
rm -f test.log

# Run test for C++
./cpp/build/fastfileio $(pwd) cpp test_config.yaml test.log

# Run test for Rust
./rust/target/release/fastfileio $(pwd) rust test_config.yaml test.log

# Run test for Python
python -m fastfileio $(pwd) python test_config.yaml test.log

# Plot results
python -m plot test.log

# Test that png files exist
png_count=$(ls *.png 2>/dev/null | wc -l || echo 0)
if [ "$png_count" -ne 10 ]; then
    echo "Error: Expected 10 PNG files, but found $png_count."
    exit 1
fi
