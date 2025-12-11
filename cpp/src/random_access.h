#pragma once
#include <chrono>
#include <filesystem>
#include <ostream>
#include <string>
#include <vector>
#include "config.h"

class RandomAccessBenchmarker {
public:
    RandomAccessBenchmarker(std::string path,
                            std::string name,
                            const Config&);
    void run(std::ostream& output);

private:
    size_t bench_write();
    size_t bench_read();

    std::string path;
    std::string name;
    std::chrono::seconds time_limit;
    size_t file_size;
    size_t repetitions;
    std::filesystem::path file;
};
