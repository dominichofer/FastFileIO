#include "config.h"
#include <fstream>
#include <sstream>
#include <stdexcept>

Config Config::load(const std::string& path) {
    std::ifstream file(path);
    if (!file.is_open()) {
        throw std::runtime_error("Failed to read config file");
    }
    std::stringstream buffer;
    buffer << file.rdbuf();
    
    Config config;
    std::string line;
    while (std::getline(buffer, line)) {
        auto delimiter_pos = line.find('=');
        if (delimiter_pos == std::string::npos)
            continue;
        std::string key = line.substr(0, delimiter_pos);
        std::string value = line.substr(delimiter_pos + 1);
        if (key == "time_limit") {
            config.time_limit = std::stoul(value);
        } else if (key == "random_accesses") {
            config.random_accesses = std::stoul(value);
        } else if (key == "small_file_count") {
            config.small_file_count = std::stoul(value);
        } else if (key == "small_file_size") {
            config.small_file_size = std::stoul(value);
        } else if (key == "large_file_size") {
            config.large_file_size = std::stoul(value);
        } else if (key == "block_size") {
            std::istringstream ss(value);
            std::string block;
            while (std::getline(ss, block, ',')) {
                config.block_size.push_back(std::stoul(block));
            }
        }
    }
    
    return config;
}
