import argparse
import os
from .config import Config
from .large_files import LargeFileBenchmarker
from .small_files import SmallFilesBenchmarker
from .random_access import RandomAccessBenchmarker

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run file I/O benchmarks')
    parser.add_argument('path', help='Path to benchmark directory')
    parser.add_argument('name', help='Benchmark name')
    parser.add_argument('config_file', help='Path to configuration file')
    parser.add_argument('output_file', help='Path to output file')
    parser.add_argument('repetitions', type=int, nargs='?', default=1, 
                        help='Number of repetitions (default: 1)')
    args = parser.parse_args()
    
    # Expand paths
    path = os.path.expanduser(os.path.expandvars(args.path))
    config_file = os.path.expanduser(os.path.expandvars(args.config_file))
    output_file = os.path.expanduser(os.path.expandvars(args.output_file))

    os.makedirs(path, exist_ok=True)

    config = Config.load(config_file)
    print("Running with:")
    print(f"  Path: {path}")
    print(f"  Name: {args.name}")
    print(f"  Config file: {config_file}")
    print(f"  Output file: {output_file}")
    print(f"  Repetitions: {args.repetitions}")
    print(f"  Time limit: {config.time_limit} seconds")
    print(f"  Random accesses: {config.random_accesses}")
    print(f"  Small file count: {config.small_file_count}")
    print(f"  Small file size: {config.small_file_size} bytes")
    print(f"  Large file size: {config.large_file_size} bytes")
    print(f"  Block sizes: {' '.join(map(str, config.block_sizes))}")

    large_benchmarker = LargeFileBenchmarker(path, args.name, config)
    small_benchmarker = SmallFilesBenchmarker(path, args.name, config)
    random_benchmarker = RandomAccessBenchmarker(path, args.name, config)

    with open(output_file, 'a') as output:
        for _ in range(args.repetitions):
            large_benchmarker.run(output)
            small_benchmarker.run(output)
            random_benchmarker.run(output)
