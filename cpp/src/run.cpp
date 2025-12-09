#include "run.h"
#include "large_files.h"
#include "small_files.h"
#include "random_access.h"
#include "format.h"
#include <iostream>
#include <fstream>
#include <sstream>
#include <filesystem>

namespace fs = std::filesystem;

Config::Config() {
    block_sizes = generate_block_sizes();
}

Config Config::load(const std::string& config_file) {
    Config config;
    
    if (!fs::exists(config_file)) {
        return config;
    }
    
    std::ifstream file(config_file);
    if (!file) {
        std::cerr << "Warning: Could not open config file: " << config_file << std::endl;
        return config;
    }
    
    std::string line;
    while (std::getline(file, line)) {
        // Skip empty lines and comments
        if (line.empty() || line[0] == '#') {
            continue;
        }
        
        size_t pos = line.find('=');
        if (pos == std::string::npos) {
            continue;
        }
        
        std::string key = line.substr(0, pos);
        std::string value = line.substr(pos + 1);
        
        // Trim whitespace
        key.erase(0, key.find_first_not_of(" \t"));
        key.erase(key.find_last_not_of(" \t") + 1);
        value.erase(0, value.find_first_not_of(" \t"));
        value.erase(value.find_last_not_of(" \t") + 1);
        
        try {
            if (key == "time_limit") {
                config.time_limit = std::stod(value);
            } else if (key == "random_accesses") {
                config.random_accesses = std::stoull(value);
            } else if (key == "small_files_count") {
                config.small_files_count = std::stoull(value);
            } else if (key == "small_file_size") {
                config.small_file_size = std::stoull(value);
            } else if (key == "big_file_size") {
                config.big_file_size = std::stoull(value);
            }
        } catch (const std::exception& e) {
            std::cerr << "Warning: Failed to parse config value for " << key 
                     << ": " << e.what() << std::endl;
        }
    }
    
    file.close();
    return config;
}

void run_large_files(const std::string& location,
                     const std::string& name,
                     const std::string& output_file,
                     const Config& config) {
    std::cout << "Running large files benchmark..." << std::endl;
    
    LargeFileBenchmarker benchmarker(
        location, name, config.time_limit, config.big_file_size
    );
    
    benchmarker.run(output_file, config.block_sizes);
    benchmarker.cleanup();
    
    std::cout << "Large files benchmark completed." << std::endl;
}

void run_small_files(const std::string& location,
                     const std::string& name,
                     const std::string& output_file,
                     const Config& config) {
    std::cout << "Running small files benchmark..." << std::endl;
    
    SmallFilesBenchmarker benchmarker(
        location, name, config.time_limit, 
        config.small_files_count, config.small_file_size
    );
    
    benchmarker.run(output_file);
    benchmarker.cleanup();
    
    std::cout << "Small files benchmark completed." << std::endl;
}

void run_random_access(const std::string& location,
                       const std::string& name,
                       const std::string& output_file,
                       const Config& config) {
    std::cout << "Running random access benchmark..." << std::endl;
    
    RandomAccessBenchmarker benchmarker(
        location, name, config.time_limit, 
        config.random_accesses, config.big_file_size
    );
    
    benchmarker.run(output_file);
    benchmarker.cleanup();
    
    std::cout << "Random access benchmark completed." << std::endl;
}

void run_all(const std::string& location,
             const std::string& name,
             const std::string& output_file,
             const Config& config) {
    std::cout << "Running all benchmarks for location: " << location << std::endl;
    
    run_large_files(location, name, output_file, config);
    run_small_files(location, name, output_file, config);
    run_random_access(location, name, output_file, config);
    
    std::cout << "All benchmarks completed." << std::endl;
}
