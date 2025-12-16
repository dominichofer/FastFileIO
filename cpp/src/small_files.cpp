#include "small_files.h"
#include <random>
#include <fstream>
#include <stdexcept>

SmallFilesBenchmarker::SmallFilesBenchmarker(
    std::string path,
    std::string name,
    const Config& config)
    : path(path),
      name(name),
      time_limit(std::chrono::seconds(config.time_limit)),
      file_size(config.small_file_size)
{
    for (size_t i = 0; i < config.small_file_count; ++i) {
        files.push_back(std::filesystem::path(path) / ("small_file_" + std::to_string(i) + ".dat"));
        rnd_data.push_back(std::vector<uint8_t>(file_size));
    }
}

size_t SmallFilesBenchmarker::write_files() {
    size_t bytes_written = 0;
    auto start = std::chrono::high_resolution_clock::now();
    for (size_t i = 0; i < files.size(); ++i) {
        std::ofstream file(files[i], std::ios::binary);
        if (!file) {
            throw std::runtime_error("Failed to open file for writing: " + files[i].string());
        }
        file.write(reinterpret_cast<const char*>(rnd_data[i].data()), file_size);
        bytes_written += file_size;
        file.close();

        if (std::chrono::high_resolution_clock::now() - start > time_limit) {
            break;
        }
    }
    return bytes_written;
}

size_t SmallFilesBenchmarker::read_files() {
    size_t bytes_read = 0;
    auto start = std::chrono::high_resolution_clock::now();
    for (size_t i = 0; i < files.size(); ++i) {
        std::ifstream file(files[i], std::ios::binary);
        if (!file) {
            continue;
        }
        file.read(reinterpret_cast<char*>(rnd_data[i].data()), file_size);
        bytes_read += file_size;
        file.close();

        if (std::chrono::high_resolution_clock::now() - start > time_limit) {
            break;
        }
    }
    return bytes_read;
}

void SmallFilesBenchmarker::run(std::ostream& output) {
    // Prepare random data
    std::mt19937 rng(std::random_device{}());
    std::uniform_int_distribution<int> dist(0, 255);
    for (auto& data : rnd_data) {
        for (auto& byte : data) {
            byte = static_cast<uint8_t>(dist(rng));
        }
    }

    // Write
    auto start = std::chrono::high_resolution_clock::now();
    size_t result = write_files();
    double duration = std::chrono::duration<double>(std::chrono::high_resolution_clock::now() - start).count();
    double bandwidth = static_cast<double>(result) / duration;

    output << "small files bandwidth, write, " << name << ", " << path << ", " << bandwidth << "\n";
    output.flush();

    // Read
    start = std::chrono::high_resolution_clock::now();
    result = read_files();
    duration = std::chrono::duration<double>(std::chrono::high_resolution_clock::now() - start).count();
    bandwidth = static_cast<double>(result) / duration;

    output << "small files bandwidth, read, " << name << ", " << path << ", " << bandwidth << "\n";

    // Cleanup
    for (const auto& file : files)
    {
        try {
            std::filesystem::remove(file);
        } catch (const std::exception&) {
        }
    }
}
