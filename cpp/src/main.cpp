#include <iostream>
#include <fstream>
#include <vector>
#include <string>
#include <chrono>
#include <random>
#include <algorithm>
#include <filesystem>
#include <cstdint>

namespace fs = std::filesystem;

// Writes data to a file and returns the bandwidth in MiB/s.
double write_file(const std::string& file_path, const std::vector<char>& data) {
    auto start = std::chrono::high_resolution_clock::now();
    std::ofstream f(file_path, std::ios::binary);
    f.write(data.data(), data.size());
    f.close();
    auto end = std::chrono::high_resolution_clock::now();
    double duration = std::chrono::duration<double>(end - start).count();
    return static_cast<double>(data.size()) / duration / (1024 * 1024);
}

// Reads data from a file and returns the bandwidth in MiB/s.
double read_file(const std::string& file_path) {
    auto start = std::chrono::high_resolution_clock::now();
    std::ifstream f(file_path, std::ios::binary | std::ios::ate);
    std::streamsize size = f.tellg();
    f.seekg(0, std::ios::beg);
    std::vector<char> data(size);
    f.read(data.data(), size);
    f.close();
    auto end = std::chrono::high_resolution_clock::now();
    double duration = std::chrono::duration<double>(end - start).count();
    return static_cast<double>(size) / duration / (1024 * 1024);
}

// Writes random bytes to a file and returns the IOPS.
double write_random_bytes(const std::string& file_path, int64_t file_size, int operations, int time_limit) {
    std::random_device rd;
    std::mt19937_64 gen(rd());
    std::uniform_int_distribution<int64_t> dist(0, file_size - 1);
    
    std::vector<int64_t> rnd_pos(operations);
    for (int i = 0; i < operations; ++i) {
        rnd_pos[i] = dist(gen);
    }
    
    int64_t bytes_written = 0;
    auto start = std::chrono::high_resolution_clock::now();
    std::fstream f(file_path, std::ios::binary | std::ios::in | std::ios::out);
    char zero = '\0';
    for (int64_t pos : rnd_pos) {
        f.seekp(pos);
        f.write(&zero, 1);
        bytes_written += 1;
        auto now = std::chrono::high_resolution_clock::now();
        if (std::chrono::duration<double>(now - start).count() > time_limit) {
            break;
        }
    }
    f.close();
    auto end = std::chrono::high_resolution_clock::now();
    double duration = std::chrono::duration<double>(end - start).count();
    return static_cast<double>(bytes_written) / duration;
}

// Reads random bytes from a file and returns the IOPS.
double read_random_bytes(const std::string& file_path, int64_t file_size, int operations, int time_limit) {
    std::random_device rd;
    std::mt19937_64 gen(rd());
    std::uniform_int_distribution<int64_t> dist(0, file_size - 1);
    
    std::vector<int64_t> rnd_pos(operations);
    for (int i = 0; i < operations; ++i) {
        rnd_pos[i] = dist(gen);
    }
    
    int64_t bytes_read = 0;
    auto start = std::chrono::high_resolution_clock::now();
    std::ifstream f(file_path, std::ios::binary);
    char buffer;
    for (int64_t pos : rnd_pos) {
        f.seekg(pos);
        if (!f.read(&buffer, 1)) {
            break;
        }
        bytes_read += 1;
        auto now = std::chrono::high_resolution_clock::now();
        if (std::chrono::duration<double>(now - start).count() > time_limit) {
            break;
        }
    }
    f.close();
    auto end = std::chrono::high_resolution_clock::now();
    double duration = std::chrono::duration<double>(end - start).count();
    return static_cast<double>(bytes_read) / duration;
}

