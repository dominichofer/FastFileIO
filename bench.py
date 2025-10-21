import os
import sys
import time
import random
import json
import shutil
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, asdict
import matplotlib.pyplot as plt

SAMPLE_SIZE = 10_000
TIME_LIMIT = 5  # seconds
SMALL_FILE_SIZE: int = 1024  # 1 KiB
BIG_FILE_SIZE: int = 10 * 1024**3  # 10 GiB
RND_DATA: bytes = os.urandom(BIG_FILE_SIZE)
BLOCK_SIZES: list[int] = [2**x for x in range(3, 31)]  # 8 Bytes to 1 GiB
THREAD_COUNTS = [1, 2, 4, 8, 16]
REPETITIONS = 150


def format_size(size_bytes: int) -> str:
    """Format size in bytes to KiB, MiB, or GiB"""
    if size_bytes >= 1024**3:
        return f"{int(size_bytes / (1024**3)):_} GiB".replace("_", ",")
    elif size_bytes >= 1024**2:
        return f"{int(size_bytes / (1024**2)):_} MiB".replace("_", ",")
    elif size_bytes >= 1024:
        return f"{int(size_bytes / 1024):_} KiB".replace("_", ",")
    else:
        return f"{size_bytes:_} B".replace("_", ",")

def write_chunk(path: str, start_pos: int, end_pos: int, block_size: int) -> int:
    """Write a chunk of file"""
    bytes_written = 0
    start = time.time()
    with open(path, 'wb') as f:
        f.seek(start_pos)
        for i in range(start_pos, end_pos, block_size):
            bytes_written += f.write(RND_DATA[i:i + block_size])
            duration = time.time() - start
            if duration > TIME_LIMIT:
                break
    return bytes_written

def read_chunk(path: str, start_pos: int, end_pos: int, block_size: int) -> int:
    """Read a chunk of file"""
    bytes_read = 0
    start = time.time()
    with open(path, 'rb') as f:
        f.seek(start_pos)
        for _ in range(start_pos, end_pos, block_size):
            data = f.read(block_size)
            if not data:
                raise IOError("Insufficient data read")
            bytes_read += len(data)
            duration = time.time() - start
            if duration > TIME_LIMIT:
                break
    return bytes_read

def bench_write(filename: str) -> dict[int, float]:
    bandwidths = {}
    for block_size in BLOCK_SIZES:
        start = time.time()
        bytes_written = write_chunk(filename, 0, BIG_FILE_SIZE, block_size)
        duration = time.time() - start
        bandwidth = bytes_written / duration / (1024**2)  # MiB/s
        print(f"Block size {format_size(block_size)}: wrote {bytes_written} bytes in {duration:.2f} seconds ({bandwidth:.2f} MiB/s)")

        os.remove(filename)  # Clean up
        bandwidths[block_size] = bandwidth
    return bandwidths

def bench_read(filename: str) -> dict[int, float]:
    bandwidths = {}
    for block_size in BLOCK_SIZES:
        start = time.time()
        bytes_read = read_chunk(filename, 0, BIG_FILE_SIZE, block_size)
        duration = time.time() - start
        bandwidth = bytes_read / duration / (1024**2)  # MiB/s
        print(f"Block size {format_size(block_size)}: read {bytes_read} bytes in {duration:.2f} seconds ({bandwidth:.2f} MiB/s)")

        bandwidths[block_size] = bandwidth

    return bandwidths

def bench_multithreaded_write(filename: str) -> dict[tuple[int, int], float]:
    bandwidths = {}
    for threads in THREAD_COUNTS:
        for block_size in BLOCK_SIZES:
            thread_size = BIG_FILE_SIZE // threads

            start = time.time()
            bytes_written = 0
            processes = []
            with ThreadPoolExecutor(max_workers=threads) as executor:
                for i in range(threads):
                    start_pos = i * thread_size
                    end_pos = (i + 1) * thread_size if i < threads - 1 else BIG_FILE_SIZE
                    processes.append(executor.submit(write_chunk, filename, start_pos, end_pos, block_size))
                for p in processes:
                    bytes_written += p.result()
            duration = time.time() - start
            print(f"{threads} threads, block size {format_size(block_size)}: wrote {bytes_written} bytes in {duration:.2f} seconds")

            bandwidths[(threads, block_size)] = bytes_written / duration / (1024**2)  # MiB/s

            os.remove(filename)  # Clean up
            
    return bandwidths

