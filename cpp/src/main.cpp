#include "config.h"
#include "large_files.h"
#include "small_files.h"
#include "random_access.h"
#include <iostream>
#include <fstream>
#include <vector>
#include <string>

int main(int argc, char* argv[]) {
    if (argc < 5) {
        std::cout << "Usage: <path> <name> <config_file> <output_file> [repetitions]" << std::endl;
        return 1;
    }

    std::string path = argv[1];
    std::string name = argv[2];
    std::string config_file = argv[3];
    std::string output_file = argv[4];
    int repetitions = (argc > 5) ? std::stoi(argv[5]) : 1;

    // Resolve path to absolute
    path = std::filesystem::absolute(path).string();
    config_file = std::filesystem::absolute(config_file).string();
    output_file = std::filesystem::absolute(output_file).string();
    
    Config config = Config::load(config_file);
    std::cout << "Running with:" << std::endl;
    std::cout << "  Path: " << path << std::endl;
    std::cout << "  Name: " << name << std::endl;
    std::cout << "  Config file: " << config_file << std::endl;
    std::cout << "  Output file: " << output_file << std::endl;
    std::cout << "  Repetitions: " << repetitions << std::endl;
    std::cout << "  Time limit: " << config.time_limit << " seconds" << std::endl;
    std::cout << "  Random accesses: " << config.random_accesses << std::endl;
    std::cout << "  Small file count: " << config.small_file_count << std::endl;
    std::cout << "  Small file size: " << config.small_file_size << " bytes" << std::endl;
    std::cout << "  Large file size: " << config.large_file_size << " bytes" << std::endl;
    std::cout << "  Block sizes: ";
    for (const auto& bs : config.block_size) {
        std::cout << bs << " ";
    }
    std::cout << std::endl;

    LargeFileBenchmarker large_bm(path, name, config);
    SmallFilesBenchmarker small_bm(path, name, config);
    RandomAccessBenchmarker random_bm(path, name, config);

    std::ofstream output(output_file, std::ios::app);
    if (!output.is_open()) {
        std::cerr << "Failed to open output file" << std::endl;
        return 1;
    }

    for (int i = 0; i < repetitions; ++i) {
        large_bm.run(output);
        small_bm.run(output);
        random_bm.run(output);
    }
    return 0;
}
