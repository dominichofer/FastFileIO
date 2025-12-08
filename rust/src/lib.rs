pub mod format;
pub mod measurements;
pub mod large_files;
pub mod small_files;
pub mod random_access;
pub mod config;
pub mod run;

pub use run::{run_all, run_random_access, run_large_files, run_small_files};
