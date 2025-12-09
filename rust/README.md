# FastFileIO - Rust Implementation

A file I/O benchmarking tool written in Rust.

## Features

- **Large File Benchmarks**: Test read/write performance with various block sizes
- **Small Files Benchmarks**: Test performance with many small files
- **Random Access Benchmarks**: Measure random I/O operations per second (IOPS)

## Building

```bash
cargo build --release
```

## Usage

```bash
cargo run --release -- <path> <name> <config_file> <output_file> [repetitions]
```

## Example

```bash
# Run 10 repetitions on C: drive
cargo run --release -- "C:\temp\benchmark" "C-Drive" config.yaml results.txt 10
```