def bench_multithreaded_read(filename: str) -> dict[tuple[int, int], float]:
    bandwidths = {}
    for threads in THREAD_COUNTS:
        for block_size in BLOCK_SIZES:
            thread_size = BIG_FILE_SIZE // threads

            start = time.time()
            bytes_read = 0
            processes = []
            with ThreadPoolExecutor(max_workers=threads) as executor:
                for i in range(threads):
                    start_pos = i * thread_size
                    end_pos = (i + 1) * thread_size if i < threads - 1 else BIG_FILE_SIZE
                    processes.append(executor.submit(read_chunk, filename, start_pos, end_pos, block_size))
                for p in processes:
                    bytes_read += p.result()
            duration = time.time() - start
            print(f"{threads} threads, block size {format_size(block_size)}: read {bytes_read} bytes in {duration:.2f} seconds")

            bandwidths[(threads, block_size)] = bytes_read / duration / (1024**2)  # MiB/s

    return bandwidths

def bench_write_frequency(filename: str) -> float:
    offsets = random.sample(range(BIG_FILE_SIZE), SAMPLE_SIZE)

    start = time.time()
    writes = 0
    with open(filename, "wb") as f:
        for offset in offsets:
            f.seek(offset)
            writes += f.write(b'\0')
            duration = time.time() - start
            if duration > TIME_LIMIT:
                break
    duration = time.time() - start
    print(f"Wrote {writes} bytes in {duration:.2f} seconds ({writes/duration:.2f} ops/s)")

    return writes / duration  # operations per second

def bench_read_frequency(filename: str) -> float:
    offsets = random.sample(range(BIG_FILE_SIZE), SAMPLE_SIZE)
    
    start = time.time()
    reads = 0
    with open(filename, "rb") as f:
        for offset in offsets:
            f.seek(offset)
            reads += len(f.read(1))
            duration = time.time() - start
            if duration > TIME_LIMIT:
                break
    duration = time.time() - start
    print(f"Read {reads} bytes in {duration:.2f} seconds ({reads/duration:.2f} ops/s)")

    return reads / duration  # operations per second

def bench_small_files(path: str) -> tuple[float, float]:
    test_dir = os.path.join(path, "small_files_test")
    os.makedirs(test_dir, exist_ok=True)  # Create directory

    start = time.time()
    bytes_written = 0
    for i in range(SAMPLE_SIZE):
        filename = os.path.join(test_dir, f"file_{i}.tmp")
        with open(filename, "wb") as f:
            bytes_written += f.write(RND_DATA[i * SMALL_FILE_SIZE:(i + 1) * SMALL_FILE_SIZE])
        duration = time.time() - start
        if duration > TIME_LIMIT:
            break
    duration = time.time() - start
    write_bandwidth = bytes_written / duration / (1024**2)  # MiB/s
    print(f"Wrote small files with total {bytes_written} bytes in {duration:.2f} seconds ({write_bandwidth:.2f} MiB/s)")

    start = time.time()
    bytes_read = 0
    for i in range(SAMPLE_SIZE):
        file = os.path.join(test_dir, f"file_{i}.tmp")
        try:
            bytes_read += read_chunk(file, 0, SMALL_FILE_SIZE, SMALL_FILE_SIZE)
        except Exception as e:
            pass
        duration = time.time() - start
        if duration > TIME_LIMIT:
            break
    duration = time.time() - start
    read_bandwidth = bytes_read / duration / (1024**2)  # MiB/s
    print(f"Read small files with total {bytes_read} bytes in {duration:.2f} seconds ({read_bandwidth:.2f} MiB/s)")

    shutil.rmtree(test_dir, ignore_errors=True)  # Clean up
    return write_bandwidth, read_bandwidth

