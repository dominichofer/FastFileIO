use chrono::{DateTime, Local};
use std::fmt;

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum IoDirection {
    Read,
    Write,
}

impl fmt::Display for IoDirection {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            IoDirection::Read => write!(f, "read"),
            IoDirection::Write => write!(f, "write"),
        }
    }
}

impl IoDirection {
    pub fn from_str(s: &str) -> Result<Self, String> {
        match s {
            "read" => Ok(IoDirection::Read),
            "write" => Ok(IoDirection::Write),
            _ => Err(format!("Unknown IoDirection: {}", s)),
        }
    }
}

#[derive(Debug, Clone)]
pub struct Measurement {
    pub timestamp: DateTime<Local>,
    pub location: String,
    pub name: String,
    pub direction: IoDirection,
}

impl Measurement {
    pub fn new(location: String, name: String, direction: IoDirection) -> Self {
        Self {
            timestamp: Local::now(),
            location,
            name,
            direction,
        }
    }
}

impl fmt::Display for Measurement {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "{}, {}, {}, {}", 
            self.timestamp.to_rfc3339(),
            self.location,
            self.name,
            self.direction)
    }
}

#[derive(Debug, Clone)]
pub struct LargeFileBandwidth {
    pub base: Measurement,
    pub block_size: u64,
    pub bandwidth: f64,  // MiB/s
}

impl LargeFileBandwidth {
    pub fn new(location: String, name: String, direction: IoDirection, block_size: u64, bandwidth: f64) -> Self {
        Self {
            base: Measurement::new(location, name, direction),
            block_size,
            bandwidth,
        }
    }
}

impl fmt::Display for LargeFileBandwidth {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "LargeFileBandwidth, {}, {}, {}", 
            self.base,
            self.block_size,
            self.bandwidth)
    }
}

#[derive(Debug, Clone)]
pub struct SmallFilesBandwidth {
    pub base: Measurement,
    pub bandwidth: f64,  // MiB/s
}

impl SmallFilesBandwidth {
    pub fn new(location: String, name: String, direction: IoDirection, bandwidth: f64) -> Self {
        Self {
            base: Measurement::new(location, name, direction),
            bandwidth,
        }
    }
}

impl fmt::Display for SmallFilesBandwidth {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "SmallFilesBandwidth, {}, {}", 
            self.base,
            self.bandwidth)
    }
}

#[derive(Debug, Clone)]
pub struct RandomAccess {
    pub base: Measurement,
    pub iops: f64,
}

impl RandomAccess {
    pub fn new(location: String, name: String, direction: IoDirection, iops: f64) -> Self {
        Self {
            base: Measurement::new(location, name, direction),
            iops,
        }
    }
}

impl fmt::Display for RandomAccess {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "RandomAccess, {}, {}", 
            self.base,
            self.iops)
    }
}
