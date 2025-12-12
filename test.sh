#!/bin/bash
set -e  # Exit immediately if a command exits with a non-zero status.

./build.sh

rm -f test.log
./cpp/build/fastfileio $(pwd) cpp test_config.yaml test.log
./rust/target/release/fastfileio $(pwd) rust test_config.yaml test.log
source venv/bin/activate
python -m fastfileio $(pwd) python test_config.yaml test.log

python -m plot test.log
