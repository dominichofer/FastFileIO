mod config;
mod large_files;
mod small_files;
mod random_access;
use config::Config;
use large_files::LargeFileBenchmarker;
use small_files::SmallFilesBenchmarker;
use random_access::RandomAccessBenchmarker;
use std::env;

fn main() {
    let args: Vec<String> = env::args().collect();
    
    if args.len() < 2 {
        println!("Usage: <path> <name> <config_file> <output_file> [repetitions]");
        return;
    }

    let path = &args[1];
    let name = &args[2];
    let config_file = &args[3];
    let output_file = &args[4];
    let repetitions = args.get(5).and_then(|s| s.parse().ok()).unwrap_or(1);

    // Resolve path to absolute
    let path = std::fs::canonicalize(path).expect("Failed to resolve path").to_str().unwrap().to_string();
    let config_file = std::fs::canonicalize(config_file).expect("Failed to resolve config file path").to_str().unwrap().to_string();
    let output_file = std::fs::canonicalize(output_file).expect("Failed to resolve output file path").to_str().unwrap().to_string();
    
    let config = Config::load(&config_file);
    println!("Running with:");
    println!("  Path: {}", path);
    println!("  Name: {}", name);
    println!("  Config file: {}", config_file);
    println!("  Output file: {}", output_file);
    println!("  Repetitions: {}", repetitions);
    println!("  Time limit: {} seconds", config.time_limit);
    println!("  Random accesses: {}", config.random_accesses);
    println!("  Small file count: {}", config.small_file_count);
    println!("  Small file size: {} bytes", config.small_file_size);
    println!("  Large file size: {} bytes", config.large_file_size);
    print!("  Block sizes: ");
    for bs in &config.block_sizes {
        print!("{} ", bs);
    }
    println!();

    let mut large_bm = LargeFileBenchmarker::new(&path, name, &config);
    let mut small_bm = SmallFilesBenchmarker::new(&path, name, &config);
    let mut random_bm = RandomAccessBenchmarker::new(&path, name, &config);

    let output = &mut std::fs::OpenOptions::new()
        .create(true)
        .append(true)
        .open(output_file)
        .expect("Failed to open output file");

    for _ in 0..repetitions {
        large_bm.run(output).expect("Large file benchmark failed");
        small_bm.run(output).expect("Small files benchmark failed");
        random_bm.run(output).expect("Random access benchmark failed");
    }
}
