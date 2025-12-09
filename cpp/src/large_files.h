#pragma once
#include "measurements.h"
#include <string>
#include <vector>
#include <fstream>

class LargeFileBenchmarker {
public:
    LargeFileBenchmarker(const std::string& location,
                         const std::string& name,
                         double time_limit = 5.0,
                         size_t big_file_size = 10ULL * 1024 * 1024 * 1024);
    
    ~LargeFileBenchmarker();

    LargeFileBandwidth benchmark_write(size_t block_size);
    LargeFileBandwidth benchmark_read(size_t block_size);
    void run(const std::string& output_file, const std::vector<size_t>& block_sizes);
    void cleanup();

private:
    std::string location_;
    std::string name_;
    double time_limit_;
    size_t big_file_size_;
    std::string file_path_;
    std::vector<char> random_data_;

    void generate_random_data();
};
