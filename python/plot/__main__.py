import argparse
import matplotlib.pyplot as plt
from dataclasses import dataclass


def clamp(value: float, min_value: float, max_value: float) -> float:
    return max(min_value, min(value, max_value))

    
@dataclass
class DataPoint:
    mode: str
    direction: str
    name: str
    path: str
    value: float

    def from_string(line: str) -> 'DataPoint':
        parts = [item.strip() for item in line.strip().split(',')]
        mode, direction, name, path, value = parts
        mode = mode.split()[0]  # first word
        return DataPoint(mode, direction, name, path, float(value))
    

def plot_data(data: list[DataPoint], names: set[str], kind: str, ylabel: str, color: str, filename_prefix: str, title_template: str, use_log_scale: bool = False) -> None:
    """Plot data for each direction."""
    for direction in ['read', 'write']:
        plt.figure()
        filtered_data = [m for m in data if m.mode == kind]
        for name in names:
            values = [m.value for m in filtered_data if m.name == name and m.direction == direction]
            if not values:
                continue
            x = [name] * len(values)
            plt.scatter(x, values, alpha=clamp(2.0/len(values), 0, 1), color=color)

        plt.ylabel(ylabel)
        if use_log_scale:
            plt.yscale('log')
        else:
            plt.ylim(bottom=0)
        ax = plt.gca()
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'{int(x):_}'.replace("_", "'")))

        plt.xticks(rotation=45, ha='right')
        plt.title(title_template.format(direction=direction.capitalize()))
        plt.grid(True, which="both", ls="--")
        plt.tight_layout()
        plt.savefig(f"{filename_prefix}_{direction}.png")
        plt.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Plot file I/O benchmarks')
    parser.add_argument('results_file', help='Path to results file')
    args = parser.parse_args()

    with open(args.results_file, 'r') as f:
        data = [DataPoint.from_string(line) for line in f if line.strip()]

    names = set(m.name for m in data)

    ylabel = {
        'large': 'Large files bandwidth (MiB/s)',
        'small': 'Small files bandwidth (MiB/s)',
        'random': 'Transfers per second (IOPS)',
    }
    title = {
        'large': '{direction} bandwidth of large files',
        'small': '{direction} bandwidth of small files',
        'random': 'Random {direction} operations per second',
    }
    filename = {
        'large': 'large_files_bandwidth',
        'small': 'small_files_bandwidth',
        'random': 'random',
    }

    for mode in ['large', 'small', 'random']:
        for direction in ['read', 'write']:
            plt.figure()
            filtered_data = [m for m in data if m.mode == mode]
            for name in names:
                values = [m.value for m in filtered_data if m.name == name and m.direction == direction]
                if not values:
                    continue
                x = [name] * len(values)
                plt.scatter(x, values, alpha=clamp(2.0/len(values), 0, 1), color='indigo')

            plt.ylabel(ylabel[mode])
            if mode == 'random access IOPS':
                plt.yscale('log')
            else:
                plt.ylim(bottom=0)
            ax = plt.gca()
            ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'{int(x):_}'.replace("_", "'")))

            plt.xticks(rotation=45, ha='right')
            plt.title(title[mode].format(direction=direction.capitalize()))
            plt.grid(True, which="both", ls="--")
            plt.tight_layout()
            plt.savefig(f"{filename[mode]}_{direction}.png")
            plt.close()
