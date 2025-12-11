import os
import time
from typing import TextIO
from .config import Config

class SmallFilesBenchmarker:
    def __init__(self, path: str, name: str, config: Config):
        self.path = path
        self.name = name
        self.time_limit = config.time_limit
        self.file_size = config.small_file_size
        self.files = [os.path.join(path, f"small_file_{i}.dat") for i in range(config.small_file_count)]
        self.rnd_data = []

    def write_files(self) -> int:
        bytes_written = 0
        start = time.time()
        for file, data in zip(self.files, self.rnd_data):
            with open(file, 'wb') as f:
                bytes_written += f.write(data)
            if time.time() - start > self.time_limit:
                break
        return bytes_written

    def read_files(self) -> int:
        bytes_read = 0
        start = time.time()
        try:
            for file in self.files:
                with open(file, 'rb') as f:
                    data = f.read()
                    if not data:
                        break
                    bytes_read += len(data)
                if time.time() - start > self.time_limit:
                    break
        except FileNotFoundError:
            pass
        return bytes_read

    def run(self, output: TextIO) -> None:
        # Prepare random data
        self.rnd_data = [os.urandom(self.file_size) for _ in self.files]

        # Write
        start = time.time()
        result = self.write_files()
        duration = time.time() - start
        bandwidth = result / duration
        now = start.strftime("%Y-%m-%d %H:%M:%S")
        output.write(f"small files bandwidth, write, {now}, {self.name}, {self.path}, {bandwidth}\n")
        output.flush()

        # Read
        start = time.time()
        result = self.read_files()
        duration = time.time() - start
        bandwidth = result / duration
        now = start.strftime("%Y-%m-%d %H:%M:%S")
        output.write(f"small files bandwidth, read, {now}, {self.name}, {self.path}, {bandwidth}\n")
        output.flush()

        # Cleanup
        for file in self.files:
            try:
                os.remove(file)
            except FileNotFoundError:
                pass
