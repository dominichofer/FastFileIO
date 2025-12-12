import yaml
from dataclasses import dataclass

@dataclass
class Config:
    time_limit: int
    random_accesses: int
    small_file_count: int
    small_file_size: int
    large_file_size: int
    block_sizes: list[int]

    @classmethod
    def load(cls, path: str) -> 'Config':
        with open(path, 'r') as f:
            content = yaml.safe_load(f)
        return cls(**content)
