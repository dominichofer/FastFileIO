#pragma once
#include "measurements.h"
#include <string>
#include <vector>

class SmallFilesBenchmarker {
public:
    SmallFilesBenchmarker(const std::string& location,
                          const std::string& name,
                          double time_limit = 5.0,
                          size_t small_files_count = 10000,
                          size_t small_file_size = 1024);
    
    ~SmallFilesBenchmarker();

    SmallFilesBandwidth benchmark_write();
    SmallFilesBandwidth benchmark_read();
    void run(const std::string& output_file);
    void cleanup();

private:
    std::string location_;
    std::string name_;
    double time_limit_;
    size_t small_files_count_;
    size_t small_file_size_;
    std::string dir_path_;
    std::vector<char> random_data_;

    void generate_random_data();
};
