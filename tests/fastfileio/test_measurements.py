import unittest
from datetime import datetime
from fastfileio.measurements import *

class TestMeasurements(unittest.TestCase):
    def test_serialization(self):
        measurements = [
            LargeFileBandwidth(
                timestamp=datetime(2024, 1, 1, 12, 0, 0),
                location="/data/largefile",
                direction=IoDirection.READ,
                block_size=4096,
                bandwidth=150.5
            ),
            SmallFilesBandwidth(
                timestamp=datetime(2024, 1, 1, 12, 5, 0),
                location="/data/smallfiles",
                direction=IoDirection.WRITE,
                block_size=512,
                bandwidth=75.0
            ),
            RandomAccess(
                timestamp=datetime(2024, 1, 1, 12, 10, 0),
                location="/data/randomaccess",
                direction=IoDirection.READ,
                iops=2000.0
            )
        ]

        # Serialize
        string = "\n".join(str(m) for m in measurements)

        # Deserialize
        parsed_measurements = [parse_measurement(line) for line in string.split("\n")]

        self.assertEqual(measurements, parsed_measurements)