def bench_multithreaded_small_files(path: str) -> tuple[dict[int, float], dict[float]]:
    test_dir = os.path.join(path, "small_files_test")

    write_bandwidths = {}
    read_bandwidths = {}
    for threads in THREAD_COUNTS:
        os.makedirs(test_dir, exist_ok=True)  # Create directory
        start = time.time()
        processes = []
        with ThreadPoolExecutor(max_workers=threads) as executor:
            for i in range(SAMPLE_SIZE):
                file = os.path.join(test_dir, f"file_{i}.tmp")
                processes.append(executor.submit(write_chunk, file, 0, SMALL_FILE_SIZE, SMALL_FILE_SIZE))
            for p in processes:
                p.result()
        duration = time.time() - start
        print(f"{threads} threads: wrote {SAMPLE_SIZE * SMALL_FILE_SIZE} bytes in {duration:.2f} seconds")
        write_bandwidths[threads] = SAMPLE_SIZE * SMALL_FILE_SIZE / duration / (1024**2)  # MiB/s

        start = time.time()
        processes = []
        with ThreadPoolExecutor(max_workers=threads) as executor:
            for i in range(SAMPLE_SIZE):
                file = os.path.join(test_dir, f"file_{i}.tmp")
                processes.append(executor.submit(read_chunk, file, 0, SMALL_FILE_SIZE, SMALL_FILE_SIZE))
            for p in processes:
                p.result()
        duration = time.time() - start
        print(f"{threads} threads: read {SAMPLE_SIZE * SMALL_FILE_SIZE} bytes in {duration:.2f} seconds")
        read_bandwidths[threads] = SAMPLE_SIZE * SMALL_FILE_SIZE / duration / (1024**2)  # MiB/s

        shutil.rmtree(test_dir, ignore_errors=True)  # Clean up

    return write_bandwidths, read_bandwidths


@dataclass
class SingleThreadedMeasurement:
    location: str
    write: dict[int, float] # block_size -> bandwidth
    read: dict[int, float]  # block_size -> bandwidth
    write_frequency: float # ops/s
    read_frequency: float # ops/s
    write_small_files: float # MiB/s
    read_small_files: float # MiB/s

    def to_dict(self):
        """Convert Measurement to JSON-serializable dict"""
        return {
            'location': self.location,
            'write': {str(k): v for k, v in self.write.items()},
            'read': {str(k): v for k, v in self.read.items()},
            'write_frequency': self.write_frequency,
            'read_frequency': self.read_frequency,
            'write_small_files': self.write_small_files,
            'read_small_files': self.read_small_files,
        }

    @staticmethod
    def from_dict(d):
        """Create Measurement from dict"""
        return SingleThreadedMeasurement(
            location=d['location'],
            write={int(k): v for k, v in d['write'].items()},
            read={int(k): v for k, v in d['read'].items()},
            write_frequency=d['write_frequency'],
            read_frequency=d['read_frequency'],
            write_small_files=d['write_small_files'],
            read_small_files=d['read_small_files'],
        )


def save_results_to_json(data: list, filename: str):
    """Save measurement results to a JSON file"""
    json_data = [m.to_dict() for m in data]
    with open(filename, 'w') as f:
        json.dump(json_data, f, indent=2)
    print(f"Results saved to {filename}")


def load_results_from_json(filename: str) -> list:
    """Load measurement results from a JSON file"""
    with open(filename, 'r') as f:
        json_data = json.load(f)
    data = [SingleThreadedMeasurement.from_dict(d) for d in json_data]
    print(f"Results loaded from {filename}")
    return data

def short_loc(loc: str) -> str:
    return loc.split('/')[:3][-1].capitalize()

# Create a box plot showing the distribution of read frequencies for all locations.
# Store the plot as PNG file.
def plot_read_frequency(data: list):
    locations = sorted(set(m.location for m in data))
    
    for i, loc in enumerate(locations):
        frequencies = [m.read_frequency for m in data if m.location == loc]
        x_positions = [i] * len(frequencies)
        plt.scatter(x_positions, frequencies, alpha=0.1, color='blue')
    
    plt.xticks(range(len(locations)), [short_loc(loc) for loc in locations])
    plt.ylabel('Frequency (ops/s)')
    plt.ylim(bottom=0)
    
    # Add explicit labels on y-axis with thousand separators
    ax = plt.gca()
    yticks = ax.get_yticks()
    ax.set_yticks(yticks)
    ax.set_yticklabels([f'{int(y):_} ops/s'.replace('_', "'") for y in yticks])

    plt.title('Read Frequency')
    plt.grid(True, which="both", ls="--")
    plt.tight_layout()
    plt.savefig('read_frequency.png')
    plt.close()

