use std::io;
use crate::config::Config;
use crate::large_files::LargeFileBenchmarker;
use crate::small_files::SmallFilesBenchmarker;
use crate::random_access::RandomAccessBenchmarker;

fn setup_paths(location: &str, output_file: &str) -> io::Result<(String, String)> {
    // Expand environment variables and user home directory
    let location = shellexpand::full(location)
        .map_err(|e| io::Error::new(io::ErrorKind::InvalidInput, e.to_string()))?
        .to_string();
    let output_file = shellexpand::full(output_file)
        .map_err(|e| io::Error::new(io::ErrorKind::InvalidInput, e.to_string()))?
        .to_string();
    
    // Create directory if it doesn't exist
    std::fs::create_dir_all(&location)?;
    
    Ok((location, output_file))
}

pub fn run_large_files(
    location: &str,
    name: &str,
    output_file: &str,
    repetitions: usize,
    config_file: &str,
) -> io::Result<()> {
    let (location, output_file) = setup_paths(location, output_file)?;
    let config = Config::load(config_file);
    
    let bm = LargeFileBenchmarker::new(&location, name, config.big_file_size, config.time_limit);
    for _ in 0..repetitions {
        for &block_size in &config.block_sizes {
            bm.run(block_size, &output_file)?;
        }
    }
    bm.cleanup()?;
    Ok(())
}

pub fn run_small_files(
    location: &str,
    name: &str,
    output_file: &str,
    repetitions: usize,
    config_file: &str,
) -> io::Result<()> {
    let (location, output_file) = setup_paths(location, output_file)?;
    let config = Config::load(config_file);
    
    let bm = SmallFilesBenchmarker::new(
        &location,
        name,
        config.small_file_size,
        config.small_files_count,
        config.time_limit,
    );
    for _ in 0..repetitions {
        bm.run(&output_file)?;
    }
    bm.cleanup()?;
    Ok(())
}

pub fn run_random_access(
    location: &str,
    name: &str,
    output_file: &str,
    repetitions: usize,
    config_file: &str,
) -> io::Result<()> {
    let (location, output_file) = setup_paths(location, output_file)?;
    let config = Config::load(config_file);
    
    let bm = RandomAccessBenchmarker::new(
        &location,
        name,
        config.big_file_size,
        config.random_accesses,
        config.time_limit,
    )?;
    for _ in 0..repetitions {
        bm.run(&output_file)?;
    }
    bm.cleanup()?;
    Ok(())
}

pub fn run_all(
    location: &str,
    name: &str,
    output_file: &str,
    repetitions: usize,
    config_file: &str,
) -> io::Result<()> {
    let (location, output_file) = setup_paths(location, output_file)?;
    let config = Config::load(config_file);
    
    let bm_large = LargeFileBenchmarker::new(&location, name, config.big_file_size, config.time_limit);
    let bm_small = SmallFilesBenchmarker::new(
        &location,
        name,
        config.small_file_size,
        config.small_files_count,
        config.time_limit,
    );
    let bm_random = RandomAccessBenchmarker::new(
        &location,
        name,
        config.big_file_size,
        config.random_accesses,
        config.time_limit,
    )?;
    
    for _ in 0..repetitions {
        for &block_size in &config.block_sizes {
            bm_large.run(block_size, &output_file)?;
        }
        bm_small.run(&output_file)?;
        bm_random.run(&output_file)?;
    }
    
    bm_large.cleanup()?;
    bm_small.cleanup()?;
    bm_random.cleanup()?;
    
    Ok(())
}
