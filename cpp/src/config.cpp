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
    std::string current_key;
    
    while (std::getline(buffer, line)) {
        // Remove comments
        auto comment_pos = line.find('#');
        if (comment_pos != std::string::npos) {
            line = line.substr(0, comment_pos);
        }
        
        // Trim trailing whitespace
        while (!line.empty() && std::isspace(line.back())) {
            line.pop_back();
        }
        
        // Skip empty lines
        if (line.empty()) continue;
        
        // Check for list item (starts with spaces/tabs and -)
        if (line.find_first_not_of(" \t") != std::string::npos && 
            line[line.find_first_not_of(" \t")] == '-') {
            auto value_start = line.find('-') + 1;
            while (value_start < line.size() && std::isspace(line[value_start])) {
                value_start++;
            }
            std::string value = line.substr(value_start);
            if (current_key == "block_sizes") {
                config.block_size.push_back(std::stoul(value));
            }
            continue;
        }
        
        // Parse key: value
        auto delimiter_pos = line.find(':');
        if (delimiter_pos == std::string::npos) continue;
        
        std::string key = line.substr(0, delimiter_pos);
        current_key = key;
        
        std::string value = line.substr(delimiter_pos + 1);
        // Trim leading whitespace from value
        auto value_start = value.find_first_not_of(" \t");
        if (value_start != std::string::npos) {
            value = value.substr(value_start);
        } else {
            value = "";
        }
        
        if (key == "time_limit" && !value.empty()) {
            config.time_limit = std::stoul(value);
        } else if (key == "random_accesses" && !value.empty()) {
            config.random_accesses = std::stoul(value);
        } else if (key == "small_file_count" && !value.empty()) {
            config.small_file_count = std::stoul(value);
        } else if (key == "small_file_size" && !value.empty()) {
            config.small_file_size = std::stoul(value);
        } else if (key == "large_file_size" && !value.empty()) {
            config.large_file_size = std::stoul(value);
        }
    }
    
    return config;
}
