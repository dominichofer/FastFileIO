import argparse
import os
import time
import random

def write_file(file_path: str, data: bytes) -> float:
    """Writes data to a file and returns the bandwidth in MiB/s."""
    start = time.time()
    with open(file_path, 'wb') as f:
        f.write(data)
    duration = time.time() - start
    return len(data) / duration / 1024**2

def read_file(file_path: str) -> float:
    """Reads data from a file and returns the bandwidth in MiB/s."""
    start = time.time()
    with open(file_path, 'rb') as f:
        data = f.read()
    duration = time.time() - start
    return len(data) / duration / 1024**2

def write_random_bytes(file_path: str, file_size: int, operations: int, time_limit: int) -> float:
    """Writes random bytes to a file and returns the IOPS."""
    rnd_pos = random.sample(range(file_size), operations)
    bytes_written = 0
    start = time.time()
    with open(file_path, 'r+b') as f:
        for pos in rnd_pos:
            f.seek(pos)
            bytes_written += f.write(b'\0')
            if time.time() - start > time_limit:
                break
    duration = time.time() - start
    return bytes_written / duration

def read_random_bytes(file_path: str, file_size: int, operations: int, time_limit: int) -> float:
    """Reads random bytes from a file and returns the IOPS."""
    rnd_pos = random.sample(range(file_size), operations)
    bytes_read = 0
    start = time.time()
    with open(file_path, 'rb') as f:
        for pos in rnd_pos:
            f.seek(pos)
            data = f.read(1)
            if not data:
                break
            bytes_read += len(data)
            if time.time() - start > time_limit:
                break
    duration = time.time() - start
    return bytes_read / duration

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run file I/O benchmarks')
    parser.add_argument('path', help='Path to benchmark directory')
    parser.add_argument('name', help='Name identifier')
    parser.add_argument('repetitions', type=int, nargs='?', default=1, 
                        help='Number of repetitions (default: 1)')
    args = parser.parse_args()

    path = os.path.expanduser(os.path.expandvars(args.path))
    name = args.name
    
    time_limit = 10  # seconds
    large_file_path = os.path.join(path, "large_file.dat")
    large_file_size = 10 * 2**30  # 10 GiB
    small_file_paths = [os.path.join(path, f"small_file_{i}.dat") for i in range(10_000)]
    small_file_size = 1 * 1**10  # 1 kiB
    rnd_data = os.urandom(large_file_size)
    small_file_data = [os.urandom(small_file_size) for _ in small_file_paths]

    for _ in range(args.repetitions):
        bandwidth = write_file(large_file_path, rnd_data)
        print(f"large file bandwidth, write, {name}, {path}, {bandwidth}")
        bandwidth = read_file(large_file_path)
        print(f"large file bandwidth, read, {name}, {path}, {bandwidth}")

        operations = 100_000
        iops = write_random_bytes(large_file_path, large_file_size, operations, time_limit)
        print(f"random access IOPS, write, {name}, {path}, {iops}")
        iops = read_random_bytes(large_file_path, large_file_size, operations, time_limit)
        print(f"random access IOPS, read, {name}, {path}, {iops}")
        
        bytes_written = 0
        start = time.time()
        for file_path, data in zip(small_file_paths, small_file_data):
            with open(file_path, 'wb') as f:
                bytes_written += f.write(data)
            if time.time() - start > time_limit:
                break
        duration = time.time() - start
        bandwidth = bytes_written / duration / 1024**2
        print(f"small file bandwidth, write, {name}, {path}, {bandwidth}")

        bytes_read = 0
        start = time.time()
        data = [[] for _ in small_file_paths]
        for file_path, d in zip(small_file_paths, small_file_data):
            try:
                with open(file_path, 'rb') as f:
                    d = f.read()
                bytes_read += len(d)
            except FileNotFoundError:
                break
            if time.time() - start > time_limit:
                break
        duration = time.time() - start
        bandwidth = bytes_read / duration / 1024**2
        print(f"small file bandwidth, read, {name}, {path}, {bandwidth}")

    # Cleanup
    os.remove(large_file_path)
    for file_path in small_file_paths:
        if os.path.exists(file_path):
            os.remove(file_path)
