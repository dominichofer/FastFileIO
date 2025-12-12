use std::fs::{File};
use std::io::{self, Write, Read};
use std::path::PathBuf;
use std::time::{Duration, Instant};
use rand::RngCore;
use crate::config::Config;

pub struct SmallFilesBenchmarker {
    path: String,
    name: String,
    time_limit: Duration,
    file_size: usize,
    files: Vec<PathBuf>,
    rnd_data: Vec<Vec<u8>>,
}

impl SmallFilesBenchmarker {
    pub fn new(path: &str, name: &str, config: &Config) -> Self {
        let files: Vec<PathBuf> = (0..config.small_file_count)
            .map(|i| PathBuf::from(path).join(format!("small_file_{}.dat", i)))
            .collect();
        
        Self {
            path: path.to_string(),
            name: name.to_string(),
            time_limit: Duration::from_secs(config.time_limit as u64),
            file_size: config.small_file_size,
            files,
            rnd_data: Vec::new(),
        }
    }

    fn write_files(&self) -> io::Result<usize> {
        let mut bytes_written = 0;
        let start = Instant::now();
        
        for (file_path, data) in self.files.iter().zip(self.rnd_data.iter()) {
            let mut file = File::create(file_path)?;
            bytes_written += file.write(data)?;
            
            if start.elapsed() > self.time_limit {
                break;
            }
        }
        
        Ok(bytes_written)
    }

    fn read_files(&self) -> io::Result<usize> {
        let mut bytes_read = 0;
        let start = Instant::now();
        
        for file_path in &self.files {
            if !file_path.exists() {
                continue;
            }
            
            let mut file = File::open(file_path)?;
            let mut buffer = Vec::new();
            let read = file.read_to_end(&mut buffer)?;
            bytes_read += read;
            
            if start.elapsed() > self.time_limit {
                break;
            }
        }
        
        Ok(bytes_read)
    }

    pub fn run(&mut self, output: &mut File)  -> io::Result<()> {
        // Prepare random data
        let mut rng = rand::rng();
        self.rnd_data = (0..self.files.len())
            .map(|_| {
                let mut data = vec![0u8; self.file_size];
                rng.fill_bytes(&mut data);
                data
            })
            .collect();
        
        // Write
        let start = Instant::now();
        let result = self.write_files()?;
        let duration = start.elapsed().as_secs_f64();
        let bandwidth = (result as f64) / duration;
        writeln!(output, "small files bandwidth, write, {}, {}, {}",
            self.name,
            self.path,
            bandwidth)?;
        output.flush()?;

        // Read
        let start = Instant::now();
        let result = self.read_files()?;
        let duration = start.elapsed().as_secs_f64();
        let bandwidth = (result as f64) / duration;
        writeln!(output, "small files bandwidth, read, {}, {}, {}",
            self.name,
            self.path,
            bandwidth)?;
        output.flush()?;

        // Cleanup
        for file in &self.files {
            std::fs::remove_file(file).unwrap();
        }

        Ok(())
    }
}
