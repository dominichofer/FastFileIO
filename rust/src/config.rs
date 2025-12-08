use std::fs::File;
use std::io::{BufRead, BufReader};
use std::path::Path;

#[derive(Debug, Clone)]
pub struct Config {
    pub time_limit: u64,
    pub random_accesses: usize,
    pub small_files_count: usize,
    pub small_file_size: u64,
    pub big_file_size: u64,
    pub block_sizes: Vec<u64>,
}

impl Default for Config {
    fn default() -> Self {
        Self {
            time_limit: 5,
            random_accesses: 100_000,
            small_files_count: 10_000,
            small_file_size: 1024,  // 1 KiB
            big_file_size: 10 * 1024 * 1024 * 1024,  // 10 GiB
            block_sizes: (3..31).map(|i| 2u64.pow(i)).collect(),  // 8 bytes to 1 GiB
        }
    }
}

impl Config {
    pub fn load(filepath: &str) -> Self {
        let mut config = Config::default();
        
        if let Ok(file) = File::open(Path::new(filepath)) {
            let reader = BufReader::new(file);
            
            for line in reader.lines() {
                if let Ok(line) = line {
                    // Remove comments
                    let line = if let Some(pos) = line.find('#') {
                        &line[..pos]
                    } else {
                        &line
                    };
                    
                    let line = line.trim();
                    if line.is_empty() {
                        continue;
                    }
                    
                    if let Some(pos) = line.find('=') {
                        let key = line[..pos].trim();
                        let value = line[pos + 1..].trim();
                        
                        match key {
                            "time_limit" => {
                                if let Ok(val) = value.parse() {
                                    config.time_limit = val;
                                }
                            }
                            "random_accesses" => {
                                if let Ok(val) = value.parse() {
                                    config.random_accesses = val;
                                }
                            }
                            "small_files_count" => {
                                if let Ok(val) = value.parse() {
                                    config.small_files_count = val;
                                }
                            }
                            "small_file_size" => {
                                if let Ok(val) = value.parse() {
                                    config.small_file_size = val;
                                }
                            }
                            "big_file_size" => {
                                if let Ok(val) = value.parse() {
                                    config.big_file_size = val;
                                }
                            }
                            "block_sizes" => {
                                config.block_sizes = value
                                    .split(',')
                                    .filter_map(|s| s.trim().parse().ok())
                                    .collect();
                            }
                            _ => {}
                        }
                    }
                }
            }
        }
        
        println!("Config:");
        println!("  time_limit: {}", config.time_limit);
        println!("  random_accesses: {}", config.random_accesses);
        println!("  small_files_count: {}", config.small_files_count);
        println!("  small_file_size: {}", config.small_file_size);
        println!("  big_file_size: {}", config.big_file_size);
        println!("  block_sizes: {:?}", config.block_sizes);
        
        config
    }
}
