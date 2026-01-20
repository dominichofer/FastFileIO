# FastFileIO

A file I/O benchmarking tool for Python, C++, and Rust.

# Dependencies

- A [Python](https://www.python.org/) interpreter
- A C++ 17 compiler, such as
    - [GCC](https://gcc.gnu.org/)
    - [MSVC](https://visualstudio.microsoft.com/)
- [Rust](https://rust-lang.org/)

# Usage
```bash
./build.sh
```
`build.sh` will build the C++ and Rust programs, create a Python virtual environment and install the required Python packages.
```bash
./run.sh <target_path> [name] [repetitions]
- `target_path`: Path to directory to benchmark file I/O.
- `name` (optional): A prefix for the benchmark name in the log file.
- `repetitions` (optional): Number of times to repeat the benchmark.
```
`run.sh` will run the benchmarks and generate plots of the results.