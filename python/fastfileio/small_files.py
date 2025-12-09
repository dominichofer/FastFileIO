import os
import time
from datetime import datetime
from .config import Config

class SmallFilesBenchmarker:
    def __init__(self, path: str, name: str, config: Config):
        self.path = path
        self.name = name
        self.time_limit = config.time_limit
        self.files = [os.path.join(path, f"small_file_{i}.dat") for i in range(config.small_files_count)]
        self.rnd_data = [bytearray(self.file_size) for _ in range(config.small_files_count)]

    def write_files(self) -> int:
        bytes_written = 0
        start = time.time()
        for file, data in zip(self.files, self.rnd_data):
            with open(file, 'wb') as f:
                bytes_written += f.write(data)
            duration = time.time() - start
            if duration > self.time_limit:
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
                duration = time.time() - start
                if duration > self.time_limit:
                    break
        except FileNotFoundError:
            pass
        return bytes_read

    def bench_write(self) -> SmallFilesBandwidth:
        start = time.time()
        bytes_written = self.write_files()
        duration = time.time() - start
        bandwidth = bytes_written / duration / (1024**2)  # MiB/s
        print(f"Small files write, {self.location}, {format_bytes(bytes_written)} in {duration:.2f} s, {bandwidth:.0f} MiB/s")
        return SmallFilesBandwidth(
            timestamp=datetime.now(),
            location=self.location,
            name=self.name,
            direction=IoDirection.WRITE,
            bandwidth=bandwidth
        )

    def bench_read(self) -> SmallFilesBandwidth:
        start = time.time()
        bytes_read = self.read_files()
        duration = time.time() - start
        bandwidth = bytes_read / duration / (1024**2)  # MiB/s
        print(f"Small files read, {self.location}, {format_bytes(bytes_read)} in {duration:.2f} s, {bandwidth:.0f} MiB/s")
        return SmallFilesBandwidth(
            timestamp=datetime.now(),
            location=self.location,
            name=self.name,
            direction=IoDirection.READ,
            bandwidth=bandwidth
        )

    def run(self, output_file: str) -> list[SmallFilesBandwidth]:
        results = []
        with open(output_file, 'a') as f:
            result = self.bench_write()
            results.append(result)
            f.write(str(result) + '\n')
            f.flush()
            result = self.bench_read()
            results.append(result)
            f.write(str(result) + '\n')
            f.flush()
        self.cleanup()
        return results
