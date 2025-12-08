# FastFileIO - Rust Implementation

A file I/O benchmarking tool written in Rust, translated from the Python version.

## Features

- **Large File Benchmarks**: Test read/write performance with various block sizes
- **Small Files Benchmarks**: Test performance with many small files
- **Random Access Benchmarks**: Measure random I/O operations per second (IOPS)

## Building

```bash
cd rust
cargo build --release
```

## Usage

The compiled binary supports several commands:

### Run all benchmarks
```bash
cargo run --release -- all <location> <name> <output_file> [repetitions] [config_file]
```

### Run large file benchmarks only
```bash
cargo run --release -- large <location> <name> <output_file> [repetitions] [config_file]
```

### Run small files benchmarks only
```bash
cargo run --release -- small <location> <name> <output_file> [repetitions] [config_file]
```

### Run random access benchmarks only
```bash
cargo run --release -- random <location> <name> <output_file> [repetitions] [config_file]
```

## Configuration

Create a `fastfileio.cfg` file to customize benchmark parameters:

```
time_limit = 5
random_accesses = 100000
small_files_count = 10000
small_file_size = 1024
big_file_size = 10737418240
block_sizes = 8, 16, 32, 64, 128, 256, 512, 1024, 2048, 4096, 8192, 16384, 32768, 65536, 131072, 262144, 524288, 1048576, 2097152, 4194304, 8388608, 16777216, 33554432, 67108864, 134217728, 268435456, 536870912, 1073741824
```

## Example

```bash
# Run all benchmarks on C: drive
cargo run --release -- all "C:\temp\benchmark" "C-Drive" results.txt 3

# Run only large file benchmarks
cargo run --release -- large "C:\temp\benchmark" "C-Drive" results.txt 1
```

## Dependencies

- `chrono`: For timestamp handling
- `rand`: For generating random data and positions
- `shellexpand`: For expanding environment variables in paths

## Differences from Python Version

The Rust implementation provides:
- Better memory safety and performance
- No runtime dependencies (compiled binary)
- Cross-platform support
- Similar functionality to the Python version (excluding plotting, which remains in Python)
