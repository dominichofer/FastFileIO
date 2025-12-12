use serde::Deserialize;

#[derive(Debug, Clone, Deserialize)]
pub struct Config {
    pub time_limit: usize,
    pub random_accesses: usize,
    pub small_file_count: usize,
    pub small_file_size: usize,
    pub large_file_size: usize,
    pub block_sizes: Vec<usize>,
}

impl Config {
    pub fn load(path: &str) -> Self {
        let content = std::fs::read_to_string(path).expect("Failed to read config file");
        serde_yaml::from_str(&content).expect("Failed to parse config file")
    }
}
