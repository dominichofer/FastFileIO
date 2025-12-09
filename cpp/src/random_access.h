#pragma once
#include "measurements.h"
#include <string>
#include <vector>

class RandomAccessBenchmarker {
public:
    RandomAccessBenchmarker(const std::string& location,
                            const std::string& name,
                            double time_limit = 5.0,
                            size_t random_accesses = 100000,
                            size_t big_file_size = 10ULL * 1024 * 1024 * 1024);
    
    ~RandomAccessBenchmarker();

    RandomAccess benchmark_write();
    RandomAccess benchmark_read();
    void run(const std::string& output_file);
    void cleanup();

private:
    std::string location_;
    std::string name_;
    double time_limit_;
    size_t random_accesses_;
    size_t big_file_size_;
    std::string file_path_;
    std::vector<size_t> positions_;
    std::vector<char> random_data_;

    void generate_positions();
    void generate_random_data();
    void create_file_for_reading();
};
