from dataclasses import dataclass
from datetime import datetime
from enum import Enum

class IoDirection(Enum):
    READ = "read"
    WRITE = "write"

@dataclass
class Measurement:
    timestamp: datetime
    location: str
    name: str
    direction: IoDirection

    def __str__(self):
        return f"{self.__class__.__name__}, {self.timestamp}, {self.location}, {self.name}, {self.direction.value}"

@dataclass
class LargeFileBandwidth(Measurement):
    block_size: int
    bandwidth: float # in MB/s

    def __str__(self):
        base_str = super().__str__()
        return f"{base_str}, {self.block_size}, {self.bandwidth}"

@dataclass
class SmallFilesBandwidth(Measurement):
    bandwidth: float # in MB/s

    def __str__(self):
        base_str = super().__str__()
        return f"{base_str}, {self.bandwidth}"

@dataclass
class RandomAccess(Measurement):
    iops: float

    def __str__(self):
        base_str = super().__str__()
        return f"{base_str}, {self.iops}"


def parse_measurement(line: str) -> Measurement:
    parts = line.strip().split(", ")
    measurement_type = parts[0]
    timestamp = datetime.fromisoformat(parts[1])
    location = parts[2]
    name = parts[3]
    direction = IoDirection(parts[4])

    if measurement_type == "LargeFileBandwidth":
        block_size = int(parts[5])
        bandwidth = float(parts[6])
        return LargeFileBandwidth(timestamp, location, name, direction, block_size, bandwidth)
    elif measurement_type == "SmallFilesBandwidth":
        bandwidth = float(parts[5])
        return SmallFilesBandwidth(timestamp, location, name, direction, bandwidth)
    elif measurement_type == "RandomAccess":
        iops = float(parts[5])
        return RandomAccess(timestamp, location, name, direction, iops)
    else:
        raise ValueError(f"Unknown measurement type: {measurement_type}")
