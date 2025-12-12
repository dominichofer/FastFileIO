use std::fs::File;
use std::io::{self, Write, Read, Seek, SeekFrom};
use std::path::PathBuf;
use std::time::{Duration, Instant};
use rand::RngCore;
use crate::config::Config;

pub struct LargeFileBenchmarker {
    path: String,
    name: String,
    time_limit: Duration,
    file_size: usize,
    block_size: Vec<usize>,
    file: PathBuf,
    rnd_data: Vec<u8>,
}

impl LargeFileBenchmarker {
    pub fn new(path: &str, name: &str, config: &Config) -> Self {
        Self {
            path: path.to_string(),
            name: name.to_string(),
            time_limit: Duration::from_secs(config.time_limit as u64),
            file_size: config.large_file_size,
            block_size: config.block_sizes.clone(),
            file: PathBuf::from(path).join("large_file.dat"),
            rnd_data: vec![0u8; config.large_file_size]
        }
    }

    fn write_chunk(&self, start_pos: usize, end_pos: usize, block_size: usize) -> io::Result<usize> {
        let mut bytes_written = 0;
        let start = Instant::now();        
        let mut file = File::create(&self.file)?;
        file.seek(SeekFrom::Start(start_pos as u64))?;
        
        for i in (start_pos..end_pos).step_by(block_size) {            
            let written = file.write(&self.rnd_data[i..i + block_size])?;
            bytes_written += written;

            if start.elapsed() > self.time_limit {
                break;
            }
        }
        
        Ok(bytes_written)
    }

    fn read_chunk(&self, start_pos: usize, end_pos: usize, block_size: usize) -> io::Result<usize> {
        let mut bytes_read = 0;
        let start = Instant::now();
        
        let mut file = File::open(&self.file)?;
        file.seek(SeekFrom::Start(start_pos as u64))?;
        
        let mut buffer = vec![0u8; block_size];
        for _ in (start_pos..end_pos).step_by(block_size) {
            let read = file.read(&mut buffer)?;
            if read == 0 {
                break;
            }
            bytes_read += read;

            if start.elapsed() > self.time_limit {
                break;
            }
        }
        Ok(bytes_read)
    }

    pub fn run(&mut self, output: &mut File)  -> io::Result<()> {
        for block_size in &self.block_size {
            // Prepare random data
            rand::rng().fill_bytes(&mut self.rnd_data);

            // Write
            let start = Instant::now();
            let result = self.write_chunk(0, self.file_size, *block_size)?;
            let duration = start.elapsed().as_secs_f64();
            let bandwidth = (result as f64) / duration;
            writeln!(output, "large file bandwidth, write, {}, {}, {}, {}",
                self.name,
                self.path,
                block_size,
                bandwidth)?;
            output.flush()?;

            // Read
            let start = Instant::now();
            let result = self.read_chunk(0, self.file_size, *block_size)?;
            let duration = start.elapsed().as_secs_f64();
            let bandwidth = (result as f64) / duration;
            writeln!(output, "large file bandwidth, read, {}, {}, {}, {}",
                self.name,
                self.path,
                block_size,
                bandwidth)?;
            output.flush()?;
        }

        // Cleanup
        std::fs::remove_file(&self.file)?;
        Ok(())
    }
}
