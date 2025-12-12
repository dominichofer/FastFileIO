import os
import time
from typing import TextIO
from .config import Config

class LargeFileBenchmarker:
    def __init__(self, path: str, name: str, config: Config):
        self.path = path
        self.name = name
        self.time_limit = config.time_limit
        self.file_size = config.large_file_size
        self.block_size = config.block_sizes
        self.file = os.path.join(path, "large_file.dat")
        self.rnd_data = bytearray(config.large_file_size)

    def write_chunk(self, start_pos: int, end_pos: int, block_size: int) -> int:
        bytes_written = 0
        start = time.time()
        with open(self.file, 'wb') as f:
            f.seek(start_pos)
            for i in range(start_pos, end_pos, block_size):
                bytes_written += f.write(self.rnd_data[i:i + block_size])
                if time.time() - start > self.time_limit:
                    break
        return bytes_written

    def read_chunk(self, start_pos: int, end_pos: int, block_size: int) -> int:
        bytes_read = 0
        start = time.time()
        with open(self.file, 'rb') as f:
            f.seek(start_pos)
            for _ in range(start_pos, end_pos, block_size):
                data = f.read(block_size)
                if not data:
                    break
                bytes_read += len(data)
                duration = time.time() - start
                if duration > self.time_limit:
                    break
        return bytes_read
    
    def run(self, output: TextIO) -> None:
        for block_size in self.block_size:
            # Prepare random data
            self.rnd_data = os.urandom(self.file_size)

            # Write
            start = time.time()
            result = self.write_chunk(0, self.file_size, block_size)
            duration = time.time() - start
            bandwidth = result / duration
            output.write(f"large file bandwidth, write, {self.name}, {self.path}, {block_size}, {bandwidth}\n")
            output.flush()

            # Read
            start = time.time()
            result = self.read_chunk(0, self.file_size, block_size)
            duration = time.time() - start
            bandwidth = result / duration
            output.write(f"large file bandwidth, read, {self.name}, {self.path}, {block_size}, {bandwidth}\n")
            output.flush()

        # Cleanup
        os.remove(self.file)