# Create a box plot showing the distribution of write frequencies for all locations.
# Store the plot as PNG file.
def plot_write_frequency(data: list):
    locations = sorted(set(m.location for m in data))
    frequencies = [[m.write_frequency for m in data if m.location == loc] for loc in locations]

    plt.boxplot(frequencies, positions=range(len(locations)), showfliers=False)
    plt.xticks(range(len(locations)), [short_loc(loc) for loc in locations])
    plt.ylabel('Frequency (ops/s)')
    plt.ylim(bottom=0)
    
    # Add explicit labels on y-axis
    ax = plt.gca()
    yticks = ax.get_yticks()
    ax.set_yticks(yticks)
    ax.set_yticklabels([f'{int(y):_} ops/s'.replace('_', "'") for y in yticks])

    plt.title('Write Frequency')
    plt.grid(True, which="both", ls="--")
    plt.tight_layout()
    plt.savefig('write_frequency.png')
    plt.close()

# Create a scatter plot showing the distribution of simple read bandwidths for each location.
# Store the plots as PNG files.
def plot_read(data: list):
    locations = sorted(set(m.location for m in data))
    
    for loc in locations:
        loc_data = [m for m in data if m.location == loc]
        block_sizes = sorted(set(bs for m in loc_data for bs in m.read.keys()))
        
        labels = []
        for i, bs in enumerate(block_sizes):
            bs_data = [m.read[bs] for m in loc_data if bs in m.read]
            if bs_data:
                x_positions = [i] * len(bs_data)
                plt.scatter(x_positions, bs_data, alpha=0.02, color='blue')
                labels.append(format_size(bs))
        
        plt.xticks(range(len(labels)), labels, rotation=90)
        plt.xlabel('Block Size')
        plt.ylabel('Bandwidth')
        plt.ylim(bottom=0)
        
        # Add explicit MiB/s labels on y-axis
        ax = plt.gca()
        yticks = ax.get_yticks()
        ax.set_yticks(yticks)
        ax.set_yticklabels([f'{int(y)} MiB/s' if y >= 1 else f'{int(y*1024)} KiB/s' for y in yticks])
        
        plt.title(f'Read Bandwidth on {short_loc(loc)}')
        plt.grid(True, which="both", ls="--")
        plt.tight_layout()
        safe_loc = short_loc(loc).replace("/", "_").replace(" ", "_")
        plt.savefig(f'read_bandwidth_{safe_loc}.png')
        plt.close()

# Create a box plot showing the distribution of simple write bandwidths for each location.
# Store the plots as PNG files.
def plot_write(data: list):
    locations = sorted(set(m.location for m in data))
    
    for loc in locations:
        loc_data = [m for m in data if m.location == loc]
        block_sizes = sorted(set(bs for m in loc_data for bs in m.write.keys()))
        
        labels = []
        for i, bs in enumerate(block_sizes):
            bs_data = [m.write[bs] for m in loc_data if bs in m.write]
            if bs_data:
                x_positions = [i] * len(bs_data)
                plt.scatter(x_positions, bs_data, alpha=0.02, color='blue')
                labels.append(format_size(bs))
        
        plt.xticks(range(len(labels)), labels, rotation=90)
        plt.xlabel('Block Size')
        plt.ylabel('Bandwidth')
        plt.ylim(bottom=0)
        
        # Add explicit MiB/s labels on y-axis
        ax = plt.gca()
        yticks = ax.get_yticks()
        ax.set_yticks(yticks)
        ax.set_yticklabels([f'{int(y)} MiB/s' if y >= 1 else f'{int(y*1024)} KiB/s' for y in yticks])
        
        plt.title(f'Write Bandwidth on {short_loc(loc)}')
        plt.grid(True, which="both", ls="--")
        plt.tight_layout()
        safe_loc = short_loc(loc).replace("/", "_").replace(" ", "_")
        plt.savefig(f'write_bandwidth_{safe_loc}.png')
        plt.close()

