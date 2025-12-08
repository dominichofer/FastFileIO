use fastfileio::{run_all, run_random_access, run_large_files, run_small_files};
use std::env;

fn main() {
    let args: Vec<String> = env::args().collect();
    
    if args.len() < 2 {
        println!("Usage: fastfileio <command> [args...]");
        println!("Commands:");
        println!("  all <location> <name> <output_file> [repetitions] [config_file]");
        println!("  large <location> <name> <output_file> [repetitions] [config_file]");
        println!("  small <location> <name> <output_file> [repetitions] [config_file]");
        println!("  random <location> <name> <output_file> [repetitions] [config_file]");
        return;
    }

    let command = &args[1];
    
    match command.as_str() {
        "all" => {
            if args.len() < 5 {
                eprintln!("Usage: fastfileio all <location> <name> <output_file> [repetitions] [config_file]");
                return;
            }
            let location = &args[2];
            let name = &args[3];
            let output_file = &args[4];
            let repetitions = args.get(5).and_then(|s| s.parse().ok()).unwrap_or(1);
            let config_file = args.get(6).map(|s| s.as_str()).unwrap_or("fastfileio.cfg");
            
            if let Err(e) = run_all(location, name, output_file, repetitions, config_file) {
                eprintln!("Error: {}", e);
            }
        }
        "large" => {
            if args.len() < 5 {
                eprintln!("Usage: fastfileio large <location> <name> <output_file> [repetitions] [config_file]");
                return;
            }
            let location = &args[2];
            let name = &args[3];
            let output_file = &args[4];
            let repetitions = args.get(5).and_then(|s| s.parse().ok()).unwrap_or(1);
            let config_file = args.get(6).map(|s| s.as_str()).unwrap_or("fastfileio.cfg");
            
            if let Err(e) = run_large_files(location, name, output_file, repetitions, config_file) {
                eprintln!("Error: {}", e);
            }
        }
        "small" => {
            if args.len() < 5 {
                eprintln!("Usage: fastfileio small <location> <name> <output_file> [repetitions] [config_file]");
                return;
            }
            let location = &args[2];
            let name = &args[3];
            let output_file = &args[4];
            let repetitions = args.get(5).and_then(|s| s.parse().ok()).unwrap_or(1);
            let config_file = args.get(6).map(|s| s.as_str()).unwrap_or("fastfileio.cfg");
            
            if let Err(e) = run_small_files(location, name, output_file, repetitions, config_file) {
                eprintln!("Error: {}", e);
            }
        }
        "random" => {
            if args.len() < 5 {
                eprintln!("Usage: fastfileio random <location> <name> <output_file> [repetitions] [config_file]");
                return;
            }
            let location = &args[2];
            let name = &args[3];
            let output_file = &args[4];
            let repetitions = args.get(5).and_then(|s| s.parse().ok()).unwrap_or(1);
            let config_file = args.get(6).map(|s| s.as_str()).unwrap_or("fastfileio.cfg");
            
            if let Err(e) = run_random_access(location, name, output_file, repetitions, config_file) {
                eprintln!("Error: {}", e);
            }
        }
        _ => {
            eprintln!("Unknown command: {}", command);
            eprintln!("Valid commands: all, large, small, random");
        }
    }
}
