import matplotlib.pyplot as plt
from .measurements import *
from .format import *

def clamp(value: float, min_value: float, max_value: float) -> float:
    return max(min_value, min(value, max_value))

class Plotter:
    data: list[Measurement]

    def __init__(self, data: list[Measurement], names: list[str]) -> None:
        self.data = data
        self.names = names

    def plot_random_access(self) -> None:
        """Plot random access transfers for each location. One plot per direction."""
        for direction in [IoDirection.READ, IoDirection.WRITE]:
            plt.figure()
            for name in self.names:
                data = [m for m in self.data if m.direction == direction and m.name == name and isinstance(m, RandomAccess)]
                iops = [m.iops for m in data]
                x = [name] * len(iops)
                plt.scatter(x, iops, alpha=clamp(2.0/len(data), 0, 1), color='red')

            plt.ylabel('Transfers per second (IOPS)')
            plt.yscale('log')
            ax = plt.gca()
            ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{int(x):_}'.replace("_", "'")))
            
            plt.xticks(rotation=45, ha='right')
            direction_str = 'write' if direction == IoDirection.WRITE else 'read'
            plt.title(f'Random {direction_str} operations per second')
            plt.grid(True, which="both", ls="--")
            plt.tight_layout()
            plt.savefig(f"random_{direction_str}.png")
            plt.close()


    def plot_large_file_bandwidth(self) -> None:
        """Plot large file bandwidth for each block size. One plot per direction and location."""
        # import matplotlib.cm as cm
        # import matplotlib.colors as mcolors
        
        # for location in self.locations:
        #     for direction in [IoDirection.READ, IoDirection.WRITE]:
        #         data = [m for m in self.data if m.direction == direction and m.location == location and isinstance(m, LargeFileBandwidth)]
        #         block_sizes = sorted(set(m.block_size for m in data))
        #         plt.figure()
                
        #         # Create colormap based on time of day (hour)
        #         hours = [m.timestamp.hour + m.timestamp.minute / 60.0 for m in data]
        #         norm = mcolors.Normalize(vmin=0, vmax=24)
        #         cmap = cm.get_cmap('twilight')
                
        #         for block_size in block_sizes:
        #             bs_data = [(m.bandwidth, m.timestamp.hour + m.timestamp.minute / 60.0) for m in data if m.block_size == block_size]
        #             x = [block_size] * len(bs_data)
        #             y = [bd[0] for bd in bs_data]
        #             colors = [cmap(norm(bd[1])) for bd in bs_data]
        #             plt.scatter(x, y, alpha=5.0/len(bs_data), c=colors)
                
        #         # Add colorbar
        #         sm = cm.ScalarMappable(cmap=cmap, norm=norm)
        #         sm.set_array([])
        #         cbar = plt.colorbar(sm, ax=plt.gca())
        #         cbar.set_label('Hour of Day')

        for name in self.names:
            for direction in [IoDirection.READ, IoDirection.WRITE]:
                data = [m for m in self.data if m.direction == direction and m.name == name and isinstance(m, LargeFileBandwidth)]
                block_sizes = sorted(set(m.block_size for m in data))
                plt.figure()
                for block_size in block_sizes:
                    bs_data = [m.bandwidth for m in data if m.block_size == block_size]
                    x = [block_size] * len(bs_data)
                    plt.scatter(x, bs_data, alpha=clamp(5.0/len(bs_data), 0, 1), color='green')
                
                plt.xscale('log', base=2)
                plt.xticks(block_sizes, [format_bytes(bs) for bs in block_sizes], rotation=90)
                plt.xlabel('Block Size')

                plt.ylabel('Bandwidth (MiB/s)')
                ax = plt.gca()
                ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{int(x):_}'.replace("_", "'")))

                direction_str = 'Write' if direction == IoDirection.WRITE else 'Read'
                plt.title(f'{direction_str} bandwidth of large files on {name}')
                plt.grid(True, which="both", ls="--")
                plt.tight_layout()
                plt.savefig(f"large_files_{direction_str.lower()}_bandwidth_{name}.png")
                plt.close()

    def plot_small_file_bandwidth(self) -> None:
        """Plot small file bandwidth for each location. One plot per direction."""
        for direction in [IoDirection.READ, IoDirection.WRITE]:
            plt.figure()
            for name in self.names:
                data = [m for m in self.data if m.direction == direction and m.name == name and isinstance(m, SmallFilesBandwidth)]
                bandwidths = [m.bandwidth for m in data]
                x = [name] * len(bandwidths)
                plt.scatter(x, bandwidths, alpha=clamp(2.0/len(data), 0, 1), color='blue')
                
            plt.ylabel('Small files bandwidth (MiB/s)')
            ax = plt.gca()
            ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{int(x):_}'.replace("_", "'")))

            plt.xticks(rotation=45, ha='right')
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


def plot(file: str, names: list[str] | None = None) -> None:
    """Load measurements from file and generate plots."""
    data = []
    name_set = set()
    with open(file, 'r') as f:
        for line in f:
            m = parse_measurement(line)
            data.append(m)
            name_set.add(m.name)

    if names is None:
        names = list(name_set)
        print(f"Detected names: {names}")

    Plotter(data, names).plot_all()
