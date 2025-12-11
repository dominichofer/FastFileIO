use std::fs::File;
use std::io::{self, Write, Read, Seek, SeekFrom};
use std::path::PathBuf;
use std::time::{Duration, Instant};
use rand::RngCore;
use crate::config::Config;

pub struct RandomAccessBenchmarker {
    path: String,
    name: String,
    time_limit: Duration,
    file_size: usize,
    repetitions: usize,
    file: PathBuf,
}

impl RandomAccessBenchmarker {
    pub fn new(path: &str, name: &str, config: &Config) -> Self {        
        Self {
            path: path.to_string(),
            name: name.to_string(),
            time_limit: Duration::from_secs(config.time_limit as u64),
            file_size: config.large_file_size,
            repetitions: config.random_accesses,
            file: PathBuf::from(path).join("random_access_file.dat"),
        }
    }

    pub fn bench_write(&self) -> io::Result<usize> {
        let mut rnd_pos: Vec<u64> = Vec::new();
        let mut rng = rand::rng();
        for _ in 0..self.repetitions {
            let pos = rng.next_u64() % (self.file_size as u64);
            rnd_pos.push(pos);
        }

        let start = Instant::now();
        let mut writes = 0;
        
        let mut file = File::options()
            .read(true)
            .write(true)
            .open(&self.file)?;
        
        for pos in rnd_pos {
            file.seek(SeekFrom::Start(pos))?;
            writes += file.write(&[0u8])?;
            
            if start.elapsed() > self.time_limit {
                break;
            }
        }
        Ok(writes)
    }

    pub fn bench_read(&self) -> io::Result<usize> {
        let mut rnd_pos: Vec<u64> = Vec::new();
        let mut rng = rand::rng();
        for _ in 0..self.repetitions {
            let pos = rng.next_u64() % (self.file_size as u64);
            rnd_pos.push(pos);
        }

        let start = Instant::now();
        let mut reads = 0;
        
        let mut file = File::open(&self.file)?;
        let mut buffer = [0u8; 1];
        
        for pos in rnd_pos {
            file.seek(SeekFrom::Start(pos))?;
            let read = file.read(&mut buffer)?;
            reads += read;
            
            if start.elapsed() > self.time_limit {
                break;
            }
        }
        Ok(reads)
    }

    pub fn run(&mut self, output: &mut File)  -> io::Result<()> {
        // Create file with random data
        let mut file = File::create(&self.file)?;
        let mut rnd_data = vec![0u8; self.file_size];
        rand::rng().fill_bytes(&mut rnd_data);
        file.write_all(&rnd_data)?;
        drop(file);

        // Write
        let start = Instant::now();
        let result = self.bench_write()?;
        let duration = start.elapsed().as_secs_f64();
        let iops = (result as f64) / duration;
        writeln!(output, "random access bandwidth, write, {:?}, {}, {}, {}",
            start,
            self.name,
            self.path,
            iops)?;
        output.flush()?;

        // Read
        let start = Instant::now();
        let result = self.bench_read()?;
        let duration = start.elapsed().as_secs_f64();
        let iops = (result as f64) / duration;
        writeln!(output, "random access bandwidth, read, {:?}, {}, {}, {}",
            start,
            self.name,
            self.path,
            iops)?;
        output.flush()?;

        // Cleanup
        std::fs::remove_file(&self.file)?;

        Ok(())
    }
}
