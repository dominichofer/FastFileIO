#!/bin/bash
set -e  # Exit immediately if a command exits with a non-zero status.

if [ "$#" -lt 1 ]; then
    echo "Usage: $0 <target_path> [name] [repetitions]"
    exit 1
fi
TARGET_PATH=$1
NAME=${2:-""}
if [ -n "$NAME" ]; then
    NAME="${NAME}_"
fi
REPETITIONS=${3:-""}

# Benchmark C++
./cpp/build/fastfileio ${TARGET_PATH} ${NAME}cpp $REPETITIONS | tee -a log.txt

# Benchmark Rust
./rust/target/release/fastfileio ${TARGET_PATH} ${NAME}rust $REPETITIONS | tee -a log.txt

# Benchmark Python
if [[ "$OSTYPE" == "msys"* || "$OSTYPE" == "win32" ]]; then
  source venv/Scripts/activate
else
  source venv/bin/activate
fi
python -m fastfileio ${TARGET_PATH} ${NAME}python $REPETITIONS | tee -a log.txt

# Plot
python -m plot log.txt
