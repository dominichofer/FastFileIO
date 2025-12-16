import argparse
import matplotlib.pyplot as plt
from dataclasses import dataclass


def clamp(value: float, min_value: float, max_value: float) -> float:
    return max(min_value, min(value, max_value))


def format_bytes(value: int) -> str:
    """Format size in bytes to KiB, MiB, or GiB"""
    if value >= 1024**3:
        return f"{int(value / (1024**3)):_} GiB".replace("_", "'")
    elif value >= 1024**2:
        return f"{int(value / (1024**2)):_} MiB".replace("_", "'")
    elif value >= 1024:
        return f"{int(value / 1024):_} KiB".replace("_", "'")
    else:
        return f"{value:_} B".replace("_", "'")
    
@dataclass
class LargeFileBandwidth:
    direction: str
    name: str
    path: str
    block_size: int
    bandwidth: float

@dataclass
class SmallFilesBandwidth:
    direction: str
    name: str
    path: str
    bandwidth: float

@dataclass
class RandomAccess:
    direction: str
    name: str
    path: str
    iops: float
    

def plot_large_file_bandwidth(data: list[LargeFileBandwidth], names: set[str]) -> None:
    """Plot large file bandwidth for each block size. One plot per direction and location."""
    for name in names:
        for direction in ['read', 'write']:
            filtered_data = [m for m in data if m.name == name and m.direction == direction]
            block_sizes = sorted(set(m.block_size for m in filtered_data))
            plt.figure()
            for block_size in block_sizes:
                bs_data = [m.bandwidth for m in filtered_data if m.block_size == block_size]
                if not bs_data:
                    continue
                x = [block_size] * len(bs_data)
                plt.scatter(x, bs_data, alpha=clamp(2.0/len(bs_data), 0, 1), color='green')
            
            plt.xscale('log', base=2)
            plt.xticks(block_sizes, [format_bytes(bs) for bs in block_sizes], rotation=90)
            plt.xlabel('Block Size')

            plt.ylabel('Bandwidth (MiB/s)')
            plt.ylim(bottom=0)
            ax = plt.gca()
            ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{int(x/1024**2):_}'.replace("_", "'")))

            plt.title(f'{direction.capitalize()} bandwidth of large files on {name}')
            plt.grid(True, which="both", ls="--")
            plt.tight_layout()
            plt.savefig(f"large_files_{direction}_bandwidth_{name}.png")
            plt.close()


def plot_small_file_bandwidth(data: list[SmallFilesBandwidth], names: set[str]) -> None:
    """Plot small files bandwidth for each location. One plot per direction."""
    for direction in ['read', 'write']:
        plt.figure()
        for name in names:
            bandwidths = [m.bandwidth for m in data if m.name == name and m.direction == direction]
            if not bandwidths:
                continue
            x = [name] * len(bandwidths)
            plt.scatter(x, bandwidths, alpha=clamp(2.0/len(bandwidths), 0, 1), color='blue')
            
        plt.ylabel('Small files bandwidth (MiB/s)')
        plt.ylim(bottom=0)
        ax = plt.gca()
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{int(x/1024**2):_}'.replace("_", "'")))

        plt.xticks(rotation=45, ha='right')
        plt.title(f'{direction.capitalize()} bandwidth of small files')
        plt.grid(True, which="both", ls="--")
        plt.tight_layout()
        plt.savefig(f"small_files_{direction}_bandwidth.png") 
        plt.close()

def plot_random_access(data: list[RandomAccess], names: set[str]) -> None:
    """Plot random access transfers for each location. One plot per direction."""
    for direction in ['read', 'write']:
        plt.figure()
        for name in names:
            iops = [m.iops for m in data if m.name == name and m.direction == direction]
            if not iops:
                continue
            x = [name] * len(iops)
            plt.scatter(x, iops, alpha=clamp(2.0/len(data), 0, 1), color='red')

        plt.ylabel('Transfers per second (IOPS)')
        plt.yscale('log')
        ax = plt.gca()
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{int(x):_}'.replace("_", "'")))
        
        plt.xticks(rotation=45, ha='right')
        plt.title(f'Random {direction} operations per second')
        plt.grid(True, which="both", ls="--")
        plt.tight_layout()
        plt.savefig(f"random_{direction}.png")
        plt.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Plot file I/O benchmarks')
    parser.add_argument('results_file', help='Path to results file')
    parser.add_argument('--names', nargs='*', help='Names to plot (default: all detected)')
    args = parser.parse_args()

    large_file_bandwidth = []
    small_file_bandwidth = []
    random_access_iops = []
    name_set = set()
    with open(args.results_file, 'r') as f:
        for line in f:
            line = line.strip().split(',')
            line = [item.strip() for item in line]
            mode, direction, name, path, *_ = line
            name_set.add(name)

            if mode == "large file bandwidth":
                block_size = int(line[4])
                bandwidth = float(line[5])
                large_file_bandwidth.append(LargeFileBandwidth(direction, name, path, block_size, bandwidth))
            elif mode == "small files bandwidth":
                bandwidth = float(line[4])
                small_file_bandwidth.append(SmallFilesBandwidth(direction, name, path, bandwidth))
            elif mode == "random access IOPS":
                iops = float(line[4])
                random_access_iops.append(RandomAccess(direction, name, path, iops))
            

    if args.names:
        names = set(args.names)
    else:
        names = name_set

    print(f"Detected names: {names}")

    plot_large_file_bandwidth(large_file_bandwidth, names)
    plot_small_file_bandwidth(small_file_bandwidth, names)
    plot_random_access(random_access_iops, names)
