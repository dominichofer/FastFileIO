use std::fs::{File, OpenOptions};
use std::io::{self, Write, Read, Seek, SeekFrom};
use std::path::PathBuf;
use std::time::Instant;
use crate::measurements::{RandomAccess, IoDirection};
use rand::seq::SliceRandom;
use rand::RngCore;

pub struct RandomAccessBenchmarker {
    location: String,
    name: String,
    filename: PathBuf,
    file_size: u64,
    sample_size: usize,
    time_limit: u64,
}

impl RandomAccessBenchmarker {
    pub fn new(location: &str, name: &str, file_size: u64, sample_size: usize, time_limit: u64) -> io::Result<Self> {
        let filename = PathBuf::from(location).join("random_access_test_file.dat");
        
        // Create file with random data
        let mut file = File::create(&filename)?;
        let mut rnd_data = vec![0u8; file_size as usize];
        rand::thread_rng().fill_bytes(&mut rnd_data);
        file.write_all(&rnd_data)?;
        
        Ok(Self {
            location: location.to_string(),
            name: name.to_string(),
            filename,
            file_size,
            sample_size,
            time_limit,
        })
    }

    pub fn cleanup(&self) -> io::Result<()> {
        if self.filename.exists() {
            std::fs::remove_file(&self.filename)?;
        }
        Ok(())
    }

    pub fn bench_write(&self) -> io::Result<RandomAccess> {
        let mut positions: Vec<u64> = (0..self.file_size).collect();
        let mut rng = rand::thread_rng();
        positions.shuffle(&mut rng);
        let positions: Vec<u64> = positions.into_iter().take(self.sample_size).collect();

        let start = Instant::now();
        let mut writes = 0u64;
        
        let mut file = OpenOptions::new()
            .write(true)
            .open(&self.filename)?;
        
        for pos in positions {
            file.seek(SeekFrom::Start(pos))?;
            writes += file.write(&[0u8])? as u64;
            
            let duration = start.elapsed().as_secs();
            if duration > self.time_limit {
                break;
            }
        }
        
        let duration = start.elapsed().as_secs_f64();
        let iops = writes as f64 / duration;
        
        println!("Random writes, {}, {} in {:.2} s, {:.0} T/s",
            self.location,
            writes,
            duration,
            iops);
        
        Ok(RandomAccess::new(
            self.location.clone(),
            self.name.clone(),
            IoDirection::Write,
            iops,
        ))
    }

    pub fn bench_read(&self) -> io::Result<RandomAccess> {
        let mut positions: Vec<u64> = (0..self.file_size).collect();
        let mut rng = rand::thread_rng();
        positions.shuffle(&mut rng);
        let positions: Vec<u64> = positions.into_iter().take(self.sample_size).collect();

        let start = Instant::now();
        let mut reads = 0u64;
        
        let mut file = File::open(&self.filename)?;
        let mut buffer = [0u8; 1];
        
        for pos in positions {
            file.seek(SeekFrom::Start(pos))?;
            let read = file.read(&mut buffer)?;
            reads += read as u64;
            
            let duration = start.elapsed().as_secs();
            if duration > self.time_limit {
                break;
            }
        }
        
        let duration = start.elapsed().as_secs_f64();
        let iops = reads as f64 / duration;
        
        println!("Random reads, {}, {} in {:.2} s, {:.0} T/s",
            self.location,
            reads,
            duration,
            iops);
        
        Ok(RandomAccess::new(
            self.location.clone(),
            self.name.clone(),
            IoDirection::Read,
            iops,
        ))
    }

    pub fn run(&self, output_file: &str) -> io::Result<Vec<RandomAccess>> {
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
        
        Ok(results)
    }
}
