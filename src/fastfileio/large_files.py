import os
import time
from datetime import datetime
from .format import format_bytes
from .measurements import LargeFileBandwidth, IoDirection

class LargeFileBenchmarker:
    def __init__(self, location: str, name: str, file_size: int, time_limit: int):
        self.location = location
        self.name = name
        self.filename = os.path.join(location, "large_file_test.dat")
        self.file_size = file_size
        self.time_limit = time_limit
        self.rnd_data = os.urandom(file_size)

    def cleanup(self) -> None:
        try:
            os.remove(self.filename)
        except FileNotFoundError:
            pass

    def write_chunk(self, start_pos: int, end_pos: int, block_size: int) -> int:
        bytes_written = 0
        start = time.time()
        with open(self.filename, 'wb') as f:
            f.seek(start_pos)
            for i in range(start_pos, end_pos, block_size):
                bytes_written += f.write(self.rnd_data[i:i + block_size])
                duration = time.time() - start
                if duration > self.time_limit:
                    break
        return bytes_written

    def read_chunk(self, start_pos: int, end_pos: int, block_size: int) -> int:
        bytes_read = 0
        start = time.time()
        with open(self.filename, 'rb') as f:
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

    def bench_write(self, block_size: int) -> LargeFileBandwidth:
        start = time.time()
        bytes_written = self.write_chunk(0, self.file_size, block_size)
        duration = time.time() - start
        bandwidth = bytes_written / duration / (1024**2)  # MiB/s
        print(f"Large files write, {self.location}, block size {format_bytes(block_size)}, {format_bytes(bytes_written)} in {duration:.2f} s, {bandwidth:.0f} MiB/s")
        return LargeFileBandwidth(
            timestamp=datetime.now(),
            location=self.location,
            name=self.name,
            direction=IoDirection.WRITE,
            block_size=block_size,
            bandwidth=bandwidth
        )

    def bench_read(self, block_size: int) -> LargeFileBandwidth:
        start = time.time()
        bytes_read = self.read_chunk(0, self.file_size, block_size)
        duration = time.time() - start
        bandwidth = bytes_read / duration / (1024**2)  # MiB/s
        print(f"Large files read, {self.location}, block size {format_bytes(block_size)}, {format_bytes(bytes_read)} in {duration:.2f} s, {bandwidth:.0f} MiB/s")
        return LargeFileBandwidth(
            timestamp=datetime.now(),
            location=self.location,
            name=self.name,
            direction=IoDirection.READ,
            block_size=block_size,
            bandwidth=bandwidth
        )
    
    def run(self, block_size: int, output_file: str) -> list[LargeFileBandwidth]:
        results = []
        with open(output_file, 'a') as f:
            result = self.bench_write(block_size)
            results.append(result)
            f.write(str(result) + '\n')
            f.flush()
            result = self.bench_read(block_size)
            results.append(result)
            f.write(str(result) + '\n')
            f.flush()
        self.cleanup()
        return results
