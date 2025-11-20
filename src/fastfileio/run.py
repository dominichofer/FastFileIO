import os
from .large_files import LargeFileBenchmarker
from .small_files import SmallFilesBenchmarker
from .random_access import RandomAccessBenchmarker
from .measurements import *

def load_config(filepath: str) -> dict:
    config = {
        'time_limit': 5,  # seconds
        'random_accesses': 100_000,
        'small_files_count': 10_000,
        'small_file_size': 1024,  # 1 kiB
        'big_file_size': 10 * 1024**3,  # 10 GiB
        'block_sizes': [2**i for i in range(3, 31)],  # 8 bytes to 1 GiB
    }
    try:
        with open(filepath, 'r') as f:
            for line in f:
                line = line.split('#', 1)[0].strip()
                if '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    if key not in config:
                        continue
                    if isinstance(config.get(key), list):
                        config[key] = [int(x.strip()) for x in value.split(',')]
                    else:
                        config[key] = int(value)
    except FileNotFoundError:
        pass

    print("Config:")
    for key, value in config.items():
        print(f"  {key}: {value}")

    return config

def _setup_paths(location: str, output_file: str, config_file: str):
    """Expand and create necessary paths."""
    location = os.path.expanduser(os.path.expandvars(location))
    output_file = os.path.expanduser(os.path.expandvars(output_file))
    config_file = os.path.expanduser(os.path.expandvars(config_file))
    os.makedirs(location, exist_ok=True)
    return location, output_file, config_file

def run_large_files(location: str, output_file: str, repetitions: int, config_file: str = 'fastfileio.cfg'):
    location, output_file, config_file = _setup_paths(location, output_file, config_file)
    config = load_config(config_file)
    
    bm = LargeFileBenchmarker(location, config['big_file_size'], config['time_limit'])
    for _ in range(repetitions):
        for block_size in config['block_sizes']:
            bm.run(block_size, output_file)
    bm.cleanup()

def run_small_files(location: str, output_file: str, repetitions: int, config_file: str = 'fastfileio.cfg'):
    location, output_file, config_file = _setup_paths(location, output_file, config_file)
    config = load_config(config_file)
    
    bm = SmallFilesBenchmarker(location, config['small_file_size'], config['small_files_count'], config['time_limit'])
    for _ in range(repetitions):
        bm.run(output_file)
    bm.cleanup()

def run_random_access(location: str, output_file: str, repetitions: int, config_file: str = 'fastfileio.cfg'):
    location, output_file, config_file = _setup_paths(location, output_file, config_file)
    config = load_config(config_file)
    
    bm = RandomAccessBenchmarker(location, config['big_file_size'], config['random_accesses'], config['time_limit'])
    for _ in range(repetitions):
        bm.run(output_file)
    bm.cleanup()

def run_all(location: str, output_file: str, repetitions: int = 1, config_file: str = 'fastfileio.cfg'):
    location, output_file, config_file = _setup_paths(location, output_file, config_file)
    config = load_config(config_file)
    
    bm_large = LargeFileBenchmarker(location, config['big_file_size'], config['time_limit'])
    bm_small = SmallFilesBenchmarker(location, config['small_file_size'], config['small_files_count'], config['time_limit'])
    bm_random = RandomAccessBenchmarker(location, config['big_file_size'], config['random_accesses'], config['time_limit'])
    
    for _ in range(repetitions):
        for block_size in config['block_sizes']:
            bm_large.run(block_size, output_file)
        bm_small.run(output_file)
        bm_random.run(output_file)
    
    bm_large.cleanup()
    bm_small.cleanup()
    bm_random.cleanup()
