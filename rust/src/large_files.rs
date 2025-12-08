use std::fs::{File, OpenOptions};
use std::io::{self, Write, Read, Seek, SeekFrom};
use std::path::PathBuf;
use std::time::Instant;
use crate::format::format_bytes;
use crate::measurements::{LargeFileBandwidth, IoDirection};
use rand::RngCore;

pub struct LargeFileBenchmarker {
    location: String,
    name: String,
    filename: PathBuf,
    file_size: u64,
    time_limit: u64,
    rnd_data: Vec<u8>,
}

impl LargeFileBenchmarker {
    pub fn new(location: &str, name: &str, file_size: u64, time_limit: u64) -> Self {
        let filename = PathBuf::from(location).join("large_file_test.dat");
        let mut rnd_data = vec![0u8; file_size as usize];
        rand::thread_rng().fill_bytes(&mut rnd_data);
        
        Self {
            location: location.to_string(),
            name: name.to_string(),
            filename,
            file_size,
            time_limit,
            rnd_data,
        }
    }

    pub fn cleanup(&self) -> io::Result<()> {
        if self.filename.exists() {
            std::fs::remove_file(&self.filename)?;
        }
        Ok(())
    }

    fn write_chunk(&self, start_pos: u64, end_pos: u64, block_size: u64) -> io::Result<u64> {
        let mut bytes_written = 0u64;
        let start = Instant::now();
        
        let mut file = OpenOptions::new()
            .write(true)
            .create(true)
            .truncate(true)
            .open(&self.filename)?;
        
        file.seek(SeekFrom::Start(start_pos))?;
        
        let mut pos = start_pos;
        while pos < end_pos {
            let chunk_size = std::cmp::min(block_size, end_pos - pos) as usize;
            let start_idx = pos as usize;
            let end_idx = start_idx + chunk_size;
            
            let written = file.write(&self.rnd_data[start_idx..end_idx])?;
            bytes_written += written as u64;
            pos += written as u64;
            
            let duration = start.elapsed().as_secs();
            if duration > self.time_limit {
                break;
            }
        }
        
        Ok(bytes_written)
    }

    fn read_chunk(&self, start_pos: u64, end_pos: u64, block_size: u64) -> io::Result<u64> {
        let mut bytes_read = 0u64;
        let start = Instant::now();
        
        let mut file = File::open(&self.filename)?;
        file.seek(SeekFrom::Start(start_pos))?;
        
        let mut buffer = vec![0u8; block_size as usize];
        let mut pos = start_pos;
        
        while pos < end_pos {
            let chunk_size = std::cmp::min(block_size, end_pos - pos) as usize;
            let read = file.read(&mut buffer[..chunk_size])?;
            if read == 0 {
                break;
            }
            bytes_read += read as u64;
            pos += read as u64;
            
            let duration = start.elapsed().as_secs();
            if duration > self.time_limit {
                break;
            }
        }
        
        Ok(bytes_read)
    }

    pub fn bench_write(&self, block_size: u64) -> io::Result<LargeFileBandwidth> {
        let start = Instant::now();
        let bytes_written = self.write_chunk(0, self.file_size, block_size)?;
        let duration = start.elapsed().as_secs_f64();
        let bandwidth = (bytes_written as f64) / duration / (1024.0 * 1024.0);
        
        println!("Large files write, {}, block size {}, {} in {:.2} s, {:.0} MiB/s",
            self.location,
            format_bytes(block_size),
            format_bytes(bytes_written),
            duration,
            bandwidth);
        
        Ok(LargeFileBandwidth::new(
            self.location.clone(),
            self.name.clone(),
            IoDirection::Write,
            block_size,
            bandwidth,
        ))
    }

    pub fn bench_read(&self, block_size: u64) -> io::Result<LargeFileBandwidth> {
        let start = Instant::now();
        let bytes_read = self.read_chunk(0, self.file_size, block_size)?;
        let duration = start.elapsed().as_secs_f64();
        let bandwidth = (bytes_read as f64) / duration / (1024.0 * 1024.0);
        
        println!("Large files read, {}, block size {}, {} in {:.2} s, {:.0} MiB/s",
            self.location,
            format_bytes(block_size),
            format_bytes(bytes_read),
            duration,
            bandwidth);
        
        Ok(LargeFileBandwidth::new(
            self.location.clone(),
            self.name.clone(),
            IoDirection::Read,
            block_size,
            bandwidth,
        ))
    }

    pub fn run(&self, block_size: u64, output_file: &str) -> io::Result<Vec<LargeFileBandwidth>> {
        let mut results = Vec::new();
        let mut file = OpenOptions::new()
            .create(true)
            .append(true)
            .open(output_file)?;
        
        let result = self.bench_write(block_size)?;
        writeln!(file, "{}", result)?;
        file.flush()?;
        results.push(result);
        
        let result = self.bench_read(block_size)?;
        writeln!(file, "{}", result)?;
        file.flush()?;
        results.push(result);
        
        self.cleanup()?;
        Ok(results)
    }
}
