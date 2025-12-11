# FastFileIO

A file I/O benchmarking tool.

# C++
To build the C++ binary into a folder `build`, run
```bash
cmake -S cpp -B build
cmake --build build
```
To run the provided tests, execute
```bash
make -C build test
```
(The GitHub actions run them on every commit.)<br>
To run the binary, use
```bash
./cpp/build/FastFileIO --help
```

# Rust
To build the Rust binary, run
```bash
cd rust
cargo build --release
```
To run the provided tests, execute
```bash
cd rust
cargo test
```
(The GitHub actions run them on every commit.)<br>
To run the binary, use
```bash
./rust/target/release/fastfileio --help
```

# Python
To install the Python package, run
```bash
cd python
pip install python

# Usage
The applications take the following command line arguments:
```
<path> <name> <config_file> <output_file> [repetitions]
```
where
- `<path>` is the directory where the benchmark files will be created,
- `<name>` is a name identifier for the benchmark run (will be included in the output),
- `<config_file>` is the path to a configuration file specifying the benchmark parameters,
- `<output_file>` is the path to a CSV file where the benchmark results will be written,
- `[repetitions]` is an optional argument specifying how many times to repeat the benchmarks (default is 1).

## C++
To run the C++ benchmark binary, execute
```bash
./build/FastFileIO <path> <name> <config_file> <output_file> [repetitions]
```

## Rust
To run the Rust benchmark binary, execute
```bash
./target/release/fast_file_io <path> <name> <config_file> <output_file> [repetitions]
```

## Python