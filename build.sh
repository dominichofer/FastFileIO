#!/bin/bash

# C++
cmake -S cpp -B build -DCMAKE_BUILD_TYPE=Release
cmake --build cpp/build

# Rust
cd rust
cargo build --release
cd ..
