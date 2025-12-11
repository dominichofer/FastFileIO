#pragma once
#include <chrono>
#include <filesystem>
#include <ostream>
#include <string>
#include <vector>
#include "config.h"

class LargeFileBenchmarker {
public:
    LargeFileBenchmarker(std::string path,
                         std::string name,
                         const Config&);

    void run(std::ostream& output);
                         
private:
    size_t write_chunk(size_t start_pos, size_t end_pos, size_t block_size);
    size_t read_chunk(size_t start_pos, size_t end_pos, size_t block_size);

    std::string path;
    std::string name;
    std::chrono::seconds time_limit;
    size_t file_size;
    std::vector<size_t> block_size;
    std::filesystem::path file;
    std::vector<uint8_t> rnd_data;
};
