import os
import time
from datetime import datetime
from .format import format_bytes
from .measurements import SmallFilesBandwidth, IoDirection

class SmallFilesBenchmarker:
    def __init__(self, location: str, name: str, file_size: int, files_count: int, time_limit: int):
        self.location = location
        self.name = name
        self.file_size = file_size
        self.files = [os.path.join(location, f"smallfile_{i}.dat") for i in range(files_count)]
        self.time_limit = time_limit
        self.rnd_data = [os.urandom(file_size) for _ in range(files_count)]

    def cleanup(self) -> None:
        for file in self.files:
            try:
                os.remove(file)
            except FileNotFoundError:
                pass

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
