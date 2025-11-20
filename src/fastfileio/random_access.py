import os
import time
import random
from datetime import datetime
from .format import format_bytes
from .measurements import RandomAccess, IoDirection

class RandomAccessBenchmarker:
    def __init__(self, location: str, file_size: int, sample_size: int, time_limit: int):
        self.location = location
        self.filename = os.path.join(location, "random_access_test_file.dat")
        self.file_size = file_size
        self.sample_size = sample_size
        self.time_limit = time_limit

        with open(self.filename, 'wb') as f:
            f.write(os.urandom(file_size))

    def cleanup(self) -> None:
        try:
            os.remove(self.filename)
        except FileNotFoundError:
            pass

    def bench_write(self) -> RandomAccess:
        positions = random.sample(range(self.file_size), self.sample_size)

        start = time.time()
        writes = 0
        with open(self.filename, 'r+b') as f:
            for pos in positions:
                f.seek(pos)
                writes += f.write(b'\0')
                duration = time.time() - start
                if duration > self.time_limit:
                    break
        duration = time.time() - start
        iops = writes / duration
        print(f"Random writes, {self.location}, {writes} in {duration:.2f} s, {iops:.0f} T/s")
        return RandomAccess(
            timestamp=datetime.now(),
            location=self.location,
            direction=IoDirection.WRITE,
            iops=iops
        )
    
    def bench_read(self) -> RandomAccess:
        positions = random.sample(range(self.file_size), self.sample_size)

        start = time.time()
        reads = 0
        with open(self.filename, 'rb') as f:
            for pos in positions:
                f.seek(pos)
                data = f.read(1)
                reads += len(data)
                duration = time.time() - start
                if duration > self.time_limit:
                    break
        duration = time.time() - start
        iops = reads / duration
        print(f"Random reads, {self.location}, {reads} in {duration:.2f} s, {iops:.0f} T/s")
        return RandomAccess(
            timestamp=datetime.now(),
            location=self.location,
            direction=IoDirection.READ,
            iops=iops
        )
    
    def run(self, output_file: str) -> list[RandomAccess]:
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
        return results
