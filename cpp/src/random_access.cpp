#include "random_access.h"
#include "format.h"
#include <iostream>
#include <fstream>
#include <chrono>
#include <random>
#include <filesystem>
#include <algorithm>

namespace fs = std::filesystem;

RandomAccessBenchmarker::RandomAccessBenchmarker(const std::string& location,
                                                 const std::string& name,
                                                 double time_limit,
                                                 size_t random_accesses,
                                                 size_t big_file_size)
    : location_(location), name_(name), time_limit_(time_limit),
      random_accesses_(random_accesses), big_file_size_(big_file_size) {
    
    file_path_ = (fs::path(location) / "random_access.bin").string();
    generate_positions();
    generate_random_data();
}

RandomAccessBenchmarker::~RandomAccessBenchmarker() {
    // Destructor
}

void RandomAccessBenchmarker::generate_positions() {
    positions_.resize(random_accesses_);
    
    std::random_device rd;
    std::mt19937_64 gen(rd());
    std::uniform_int_distribution<size_t> dis(0, big_file_size_ - 1);
    
    for (auto& pos : positions_) {
        pos = dis(gen);
    }
}

void RandomAccessBenchmarker::generate_random_data() {
    random_data_.resize(random_accesses_);
    
    std::random_device rd;
    std::mt19937 gen(rd());
    std::uniform_int_distribution<> dis(0, 255);
    
    for (auto& byte : random_data_) {
        byte = static_cast<char>(dis(gen));
    }
}

void RandomAccessBenchmarker::create_file_for_reading() {
    if (fs::exists(file_path_)) {
        return;
    }
    
    std::ofstream file(file_path_, std::ios::binary);
    if (!file) {
        throw std::runtime_error("Failed to create file: " + file_path_);
    }
    
    // Create a sparse file by seeking to the end
    file.seekp(big_file_size_ - 1);
    file.put(0);
    file.close();
}

RandomAccess RandomAccessBenchmarker::benchmark_write() {
    // Create or truncate file
    std::fstream file(file_path_, std::ios::binary | std::ios::in | std::ios::out | std::ios::trunc);
    if (!file) {
        throw std::runtime_error("Failed to open file for writing: " + file_path_);
    }
    
    // Create sparse file
    file.seekp(big_file_size_ - 1);
    file.put(0);
    
    auto start = std::chrono::steady_clock::now();
    size_t operations = 0;
    
    for (size_t i = 0; i < random_accesses_; ++i) {
        auto elapsed = std::chrono::duration<double>(
            std::chrono::steady_clock::now() - start).count();
        
        if (elapsed > time_limit_) {
            break;
        }
        
        file.seekp(positions_[i]);
        file.put(random_data_[i]);
        file.flush();
        
        operations++;
    }
    
    file.close();
    
    auto end = std::chrono::steady_clock::now();
    double elapsed = std::chrono::duration<double>(end - start).count();
    double iops = operations / elapsed;
    
    RandomAccess m;
    m.timestamp = std::chrono::system_clock::now();
    m.location = file_path_;
    m.name = name_;
    m.direction = IoDirection::WRITE;
    m.iops = iops;
    return m;
}

RandomAccess RandomAccessBenchmarker::benchmark_read() {
    // Ensure file exists
    create_file_for_reading();
    
    std::ifstream file(file_path_, std::ios::binary);
    if (!file) {
        throw std::runtime_error("Failed to open file for reading: " + file_path_);
    }
    
    auto start = std::chrono::steady_clock::now();
    size_t operations = 0;
    char byte;
    
    for (size_t i = 0; i < random_accesses_; ++i) {
        auto elapsed = std::chrono::duration<double>(
            std::chrono::steady_clock::now() - start).count();
        
        if (elapsed > time_limit_) {
            break;
        }
        
        file.seekg(positions_[i]);
        file.get(byte);
        
        operations++;
    }
    
    file.close();
    
    auto end = std::chrono::steady_clock::now();
    double elapsed = std::chrono::duration<double>(end - start).count();
    double iops = operations / elapsed;
    
    RandomAccess m;
    m.timestamp = std::chrono::system_clock::now();
    m.location = file_path_;
    m.name = name_;
    m.direction = IoDirection::READ;
    m.iops = iops;
    return m;
}

void RandomAccessBenchmarker::run(const std::string& output_file) {
    std::ofstream out(output_file, std::ios::app);
    if (!out) {
        throw std::runtime_error("Failed to open output file: " + output_file);
    }
    
    try {
        std::cout << "Random access write: " << format_with_apostrophes(random_accesses_) 
                 << " operations" << std::endl;
        auto write_result = benchmark_write();
        out << write_result.to_string() << std::endl;
        out.flush();
        
        std::cout << "Random access read: " << format_with_apostrophes(random_accesses_) 
                 << " operations" << std::endl;
        auto read_result = benchmark_read();
        out << read_result.to_string() << std::endl;
        out.flush();
    } catch (const std::exception& e) {
        std::cerr << "Error in random access benchmark: " << e.what() << std::endl;
    }
    
    out.close();
}

void RandomAccessBenchmarker::cleanup() {
    if (fs::exists(file_path_)) {
        fs::remove(file_path_);
    }
}
