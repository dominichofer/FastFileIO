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
    files: Vec<PathBuf>,
    rnd_data: Vec<Vec<u8>>,
}

impl SmallFilesBenchmarker {
    pub fn new(path: &str, name: &str, config: &Config) -> Self {
        let files: Vec<PathBuf> = (0..config.small_file_count)
            .map(|i| PathBuf::from(path).join(format!("small_file_{}.dat", i)))
            .collect();
        let mut rnd_data = Vec::new();
        for _ in 0..config.small_file_count {
            let mut data = vec![0u8; config.small_file_size as usize];
            rand::rng().fill_bytes(&mut data);
            rnd_data.push(data);
        }
        
        Self {
            path: path.to_string(),
            name: name.to_string(),
            time_limit: Duration::from_secs(config.time_limit as u64),
            files,
            rnd_data,
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
        // Write
        let start = Instant::now();
        let result = self.write_files()?;
        let duration = start.elapsed().as_secs_f64();
        let bandwidth = (result as f64) / duration;
        writeln!(output, "small files bandwidth, write, {:?}, {}, {}, {}",
            start,
            self.name,
            self.path,
            bandwidth)?;
        output.flush()?;

        // Read
        let start = Instant::now();
        let result = self.read_files()?;
        let duration = start.elapsed().as_secs_f64();
        let bandwidth = (result as f64) / duration;
        writeln!(output, "small files bandwidth, read, {:?}, {}, {}, {}",
            start,
            self.name,
            self.path,
            bandwidth)?;
        output.flush()?;

        // Cleanup
        for file_path in &self.files {
            if file_path.exists() {
                std::fs::remove_file(file_path)?;
            }
        }

        Ok(())
    }
}