# Create a box plot showing the distribution of multithreaded read bandwidths for each location.
# Split by thread count but use same scale across ALL plots.
# Store the plots as PNG files.
def plot_multithreaded_read(data: list):
    locations = sorted(set(m.location for m in data))
    
    # First, collect ALL data across all locations to determine global y-axis range
    all_values = []
    for m in data:
        all_values.extend(m.multithreaded_read.values())
    
    # Determine global y-axis limits for all plots
    if all_values:
        y_min = 0
        y_max = max(all_values) * 1.1  # Add 10% padding
    else:
        y_min, y_max = 0, 100
    
    for loc in locations:
        loc_data = [m for m in data if m.location == loc]
        block_sizes = sorted(set(tb.block_size for m in loc_data for tb in m.multithreaded_read.keys()))
        thread_counts = sorted(set(tb.threads for m in loc_data for tb in m.multithreaded_read.keys()))
        
        # Create separate plot for each thread count
        for tc in thread_counts:
            labels = []
            bandwidths_list = []
            
            for bs in block_sizes:
                tc_data = [m.multithreaded_read.get(TnB(tc, bs), 0) for m in loc_data if TnB(tc, bs) in m.multithreaded_read]
                if tc_data:
                    bandwidths_list.append(tc_data)
                    labels.append(format_size(bs))
            
            if not bandwidths_list:
                continue
            
            plt.boxplot(bandwidths_list, positions=range(len(labels)), showfliers=False)
            plt.xticks(range(len(labels)), labels)
            plt.xlabel('Block Size')
            plt.ylabel('Bandwidth')
            plt.ylim(y_min, y_max)
            
            # Add explicit MiB/s labels on y-axis
            ax = plt.gca()
            yticks = ax.get_yticks()
            ax.set_yticks(yticks)
            ax.set_yticklabels([f'{int(y)} MiB/s' if y >= 1 else f'{int(y*1024)} KiB/s' for y in yticks])
            
            plt.title(f'Read with {tc} threads on {short_loc(loc)}')
            plt.grid(True, which="both", ls="--")
            plt.tight_layout()
            safe_loc = short_loc(loc).replace("/", "_").replace(" ", "_")
            plt.savefig(f'read_bandwidth_{safe_loc}_{tc}T.png')
            plt.close()

# Create a box plot showing the distribution of multithreaded write bandwidths for each location.
# Split by thread count but use same scale across ALL plots.
# Store the plots as PNG files.
def plot_multithreaded_write(data: list):
    locations = sorted(set(m.location for m in data))
    
    # First, collect ALL data across all locations to determine global y-axis range
    all_values = []
    for m in data:
        all_values.extend(m.multithreaded_write.values())
    
    # Determine global y-axis limits for all plots
    if all_values:
        y_min = 0
        y_max = max(all_values) * 1.1  # Add 10% padding
    else:
        y_min, y_max = 0, 100
    
    for loc in locations:
        loc_data = [m for m in data if m.location == loc]
        block_sizes = sorted(set(tb.block_size for m in loc_data for tb in m.multithreaded_write.keys()))
        thread_counts = sorted(set(tb.threads for m in loc_data for tb in m.multithreaded_write.keys()))
        
        # Create separate plot for each thread count
        for tc in thread_counts:
            labels = []
            bandwidths_list = []
            
            for bs in block_sizes:
                tc_data = [m.multithreaded_write.get(TnB(tc, bs), 0) for m in loc_data if TnB(tc, bs) in m.multithreaded_write]
                if tc_data:
                    bandwidths_list.append(tc_data)
                    labels.append(format_size(bs))
            
            if not bandwidths_list:
                continue

            plt.boxplot(bandwidths_list, positions=range(len(labels)), showfliers=False)
            plt.xticks(range(len(labels)), labels)
            plt.xlabel('Block Size')
            plt.ylabel('Bandwidth')
            plt.ylim(y_min, y_max)
            
            # Add explicit MiB/s labels on y-axis
            ax = plt.gca()
            yticks = ax.get_yticks()
            ax.set_yticks(yticks)
            ax.set_yticklabels([f'{int(y)} MiB/s' if y >= 1 else f'{int(y*1024)} KiB/s' for y in yticks])
            
            plt.title(f'Write with {tc} threads on {short_loc(loc)}')
            plt.grid(True, which="both", ls="--")
            plt.tight_layout()
            safe_loc = short_loc(loc).replace("/", "_").replace(" ", "_")
            plt.savefig(f'write_bandwidth_{safe_loc}_{tc}T.png')
            plt.close()

