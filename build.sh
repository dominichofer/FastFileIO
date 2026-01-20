#!/bin/bash

# C++
cmake -S cpp -B cpp/build -DCMAKE_BUILD_TYPE=Release
cmake --build cpp/build

# Rust
cd rust
cargo build --release
cd ..

# Python
python -m venv venv
if [[ "$OSTYPE" == "msys"* || "$OSTYPE" == "win32" ]]; then
  source venv/Scripts/activate
else
  source venv/bin/activate
fi
pip install -e ./python
