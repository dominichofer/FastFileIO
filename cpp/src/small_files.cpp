#include "small_files.h"
#include "format.h"
#include <iostream>
#include <fstream>
#include <chrono>
#include <random>
#include <filesystem>

namespace fs = std::filesystem;

SmallFilesBenchmarker::SmallFilesBenchmarker(const std::string& location,
                                             const std::string& name,
                                             double time_limit,
                                             size_t small_files_count,
                                             size_t small_file_size)
    : location_(location), name_(name), time_limit_(time_limit),
      small_files_count_(small_files_count), small_file_size_(small_file_size) {
    
    dir_path_ = (fs::path(location) / "small_files").string();
    fs::create_directories(dir_path_);
    generate_random_data();
}

SmallFilesBenchmarker::~SmallFilesBenchmarker() {
    // Destructor
}

void SmallFilesBenchmarker::generate_random_data() {
    random_data_.resize(small_file_size_);
    
    std::random_device rd;
    std::mt19937 gen(rd());
    std::uniform_int_distribution<> dis(0, 255);
    
    for (auto& byte : random_data_) {
        byte = static_cast<char>(dis(gen));
    }
}

SmallFilesBandwidth SmallFilesBenchmarker::benchmark_write() {
    auto start = std::chrono::steady_clock::now();
    size_t files_written = 0;
    
    for (size_t i = 0; i < small_files_count_; ++i) {
        auto elapsed = std::chrono::duration<double>(
            std::chrono::steady_clock::now() - start).count();
        
        if (elapsed > time_limit_) {
            break;
        }
        
        std::string file_path = (fs::path(dir_path_) / ("file_" + std::to_string(i) + ".bin")).string();
        std::ofstream file(file_path, std::ios::binary);
        
        if (!file) {
            throw std::runtime_error("Failed to create file: " + file_path);
        }
        
        file.write(random_data_.data(), small_file_size_);
        file.close();
        
        files_written++;
    }
    
    auto end = std::chrono::steady_clock::now();
    double elapsed = std::chrono::duration<double>(end - start).count();
    size_t total_bytes = files_written * small_file_size_;
    double bandwidth = (total_bytes / (1024.0 * 1024.0)) / elapsed;
    
    SmallFilesBandwidth m;
    m.timestamp = std::chrono::system_clock::now();
    m.location = dir_path_;
    m.name = name_;
    m.direction = IoDirection::WRITE;
    m.bandwidth = bandwidth;
    return m;
}

SmallFilesBandwidth SmallFilesBenchmarker::benchmark_read() {
    auto start = std::chrono::steady_clock::now();
    size_t files_read = 0;
    std::vector<char> buffer(small_file_size_);
    
    for (size_t i = 0; i < small_files_count_; ++i) {
        auto elapsed = std::chrono::duration<double>(
            std::chrono::steady_clock::now() - start).count();
        
        if (elapsed > time_limit_) {
            break;
        }
        
        std::string file_path = (fs::path(dir_path_) / ("file_" + std::to_string(i) + ".bin")).string();
        
        if (!fs::exists(file_path)) {
            break;
        }
        
        std::ifstream file(file_path, std::ios::binary);
        
        if (!file) {
            throw std::runtime_error("Failed to open file: " + file_path);
        }
        
        file.read(buffer.data(), small_file_size_);
        file.close();
        
        files_read++;
    }
    
    auto end = std::chrono::steady_clock::now();
    double elapsed = std::chrono::duration<double>(end - start).count();
    size_t total_bytes = files_read * small_file_size_;
    double bandwidth = (total_bytes / (1024.0 * 1024.0)) / elapsed;
    
    SmallFilesBandwidth m;
    m.timestamp = std::chrono::system_clock::now();
    m.location = dir_path_;
    m.name = name_;
    m.direction = IoDirection::READ;
    m.bandwidth = bandwidth;
    return m;
}

void SmallFilesBenchmarker::run(const std::string& output_file) {
    std::ofstream out(output_file, std::ios::app);
    if (!out) {
        throw std::runtime_error("Failed to open output file: " + output_file);
    }
    
    try {
        std::cout << "Small files write: " << format_with_apostrophes(small_files_count_) 
                 << " files" << std::endl;
        auto write_result = benchmark_write();
        out << write_result.to_string() << std::endl;
        out.flush();
        
        std::cout << "Small files read: " << format_with_apostrophes(small_files_count_) 
                 << " files" << std::endl;
        auto read_result = benchmark_read();
        out << read_result.to_string() << std::endl;
        out.flush();
    } catch (const std::exception& e) {
        std::cerr << "Error in small files benchmark: " << e.what() << std::endl;
    }
    
    out.close();
}

void SmallFilesBenchmarker::cleanup() {
    if (fs::exists(dir_path_)) {
        fs::remove_all(dir_path_);
    }
}
