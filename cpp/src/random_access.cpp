#include "random_access.h"
#include <random>
#include <fstream>
#include <stdexcept>

RandomAccessBenchmarker::RandomAccessBenchmarker(
    std::string path,
    std::string name,
    const Config& config)
    : path(path),
      name(name),
      time_limit(std::chrono::seconds(config.time_limit)),
      file_size(config.large_file_size),
      repetitions(config.random_accesses),
      file(std::filesystem::path(path) / "random_access_file.dat")
{}

size_t RandomAccessBenchmarker::bench_write() {
    std::mt19937 rng(std::random_device{}());
    std::uniform_int_distribution<size_t> dist(0, file_size - 1);
    std::vector<size_t> rnd_pos;
    for (size_t i = 0; i < repetitions; ++i) {
        rnd_pos.push_back(dist(rng));
    }
    
    auto start = std::chrono::high_resolution_clock::now();
    size_t writes = 0;
    
    std::ofstream file_stream(file, std::ios::binary | std::ios::app);
    if (!file_stream) {
        throw std::runtime_error("Failed to create file");
    }

    for (size_t i = 0; i < repetitions; ++i) {
        file_stream.seekp(rnd_pos[i]);
        file_stream.put('\0');
        writes++;

        if (std::chrono::high_resolution_clock::now() - start > time_limit) {
            break;
        }
    }
    return writes;
}

size_t RandomAccessBenchmarker::bench_read() {
    std::mt19937 rng(std::random_device{}());
    std::uniform_int_distribution<size_t> dist(0, file_size - 1);
    std::vector<size_t> rnd_pos;
    for (size_t i = 0; i < repetitions; ++i) {
        rnd_pos.push_back(dist(rng));
    }
    
    auto start = std::chrono::high_resolution_clock::now();
    size_t reads = 0;
    
    std::ifstream file_stream(file, std::ios::binary);
    if (!file_stream) {
        throw std::runtime_error("Failed to open file");
    }

    for (size_t i = 0; i < repetitions; ++i) {
        file_stream.seekg(rnd_pos[i]);
        file_stream.get();
        reads++;

        if (std::chrono::high_resolution_clock::now() - start > time_limit) {
            break;
        }
    }
    return reads;
}

void RandomAccessBenchmarker::run(std::ostream& output) {
    // Create file with random data
    std::ofstream file_stream(file, std::ios::binary);
    if (!file_stream) {
        throw std::runtime_error("Failed to create file");
    }
    std::mt19937 rng(std::random_device{}());
    std::uniform_int_distribution<size_t> dist(0, file_size - 1);
    std::vector<uint8_t> data(file_size);
    for (auto& byte : data)
        byte = static_cast<uint8_t>(dist(rng) % 256);
    file_stream.write(reinterpret_cast<const char*>(data.data()), file_size);
    file_stream.close();

    // Write
    auto start = std::chrono::high_resolution_clock::now();
    size_t result = bench_write();
    double duration = std::chrono::duration<double>(std::chrono::high_resolution_clock::now() - start).count();
    double iops = static_cast<double>(result) / duration;
    output << "random access IOPS, write, " << name << ", " << path << ", " << iops << std::endl;
    output.flush();

    // Read
    start = std::chrono::high_resolution_clock::now();
    result = bench_read();
    duration = std::chrono::duration<double>(std::chrono::high_resolution_clock::now() - start).count();
    iops = static_cast<double>(result) / duration;
    output << "random access IOPS, read, " << name << ", " << path << ", " << iops << std::endl;
    output.flush();

    // Cleanup
    try {
        std::filesystem::remove(file);
    } catch (const std::exception&) {
    }
}