# Create a scatter plot showing the distribution of small files read bandwidths for all locations.
# Store the plot as PNG file.
def plot_read_small_files(data: list):
    locations = sorted(set(m.location for m in data))
    
    for i, loc in enumerate(locations):
        loc_data = [m.read_small_files for m in data if m.location == loc]
        x_positions = [i] * len(loc_data)
        plt.scatter(x_positions, loc_data, alpha=0.02, color='blue')
    
    plt.xticks(range(len(locations)), [short_loc(loc) for loc in locations])
    plt.ylabel('Bandwidth')
    plt.ylim(bottom=0)
    
    # Add explicit MiB/s labels on y-axis
    ax = plt.gca()
    yticks = ax.get_yticks()
    ax.set_yticks(yticks)
    ax.set_yticklabels([f'{int(y)} MiB/s' if y >= 1 else f'{int(y*1024)} KiB/s' for y in yticks])
    
    plt.title('Small Files Read Bandwidth')
    plt.grid(True, which="both", ls="--")
    plt.tight_layout()
    plt.savefig('read_small_files.png')
    plt.close()

# Create a scatter plot showing the distribution of small files write bandwidths for all locations.
# Store the plot as PNG file.
def plot_write_small_files(data: list):
    locations = sorted(set(m.location for m in data))
    
    for i, loc in enumerate(locations):
        loc_data = [m.write_small_files for m in data if m.location == loc]
        x_positions = [i] * len(loc_data)
        plt.scatter(x_positions, loc_data, alpha=0.02, color='blue')
    
    plt.xticks(range(len(locations)), [short_loc(loc) for loc in locations])
    plt.ylabel('Bandwidth')
    plt.ylim(bottom=0)
    
    # Add explicit MiB/s labels on y-axis
    ax = plt.gca()
    yticks = ax.get_yticks()
    ax.set_yticks(yticks)
    ax.set_yticklabels([f'{int(y)} MiB/s' if y >= 1 else f'{int(y*1024)} KiB/s' for y in yticks])
    
    plt.title('Small Files Write Bandwidth')
    plt.grid(True, which="both", ls="--")
    plt.tight_layout()
    plt.savefig('write_small_files.png')
    plt.close()

# Create a box plot showing the distribution of multithreaded small files read bandwidths for all locations and thread counts.
# Split by thread count but use same scale across ALL plots.
# Store the plots as PNG files.
def plot_multithreaded_read_small_files(data: list):
    locations = sorted(set(m.location for m in data))
    thread_counts = sorted(set(tc for m in data for tc in m.multithreaded_read_small_files.keys()))
    
    # First, collect ALL data across all locations to determine global y-axis range
    all_values = []
    for m in data:
        all_values.extend(m.multithreaded_read_small_files.values())
    
    # Determine global y-axis limits for all plots
    if all_values:
        y_min = 0
        y_max = max(all_values) * 1.1  # Add 10% padding
    else:
        y_min, y_max = 0, 100
    
    # Create separate plot for each thread count
    for tc in thread_counts:
        labels = []
        bandwidths_list = []
        
        for loc in locations:
            loc_data = [m.multithreaded_read_small_files.get(tc, 0) for m in data if m.location == loc and tc in m.multithreaded_read_small_files]
            if loc_data:
                bandwidths_list.append(loc_data)
                labels.append(short_loc(loc))
        
        if not bandwidths_list:
            continue

        plt.boxplot(bandwidths_list, positions=range(len(labels)), showfliers=False)
        plt.xticks(range(len(labels)), labels)
        plt.xlabel('Location')
        plt.ylabel('Bandwidth')
        plt.ylim(y_min, y_max)
        
        # Add explicit MiB/s labels on y-axis
        ax = plt.gca()
        yticks = ax.get_yticks()
        ax.set_yticks(yticks)
        ax.set_yticklabels([f'{int(y)} MiB/s' if y >= 1 else f'{int(y*1024)} KiB/s' for y in yticks])
        
        plt.title(f'Small Files Read ({tc} threads)')
        plt.grid(True, which="both", ls="--")
        plt.tight_layout()
        plt.savefig(f'read_small_files_{tc}T.png')
        plt.close()

