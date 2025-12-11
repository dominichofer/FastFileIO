import argparse
import os
from .config import Config
from .large_files import LargeFileBenchmarker
from .small_files import SmallFilesBenchmarker
from .random_access import RandomAccessBenchmarker

def run(path: str, name: str, config_file: str, output_file: str, repetitions: int = 1) -> None:
    # Expand paths
    location = os.path.expanduser(os.path.expandvars(path))
    output_file = os.path.expanduser(os.path.expandvars(output_file))
    config_file = os.path.expanduser(os.path.expandvars(config_file))

    os.makedirs(location, exist_ok=True)

    config = Config.load(config_file)
    large_benchmarker = LargeFileBenchmarker(path, name, config)
    small_benchmarker = SmallFilesBenchmarker(path, name, config)
    random_benchmarker = RandomAccessBenchmarker(path, name, config)

    with open(output_file, 'a') as output:
        for _ in range(repetitions):
            large_benchmarker.run(output)
            small_benchmarker.run(output)
            random_benchmarker.run(output)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run file I/O benchmarks')
    parser.add_argument('path', help='Path to benchmark directory')
    parser.add_argument('name', help='Benchmark name')
    parser.add_argument('config_file', help='Path to configuration file')
    parser.add_argument('output_file', help='Path to output file')
    parser.add_argument('repetitions', default=1, 
                        help='Number of repetitions (default: 1)')
    
    args = parser.parse_args()
    run(args.path, args.name, args.config_file, args.output_file, args.repetitions)
