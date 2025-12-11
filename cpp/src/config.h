#pragma once
#include <string>
#include <vector>

struct Config {
    size_t time_limit;
    size_t random_accesses;
    size_t small_file_count;
    size_t small_file_size;
    size_t large_file_size;
    std::vector<size_t> block_size;

    static Config load(const std::string& path);
};
