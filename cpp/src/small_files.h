#pragma once
#include <chrono>
#include <filesystem>
#include <ostream>
#include <string>
#include <vector>
#include "config.h"

class SmallFilesBenchmarker {
public:
    SmallFilesBenchmarker(std::string path,
                          std::string name,
                          const Config&);

    size_t write_files();
    size_t read_files();
    void run(std::ostream& output);

private:
    std::string path;
    std::string name;
    std::chrono::seconds time_limit;
    size_t file_size;
    std::vector<std::filesystem::path> files;
    std::vector<std::vector<uint8_t>> rnd_data;
};
