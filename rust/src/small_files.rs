use std::fs::{File, OpenOptions};
use std::io::{self, Write, Read};
use std::path::PathBuf;
use std::time::Instant;
use crate::format::format_bytes;
use crate::measurements::{SmallFilesBandwidth, IoDirection};
use rand::RngCore;

pub struct SmallFilesBenchmarker {
    location: String,
    name: String,
    files: Vec<PathBuf>,
    time_limit: u64,
    rnd_data: Vec<Vec<u8>>,
}

impl SmallFilesBenchmarker {
    pub fn new(location: &str, name: &str, file_size: u64, files_count: usize, time_limit: u64) -> Self {
        let files: Vec<PathBuf> = (0..files_count)
            .map(|i| PathBuf::from(location).join(format!("smallfile_{}.dat", i)))
            .collect();
        
        let mut rnd_data = Vec::new();
        for _ in 0..files_count {
            let mut data = vec![0u8; file_size as usize];
            rand::thread_rng().fill_bytes(&mut data);
            rnd_data.push(data);
        }
        
        Self {
            location: location.to_string(),
            name: name.to_string(),
            files,
            time_limit,
            rnd_data,
        }
    }

    pub fn cleanup(&self) -> io::Result<()> {
        for file in &self.files {
            if file.exists() {
                let _ = std::fs::remove_file(file);
            }
        }
        Ok(())
    }

    fn write_files(&self) -> io::Result<u64> {
        let mut bytes_written = 0u64;
        let start = Instant::now();
        
        for (file_path, data) in self.files.iter().zip(self.rnd_data.iter()) {
            let mut file = File::create(file_path)?;
            bytes_written += file.write(data)? as u64;
            
            let duration = start.elapsed().as_secs();
            if duration > self.time_limit {
                break;
            }
        }
        
        Ok(bytes_written)
    }

    fn read_files(&self) -> io::Result<u64> {
        let mut bytes_read = 0u64;
        let start = Instant::now();
        
        for file_path in &self.files {
            if !file_path.exists() {
                continue;
            }
            
            let mut file = File::open(file_path)?;
            let mut buffer = Vec::new();
            let read = file.read_to_end(&mut buffer)?;
            if read == 0 {
                break;
            }
            bytes_read += read as u64;
            
            let duration = start.elapsed().as_secs();
            if duration > self.time_limit {
                break;
            }
        }
        
        Ok(bytes_read)
    }

    pub fn bench_write(&self) -> io::Result<SmallFilesBandwidth> {
        let start = Instant::now();
        let bytes_written = self.write_files()?;
        let duration = start.elapsed().as_secs_f64();
        let bandwidth = (bytes_written as f64) / duration / (1024.0 * 1024.0);
        
        println!("Small files write, {}, {} in {:.2} s, {:.0} MiB/s",
            self.location,
            format_bytes(bytes_written),
            duration,
            bandwidth);
        
        Ok(SmallFilesBandwidth::new(
            self.location.clone(),
            self.name.clone(),
            IoDirection::Write,
            bandwidth,
        ))
    }

    pub fn bench_read(&self) -> io::Result<SmallFilesBandwidth> {
        let start = Instant::now();
        let bytes_read = self.read_files()?;
        let duration = start.elapsed().as_secs_f64();
        let bandwidth = (bytes_read as f64) / duration / (1024.0 * 1024.0);
        
        println!("Small files read, {}, {} in {:.2} s, {:.0} MiB/s",
            self.location,
            format_bytes(bytes_read),
            duration,
            bandwidth);
        
        Ok(SmallFilesBandwidth::new(
            self.location.clone(),
            self.name.clone(),
            IoDirection::Read,
            bandwidth,
        ))
    }

    pub fn run(&self, output_file: &str) -> io::Result<Vec<SmallFilesBandwidth>> {
        let mut results = Vec::new();
        let mut file = OpenOptions::new()
            .create(true)
            .append(true)
            .open(output_file)?;
        
        let result = self.bench_write()?;
        writeln!(file, "{}", result)?;
        std::io::Write::flush(&mut file)?;
        results.push(result);
        
        let result = self.bench_read()?;
        writeln!(file, "{}", result)?;
        std::io::Write::flush(&mut file)?;
        results.push(result);
        
        self.cleanup()?;
        Ok(results)
    }
}