# Create a box plot showing the distribution of multithreaded small files write bandwidths for all locations and thread counts.
# Split by thread count but use same scale across ALL plots.
# Store the plots as PNG files.
def plot_multithreaded_write_small_files(data: list):
    locations = sorted(set(m.location for m in data))
    thread_counts = sorted(set(tc for m in data for tc in m.multithreaded_write_small_files.keys()))
    
    # First, collect ALL data across all locations to determine global y-axis range
    all_values = []
    for m in data:
        all_values.extend(m.multithreaded_write_small_files.values())
    
    # Determine global y-axis limits for all plots
    if all_values:
        y_min = 0
        y_max = max(all_values) * 1.1  # Add 10% padding
    else:
        y_min, y_max = 0, 100
    
    # Create separate plot for each thread count
    for tc in thread_counts:
        labels = []
        bandwidths_list = []
        
        for loc in locations:
            loc_data = [m.multithreaded_write_small_files.get(tc, 0) for m in data if m.location == loc and tc in m.multithreaded_write_small_files]
            if loc_data:
                bandwidths_list.append(loc_data)
                labels.append(short_loc(loc))
        
        if not bandwidths_list:
            continue

        plt.boxplot(bandwidths_list, positions=range(len(labels)), showfliers=False)
        plt.xticks(range(len(labels)), labels)
        plt.xlabel('Location')
        plt.ylabel('Bandwidth')
        plt.ylim(y_min, y_max)
        
        # Add explicit MiB/s labels on y-axis
        ax = plt.gca()
        yticks = ax.get_yticks()
        ax.set_yticks(yticks)
        ax.set_yticklabels([f'{int(y)} MiB/s' if y >= 1 else f'{int(y*1024)} KiB/s' for y in yticks])
        
        plt.title(f'Small Files Write ({tc} threads)')
        plt.grid(True, which="both", ls="--")
        plt.tight_layout()
        plt.savefig(f'write_small_files_{tc}T.png')
        plt.close()


if __name__ == "__main__":
    # First CLI argument is the path to benchmark
    if len(sys.argv) < 2:
        print(sys.argv)
        raise ValueError("Please provide a path to benchmark as argument.")
    location = sys.argv[1]
    json_filename = f"{short_loc(location)}_results.json"
    data : list = []
    try:
        data = load_results_from_json(json_filename)
    except FileNotFoundError:
        pass

    # for _ in range(REPETITIONS):
    #     if not os.path.exists(location):
    #         continue

    #     write_filename = os.path.join(location, "write_file.tmp")
    #     # Create static read file
    #     read_filename = os.path.join(location, "read_file.tmp")
    #     with open(read_filename, 'wb') as f:
    #         f.write(RND_DATA)

    #     small_files = bench_small_files(location)
    #     m = SingleThreadedMeasurement(
    #         location=location,
    #         write=bench_write(write_filename),
    #         read=bench_read(read_filename),
    #         write_frequency=bench_write_frequency(write_filename),
    #         read_frequency=bench_read_frequency(read_filename),
    #         write_small_files=small_files[0],
    #         read_small_files=small_files[1],
    #     )
    #     os.remove(read_filename)  # Clean up

    #     data.append(m)
        
    #     save_results_to_json(data, json_filename)
    #     plot_read_frequency(data)
    #     plot_write_frequency(data)
    #     plot_read(data)
    #     plot_write(data)
    #     plot_read_small_files(data)
    #     plot_write_small_files(data)

    plot_read_frequency(data)
    plot_write_frequency(data)
    plot_read(data)
    plot_write(data)
    plot_read_small_files(data)
    plot_write_small_files(data)
