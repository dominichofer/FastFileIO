import os
import time
import random
from typing import TextIO
from .config import Config

class RandomAccessBenchmarker:
    def __init__(self, path: str, name: str, config: Config):
        self.path = path
        self.name = name
        self.time_limit = config.time_limit
        self.file_size = config.large_file_size
        self.samples = config.random_accesses
        self.file = os.path.join(path, "random_access_file.dat")

    def bench_write(self) -> int:
        rnd_pos = random.sample(range(self.file_size), self.samples)

        start = time.time()
        writes = 0
        with open(self.file, 'r+b') as f:
            for pos in rnd_pos:
                f.seek(pos)
                writes += f.write(b'\0')
                if time.time() - start > self.time_limit:
                    break
        return writes
    
    def bench_read(self) -> int:
        rnd_pos = random.sample(range(self.file_size), self.samples)

        start = time.time()
        reads = 0
        with open(self.file, 'rb') as f:
            for pos in rnd_pos:
                f.seek(pos)
                data = f.read(1)
                reads += len(data)
                if time.time() - start > self.time_limit:
                    break
        return reads
    
    def run(self, output: TextIO) -> None:
        # Create file with random data
        with open(self.file, 'wb') as f:
            f.write(os.urandom(self.file_size))
        
        # Write
        start = time.time()
        result = self.bench_write()
        duration = time.time() - start
        iops = result / duration
        now = start.strftime("%Y-%m-%d %H:%M:%S")
        output.write(f"random access IOPS, write, {now}, {self.name}, {self.path}, {iops}\n")
        output.flush()

        # Read
        start = time.time()
        result = self.bench_read()
        duration = time.time() - start
        iops = result / duration
        now = start.strftime("%Y-%m-%d %H:%M:%S")
        output.write(f"random access IOPS, read, {now}, {self.name}, {self.path}, {iops}\n")
        output.flush()

        # Cleanup
        os.remove(self.file)
