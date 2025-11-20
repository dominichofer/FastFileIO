import matplotlib.pyplot as plt
from .measurements import *
from .format import *

class Plotter:
    data: list[Measurement]
    location_label: dict[str, str]  # Maps location to label

    def __init__(self, data: list[Measurement], location_label: dict[str, str] = None) -> None:
        self.data = data
        self.location_label = location_label or {}

    def plot_random_access(self) -> None:
        """Plot random access transfers for each location. One plot per direction."""
        locations = set(m.location for m in self.data)
        for direction in [IoDirection.READ, IoDirection.WRITE]:
            plt.figure()
            for location in locations:
                loc = self.location_label.get(location, location)
                data = [m for m in self.data if m.direction == direction and m.location == location and isinstance(m, RandomAccess)]
                iops = [m.iops for m in data]
                x = [loc] * len(iops)
                plt.scatter(x, iops, alpha=0.1, color='red')

            plt.ylabel('Transfers per second (IOPS)')
            plt.ylim(bottom=0)
            ax = plt.gca()
            ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{int(x):_}'.replace("_", "'")))
            
            direction_str = 'writes' if direction == IoDirection.WRITE else 'reads'
            plt.title(f'Random {direction_str} IOPS')
            plt.grid(True, which="both", ls="--")
            plt.tight_layout()
            plt.savefig(f"random_{direction_str}.png")
            plt.close()


    def plot_large_file_bandwidth(self) -> None:
        """Plot large file bandwidth for each block size. One plot per direction and location."""
        locations = set(m.location for m in self.data)
        for location in locations:
            loc = self.location_label.get(location, location)
            for direction in [IoDirection.READ, IoDirection.WRITE]:
                data = [m for m in self.data if m.direction == direction and m.location == location and isinstance(m, LargeFileBandwidth)]
                block_sizes = sorted(set(m.block_size for m in data))
                plt.figure()
                for block_size in block_sizes:
                    bs_data = [m.bandwidth for m in data if m.block_size == block_size]
                    x = [block_size] * len(bs_data)
                    plt.scatter(x, bs_data, alpha=0.1, color='green')
                
                plt.xscale('log', base=2)
                plt.xticks(block_sizes, [format_bytes(bs) for bs in block_sizes], rotation=90)
                plt.xlabel('Block Size')

                plt.ylabel('Bandwidth (MiB/s)')
                plt.ylim(bottom=0)
                ax = plt.gca()
                ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{int(x):_}'.replace("_", "'")))

                direction_str = 'Write' if direction == IoDirection.WRITE else 'Read'
                plt.title(f'{direction_str} bandwidth of large files on {loc}')
                plt.grid(True, which="both", ls="--")
                plt.tight_layout()
                plt.savefig(f"large_files_{direction_str.lower()}_bandwidth_{loc}.png")
                plt.close()

    def plot_small_file_bandwidth(self) -> None:
        """Plot small file bandwidth for each location. One plot per direction."""
        locations = set(m.location for m in self.data)
        for direction in [IoDirection.READ, IoDirection.WRITE]:
            plt.figure()
            for location in locations:
                loc = self.location_label.get(location, location)
                data = [m for m in self.data if m.direction == direction and m.location == location and isinstance(m, SmallFilesBandwidth)]
                bandwidths = [m.bandwidth for m in data]
                x = [loc] * len(bandwidths)
                plt.scatter(x, bandwidths, alpha=0.1, color='blue')
                
            plt.ylabel('Small files bandwidth (MiB/s)')
            plt.ylim(bottom=0)
            ax = plt.gca()
            ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{int(x):_}'.replace("_", "'")))

            direction_str = 'Write' if direction == IoDirection.WRITE else 'Read'
            plt.title(f'{direction_str} bandwidth of small files')
            plt.grid(True, which="both", ls="--")
            plt.tight_layout()
            plt.savefig(f"small_files_{direction_str.lower()}_bandwidth.png") 
            plt.close()

    def plot_all(self) -> None:
        self.plot_random_access()
        self.plot_large_file_bandwidth()
        self.plot_small_file_bandwidth()


    def plot(file: str) -> None:
        """Load measurements from file and generate plots."""
        data = []
        with open(file, 'r') as f:
            for line in f:
                data.append(parse_measurement(line))

        Plotter(data).plot_all()

def plot(file: str) -> None:
    """Load measurements from file and generate plots."""
    data = []
    with open(file, 'r') as f:
        for line in f:
            data.append(parse_measurement(line))

    location_label = {
        '/home/dominic/schnitzengiggel': 'Home',
    }
    Plotter(data, location_label).plot_all()
