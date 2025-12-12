#include "large_files.h"
#include <random>
#include <fstream>
#include <stdexcept>

LargeFileBenchmarker::LargeFileBenchmarker(
    std::string path,
    std::string name,
    const Config& config)
    : path(path),
      name(name),
      time_limit(std::chrono::seconds(config.time_limit)),
      file_size(config.large_file_size),
      block_size(config.block_size),
      file(std::filesystem::path(path) / "large_file.dat"),
      rnd_data(file_size, 0)
{}

size_t LargeFileBenchmarker::write_chunk(size_t start_pos, size_t end_pos, size_t block_size) {
    size_t bytes_written = 0;
    auto start = std::chrono::high_resolution_clock::now();
    
    std::ofstream file_stream(file, std::ios::binary);
    if (!file_stream) {
        throw std::runtime_error("Failed to create file");
    }
    
    file_stream.seekp(start_pos);
    
    for (size_t i = start_pos; i < end_pos; i += block_size) {
        file_stream.write(reinterpret_cast<const char*>(&rnd_data[i]), block_size);
        bytes_written += block_size;
        
        if (std::chrono::high_resolution_clock::now() - start > time_limit) {
            break;
        }
    }
    
    return bytes_written;
}

size_t LargeFileBenchmarker::read_chunk(size_t start_pos, size_t end_pos, size_t block_size) {
    size_t bytes_read = 0;
    auto start = std::chrono::high_resolution_clock::now();
    
    std::ifstream file_stream(file, std::ios::binary);
    if (!file_stream) {
        throw std::runtime_error("Failed to open file");
    }
    
    file_stream.seekg(start_pos);
    
    std::vector<uint8_t> buffer(block_size);
    for (size_t i = start_pos; i < end_pos; i += block_size) {
        file_stream.read(reinterpret_cast<char*>(buffer.data()), block_size);
        size_t read = file_stream.gcount();
        if (read == 0) {
            break;
        }
        bytes_read += read;
        
        if (std::chrono::high_resolution_clock::now() - start > time_limit) {
            break;
        }
    }
    
    return bytes_read;
}

void LargeFileBenchmarker::run(std::ostream& output) {
    std::mt19937 rng(std::random_device{}());
    std::uniform_int_distribution<> dis(0, 255);

    for (size_t bs : block_size) {
        // Prepare random data
        for (auto& byte : rnd_data) {
            byte = static_cast<uint8_t>(dis(rng));
        }

        // Write
        auto start = std::chrono::high_resolution_clock::now();
        size_t result = write_chunk(0, file_size, bs);
        double duration = std::chrono::duration<double>(std::chrono::high_resolution_clock::now() - start).count();
        double bandwidth = static_cast<double>(result) / duration;
        
        output << std::fixed << "large file bandwidth, write, " << name << ", " << path << ", " << bs << ", " << bandwidth << "\n";
        output.flush();

        // Read
        start = std::chrono::high_resolution_clock::now();
        result = read_chunk(0, file_size, bs);
        duration = std::chrono::duration<double>(std::chrono::high_resolution_clock::now() - start).count();
        bandwidth = static_cast<double>(result) / duration;
        
        output << std::fixed << "large file bandwidth, read, " << name << ", " << path << ", " << bs << ", " << bandwidth << "\n";
        output.flush();
    }

    // Cleanup
    try {
        std::filesystem::remove(file);
    } catch (const std::exception&) {
    }
}
