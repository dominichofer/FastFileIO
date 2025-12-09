#include "large_files.h"
#include "format.h"
#include <iostream>
#include <fstream>
#include <chrono>
#include <random>
#include <filesystem>
#include <cstring>

namespace fs = std::filesystem;

LargeFileBenchmarker::LargeFileBenchmarker(const std::string& location,
                                           const std::string& name,
                                           double time_limit,
                                           size_t big_file_size)
    : location_(location), name_(name), time_limit_(time_limit), 
      big_file_size_(big_file_size) {
    
    file_path_ = (fs::path(location) / "big_file.bin").string();
    generate_random_data();
}

LargeFileBenchmarker::~LargeFileBenchmarker() {
    // Destructor
}

void LargeFileBenchmarker::generate_random_data() {
    // Generate enough random data for the largest block size (1 GB)
    size_t max_block_size = 1ULL << 30;
    random_data_.resize(max_block_size);
    
    std::random_device rd;
    std::mt19937 gen(rd());
    std::uniform_int_distribution<> dis(0, 255);
    
    for (auto& byte : random_data_) {
        byte = static_cast<char>(dis(gen));
    }
}

LargeFileBandwidth LargeFileBenchmarker::benchmark_write(size_t block_size) {
    auto start = std::chrono::steady_clock::now();
    size_t bytes_written = 0;
    
    std::ofstream file(file_path_, std::ios::binary | std::ios::trunc);
    if (!file) {
        throw std::runtime_error("Failed to open file for writing: " + file_path_);
    }
    
    while (bytes_written < big_file_size_) {
        auto elapsed = std::chrono::duration<double>(
            std::chrono::steady_clock::now() - start).count();
        
        if (elapsed > time_limit_) {
            break;
        }
        
        size_t to_write = std::min(block_size, big_file_size_ - bytes_written);
        file.write(random_data_.data(), to_write);
        
        if (!file) {
            throw std::runtime_error("Write failed");
        }
        
        bytes_written += to_write;
    }
    
    file.close();
    
    auto end = std::chrono::steady_clock::now();
    double elapsed = std::chrono::duration<double>(end - start).count();
    double bandwidth = (bytes_written / (1024.0 * 1024.0)) / elapsed;
    
    return LargeFileBandwidth {
        std::chrono::system_clock::now(),
        file_path_,
        name_,
        IoDirection::WRITE,
        block_size,
        bandwidth
    };
}

LargeFileBandwidth LargeFileBenchmarker::benchmark_read(size_t block_size) {
    // Ensure file exists for reading
    if (!fs::exists(file_path_)) {
        // Create file if it doesn't exist
        auto write_result = benchmark_write(1ULL << 20); // Use 1MB blocks to create file
    }
    
    auto start = std::chrono::steady_clock::now();
    size_t bytes_read = 0;
    
    std::ifstream file(file_path_, std::ios::binary);
    if (!file) {
        throw std::runtime_error("Failed to open file for reading: " + file_path_);
    }
    
    std::vector<char> buffer(block_size);
    
    while (bytes_read < big_file_size_) {
        auto elapsed = std::chrono::duration<double>(
            std::chrono::steady_clock::now() - start).count();
        
        if (elapsed > time_limit_) {
            break;
        }
        
        size_t to_read = std::min(block_size, big_file_size_ - bytes_read);
        file.read(buffer.data(), to_read);
        
        size_t actually_read = file.gcount();
        if (actually_read == 0) {
            break;
        }
        
        bytes_read += actually_read;
    }
    
    file.close();
    
    auto end = std::chrono::steady_clock::now();
    double elapsed = std::chrono::duration<double>(end - start).count();
    double bandwidth = (bytes_read / (1024.0 * 1024.0)) / elapsed;
    
    return LargeFileBandwidth {
        std::chrono::system_clock::now(),
        file_path_,
        name_,
        IoDirection::READ,
        block_size,
        bandwidth
    };
}

void LargeFileBenchmarker::run(const std::string& output_file, 
                               const std::vector<size_t>& block_sizes) {
    std::ofstream out(output_file, std::ios::app);
    if (!out) {
        throw std::runtime_error("Failed to open output file: " + output_file);
    }
    
    for (size_t block_size : block_sizes) {
        try {
            std::cout << "Large files write: " << format_with_apostrophes(block_size) 
                     << " bytes" << std::endl;
            auto write_result = benchmark_write(block_size);
            out << write_result.to_string() << std::endl;
            out.flush();
            
            std::cout << "Large files read: " << format_with_apostrophes(block_size) 
                     << " bytes" << std::endl;
            auto read_result = benchmark_read(block_size);
            out << read_result.to_string() << std::endl;
            out.flush();
        } catch (const std::exception& e) {
            std::cerr << "Error with block size " << block_size << ": " 
                     << e.what() << std::endl;
        }
    }
    
    out.close();
}

void LargeFileBenchmarker::cleanup() {
    if (fs::exists(file_path_)) {
        fs::remove(file_path_);
    }
}
