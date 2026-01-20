use rand::Rng;
use std::env;
use std::fs::{self, File, OpenOptions};
use std::io::{Read, Seek, SeekFrom, Write};
use std::path::PathBuf;
use std::time::{Duration, Instant};

/// Writes data to a file and returns the bandwidth in MiB/s.
fn write_file(file_path: &PathBuf, data: &[u8]) -> f64 {
    let start = Instant::now();
    let mut f = File::create(file_path).expect("Failed to create file");
    f.write_all(data).expect("Failed to write data");
    let duration = start.elapsed().as_secs_f64();
    data.len() as f64 / duration / (1024.0 * 1024.0)
}

/// Reads data from a file and returns the bandwidth in MiB/s.
fn read_file(file_path: &PathBuf) -> f64 {
    let start = Instant::now();
    let mut f = File::open(file_path).expect("Failed to open file");
    let mut data = Vec::new();
    f.read_to_end(&mut data).expect("Failed to read data");
    let duration = start.elapsed().as_secs_f64();
    data.len() as f64 / duration / (1024.0 * 1024.0)
}

/// Writes random bytes to a file and returns the IOPS.
fn write_random_bytes(file_path: &PathBuf, file_size: usize, operations: usize, time_limit: Duration) -> f64 {
    let mut rng = rand::rng();
    let rnd_pos: Vec<u64> = (0..operations)
        .map(|_| rng.random_range(0..file_size as u64))
        .collect();
    let mut bytes_written = 0usize;
    let start = Instant::now();
    let mut f = OpenOptions::new()
        .read(true)
        .write(true)
        .open(file_path)
        .expect("Failed to open file");
    for pos in rnd_pos {
        f.seek(SeekFrom::Start(pos)).expect("Failed to seek");
        bytes_written += f.write(&[0u8]).expect("Failed to write");
        if start.elapsed() > time_limit {
            break;
        }
    }
    let duration = start.elapsed().as_secs_f64();
    bytes_written as f64 / duration
}

/// Reads random bytes from a file and returns the IOPS.
fn read_random_bytes(file_path: &PathBuf, file_size: usize, operations: usize, time_limit: Duration) -> f64 {
    let mut rng = rand::rng();
    let rnd_pos: Vec<u64> = (0..operations)
        .map(|_| rng.random_range(0..file_size as u64))
        .collect();
    let mut bytes_read = 0usize;
    let start = Instant::now();
    let mut f = File::open(file_path).expect("Failed to open file");
    let mut buf = [0u8; 1];
    for pos in rnd_pos {
        f.seek(SeekFrom::Start(pos)).expect("Failed to seek");
        let n = f.read(&mut buf).expect("Failed to read");
        if n == 0 {
            break;
        }
        bytes_read += n;
        if start.elapsed() > time_limit {
            break;
        }
    }
    let duration = start.elapsed().as_secs_f64();
    bytes_read as f64 / duration
}

fn main() {
    let args: Vec<String> = env::args().collect();
    if args.len() < 2 {
        eprintln!("Usage: {} <path> <name> [repetitions]", args[0]);
        std::process::exit(1);
    }

    let path = PathBuf::from(shellexpand::full(&args[1]).unwrap().to_string());
    let name = args[2].clone();
    let repetitions: usize = args.get(3).and_then(|s| s.parse().ok()).unwrap_or(1);

    let time_limit = Duration::from_secs(10);
    let large_file_path = path.join("large_file.dat");
    let large_file_size: usize = 10 * (1 << 30); // 10 GiB
    let small_file_paths: Vec<PathBuf> = (0..10_000)
        .map(|i| path.join(format!("small_file_{}.dat", i)))
        .collect();
    let small_file_size: usize = 1 << 10; // 1 kiB

    let mut rng = rand::rng();
    let rnd_data: Vec<u8> = (0..large_file_size).map(|_| rng.random()).collect();
    let small_file_data: Vec<Vec<u8>> = (0..small_file_paths.len())
        .map(|_| (0..small_file_size).map(|_| rng.random()).collect())
        .collect();

    for _ in 0..repetitions {
        let bandwidth = write_file(&large_file_path, &rnd_data);
        println!("large file bandwidth, write, {}, {}, {}", name, path.display(), bandwidth);
        let bandwidth = read_file(&large_file_path);
        println!("large file bandwidth, read, {}, {}, {}", name, path.display(), bandwidth);

        let operations = 100_000;
        let iops = write_random_bytes(&large_file_path, large_file_size, operations, time_limit);
        println!("random access IOPS, write, {}, {}, {}", name, path.display(), iops);
        let iops = read_random_bytes(&large_file_path, large_file_size, operations, time_limit);
        println!("random access IOPS, read, {}, {}, {}", name, path.display(), iops);

        let mut bytes_written = 0usize;
        let start = Instant::now();
        for (file_path, small_data) in small_file_paths.iter().zip(small_file_data.iter()) {
            let mut f = File::create(file_path).expect("Failed to create file");
            bytes_written += f.write(small_data).expect("Failed to write");
            if start.elapsed() > time_limit {
                break;
            }
        }
        let duration = start.elapsed().as_secs_f64();
        let bandwidth = bytes_written as f64 / duration / (1024.0 * 1024.0);
        println!("small file bandwidth, write, {}, {}, {}", name, path.display(), bandwidth);

        let mut bytes_read = 0usize;
        let start = Instant::now();
        let mut data: Vec<Vec<u8>> = small_file_data.iter().map(|d| vec![0u8; d.len()]).collect();
        for (file_path, d) in small_file_paths.iter().zip(data.iter_mut()) {
            match File::open(file_path) {
                Ok(mut f) => {
                    f.read_to_end(d).expect("Failed to read");
                    bytes_read += d.len();
                }
                Err(_) => break,
            }
            if start.elapsed() > time_limit {
                break;
            }
        }
        let duration = start.elapsed().as_secs_f64();
        let bandwidth = bytes_read as f64 / duration / (1024.0 * 1024.0);
        println!("small file bandwidth, read, {}, {}, {}", name, path.display(), bandwidth);
    }

    // Cleanup
    let _ = fs::remove_file(&large_file_path);
    for file_path in &small_file_paths {
        let _ = fs::remove_file(file_path);
    }
}
