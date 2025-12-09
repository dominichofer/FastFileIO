#pragma once
#include <string>
#include <vector>

struct Config {
    double time_limit = 5.0;
    size_t random_accesses = 100000;
    size_t small_files_count = 10000;
    size_t small_file_size = 1024;
    size_t big_file_size = 10ULL * 1024 * 1024 * 1024;
    std::vector<size_t> block_sizes;
    
    Config();
    
    // Load configuration from file (optional)
    static Config load(const std::string& config_file);
};

void run_large_files(const std::string& location,
                     const std::string& name,
                     const std::string& output_file,
                     const Config& config = Config());

void run_small_files(const std::string& location,
                     const std::string& name,
                     const std::string& output_file,
                     const Config& config = Config());

void run_random_access(const std::string& location,
                       const std::string& name,
                       const std::string& output_file,
                       const Config& config = Config());

void run_all(const std::string& location,
             const std::string& name,
             const std::string& output_file,
             const Config& config = Config());