int main(int argc, char* argv[]) {
    if (argc < 2) {
        std::cerr << "Usage: " << argv[0] << " <path> <name> [repetitions]" << std::endl;
        return 1;
    }
    
    std::string path = argv[1];
    std::string name = argv[2];
    int repetitions = (argc >= 4) ? std::stoi(argv[3]) : 1;
    
    int time_limit = 10;  // seconds
    std::string large_file_path = (fs::path(path) / "large_file.dat").string();
    int64_t large_file_size = 10LL * (1LL << 30);  // 10 GiB
    
    std::vector<std::string> small_file_paths;
    for (int i = 0; i < 10'000; ++i) {
        small_file_paths.push_back((fs::path(path) / ("small_file_" + std::to_string(i) + ".dat")).string());
    }
    int64_t small_file_size = 1 * (1 << 10);  // 1 kiB
    
    // Generate random data
    std::random_device rd;
    std::ranlux24_base gen(rd());
    std::uniform_int_distribution<int> dist(0, 255);
    std::vector<char> rnd_data(large_file_size);
    for (int64_t i = 0; i < large_file_size; ++i) {
        rnd_data[i] = static_cast<char>(dist(gen));
    }
    std::vector<std::vector<char>> small_file_data;
    for (size_t i = 0; i < small_file_paths.size(); ++i) {
        std::vector<char> data(small_file_size);
        for (int64_t j = 0; j < small_file_size; ++j) {
            data[j] = static_cast<char>(dist(gen));
        }
        small_file_data.push_back(std::move(data));
    }
    
    for (int rep = 0; rep < repetitions; ++rep) {
        double bandwidth = write_file(large_file_path, rnd_data);
        std::cout << "large file bandwidth, write, " << name << ", " << path << ", " << bandwidth << std::endl;
        bandwidth = read_file(large_file_path);
        std::cout << "large file bandwidth, read, " << name << ", " << path << ", " << bandwidth << std::endl;
        
        int operations = 100000;
        double iops = write_random_bytes(large_file_path, large_file_size, operations, time_limit);
        std::cout << "random access IOPS, write, " << name << ", " << path << ", " << iops << std::endl;
        iops = read_random_bytes(large_file_path, large_file_size, operations, time_limit);
        std::cout << "random access IOPS, read, " << name << ", " << path << ", " << iops << std::endl;
        
        int64_t bytes_written = 0;
        auto start = std::chrono::high_resolution_clock::now();
        for (size_t i = 0; i < small_file_paths.size(); ++i) {
            std::ofstream f(small_file_paths[i], std::ios::binary);
            f.write(small_file_data[i].data(), small_file_data[i].size());
            bytes_written += small_file_size;
            f.close();
            auto now = std::chrono::high_resolution_clock::now();
            if (std::chrono::duration<double>(now - start).count() > time_limit) {
                break;
            }
        }
        auto end = std::chrono::high_resolution_clock::now();
        double duration = std::chrono::duration<double>(end - start).count();
        bandwidth = static_cast<double>(bytes_written) / duration / (1024 * 1024);
        std::cout << "small file bandwidth, write, " << name << ", " << path << ", " << bandwidth << std::endl;
        
        int64_t bytes_read = 0;
        start = std::chrono::high_resolution_clock::now();
        std::vector<std::vector<char>> data(small_file_paths.size());
        for (size_t i = 0; i < small_file_paths.size(); ++i) {
            data[i].resize(small_file_size);
        }
        for (size_t i = 0; i < small_file_paths.size(); ++i) {
            std::ifstream f(small_file_paths[i], std::ios::binary | std::ios::ate);
            if (!f) {
                break;
            }
            std::streamsize size = f.tellg();
            f.seekg(0, std::ios::beg);
            f.read(data[i].data(), size);
            bytes_read += size;
            f.close();
            auto now = std::chrono::high_resolution_clock::now();
            if (std::chrono::duration<double>(now - start).count() > time_limit) {
                break;
            }
        }
        end = std::chrono::high_resolution_clock::now();
        duration = std::chrono::duration<double>(end - start).count();
        bandwidth = static_cast<double>(bytes_read) / duration / (1024 * 1024);
        std::cout << "small file bandwidth, read, " << name << ", " << path << ", " << bandwidth << std::endl;
    }
    
    // Cleanup
    fs::remove(large_file_path);
    for (const auto& file_path : small_file_paths) {
        if (fs::exists(file_path)) {
            fs::remove(file_path);
        }
    }
    
    return 0;
}
