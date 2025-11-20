
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

def format_MiB_per_s(value: float) -> str:
    """Format bandwidth in MiB/s with appropriate suffix"""
    return f"{int(value):_} MiB/s".replace("_", "'")
