# FastFileIO

A file I/O benchmarking tool.

# Benchmarks
## C++
To build the C++ binary into a folder `build`, run
```bash
cmake -S cpp -B build -DCMAKE_BUILD_TYPE=Release
cmake --build cpp/build
```
To run the binary, use
```bash
./cpp/build/fastfileio --help
```

## Rust Benchmark
To build the Rust binary, run
```bash
cd rust
cargo build --release
```
To run the binary, use
```bash
./rust/target/release/fastfileio --help
```

## Python Benchmark
To install the Python package, run
```bash
pip install ./python/
```
To use the package, you can run
```bash
python -m fastfileio --help
```

## Usage
The benchmarks take the following command line arguments:
```
<path> <name> <config_file> <output_file> [repetitions]
```
where
- `<path>` is the directory where the benchmark files will be created,
- `<name>` is a name identifier for the benchmark run (will be included in the output),
- `<config_file>` is the path to a configuration file specifying the benchmark parameters,
- `<output_file>` is the path to a CSV file where the benchmark results will be written,
- `[repetitions]` is an optional argument specifying how many times to repeat the benchmarks (default is 1).

# Plotting