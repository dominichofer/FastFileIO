# FastFileIO - C++ Implementation

This is the C++ implementation of the FastFileIO benchmarking suite. It provides the same benchmarking capabilities as the Python version, outputting results in a compatible format.

## Features

- **Large File Benchmarks**: Sequential read/write with varying block sizes (2³ to 2³⁰ bytes)
- **Small Files Benchmarks**: Operations on 10,000 small files (1 KiB each)
- **Random Access Benchmarks**: Random read/write operations (100,000 operations)
- **Compatible Output**: Produces log files compatible with Python plotting tools
- **Configurable**: Supports configuration files for parameter customization

## Requirements

- C++17 compatible compiler (GCC 7+, Clang 5+, MSVC 2017+)
- CMake 3.15 or higher
- Linux/Unix system (uses POSIX filesystem APIs)

## Building

```bash
# From the cpp/ directory
mkdir build
cd build
cmake ..
make

# Or with specific build type
cmake -DCMAKE_BUILD_TYPE=Release ..
make
```

The executable will be created as `build/fastfileio`.

## Usage

### Basic Usage

Run all benchmarks:
```bash
./fastfileio --location /path/to/test --name scratch --output scratch.log
```

### Command Line Options

- `--location PATH` : Directory where benchmark files will be created (required)
- `--name NAME` : Friendly name for the location, e.g., 'scratch', 'home' (required)
- `--output FILE` : Output log file (default: `output.log`)
- `--config FILE` : Optional configuration file
- `--large-files` : Run only large files benchmark
- `--small-files` : Run only small files benchmark
- `--random-access` : Run only random access benchmark
- `--help` : Show help message

### Examples

Run all benchmarks on scratch storage:
```bash
./fastfileio --location /scratch/user --name scratch --output scratch.log
```

Run only large file benchmarks:
```bash
./fastfileio --location /tmp --name tmp --output tmp.log --large-files
```

Use custom configuration:
```bash
./fastfileio --location /home/user --name home --output home.log --config ../config.txt
```

## Configuration File

The configuration file uses a simple `key=value` format compatible with the Python version:

```
time_limit=5.0
random_accesses=100000
small_files_count=10000
small_file_size=1024
big_file_size=10737418240
```

Lines starting with `#` are treated as comments.

## Output Format

The benchmark produces log files with measurements in CSV format:
```
2024-12-03T10:15:30.123Z,/path/to/file,scratch,WRITE,1048576,523.45
```

Fields:
1. Timestamp (ISO 8601 format)
2. File path
3. Location name
4. Direction (READ or WRITE)
5. Block size (for large files) or bandwidth/IOPS
6. Measured bandwidth (MiB/s) or IOPS

## Visualization

Use the Python plotting tools to visualize results:
```bash
cd ..
python -c "import fastfileio; fastfileio.plot('cpp_results.log')"
```

## Architecture

```
cpp/
├── CMakeLists.txt          # Build configuration
├── README.md               # This file
├── include/fastfileio/     # Header files
│   ├── measurements.h    # Measurement data structures
│   ├── format.h          # Formatting utilities
│   ├── large_files.h     # Large file benchmarker
│   ├── small_files.h     # Small files benchmarker
│   ├── random_access.h   # Random access benchmarker
│   └── run.h             # Main orchestration
└── src/                    # Implementation files
    ├── measurements.cpp
    ├── format.cpp
    ├── large_files.cpp
    ├── small_files.cpp
    ├── random_access.cpp
    ├── run.cpp
    └── main.cpp            # CLI entry point
```

## Implementation Notes

- Uses C++17 filesystem library for portable path handling
- Random data is pre-generated to avoid timing bias
- Time limits prevent hung tests (default: 5 seconds per operation)
- Results are flushed immediately for crash resistance
- Compatible with Python's measurement format for unified plotting

## Performance Considerations

- The C++ implementation uses standard library I/O (`<fstream>`)
- For maximum performance, consider:
  - Using POSIX APIs (`open`, `read`, `write`) directly
  - Using `io_uring` for async I/O on modern Linux kernels
  - Adjusting filesystem mount options and caching
  - Using O_DIRECT flag to bypass page cache

## Comparison with Python

The C++ implementation aims to:
- Produce identical measurement formats
- Use the same default parameters
- Follow the same benchmark methodology
- Enable cross-language performance comparison

Differences:
- C++ uses native I/O APIs vs Python's buffered I/O
- Memory management is explicit in C++
- May show different performance characteristics due to runtime overhead differences
