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
    
    Config config = Config::load(config_file);
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
