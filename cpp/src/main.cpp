#include "run.h"
#include <iostream>
#include <string>
#include <cstring>
#include <filesystem>

namespace fs = std::filesystem;

void print_usage(const char* program_name) {
    std::cout << "Usage: " << program_name << " [OPTIONS]\n"
              << "\n"
              << "Options:\n"
              << "  --location PATH      Directory where benchmark files will be created\n"
              << "  --name NAME          Friendly name for the location (e.g., 'scratch', 'home')\n"
              << "  --output FILE        Output log file (default: output.log)\n"
              << "  --config FILE        Optional configuration file\n"
              << "  --large-files        Run only large files benchmark\n"
              << "  --small-files        Run only small files benchmark\n"
              << "  --random-access      Run only random access benchmark\n"
              << "  --help               Show this help message\n"
              << "\n"
              << "If no specific benchmark is selected, all benchmarks will run.\n"
              << "\n"
              << "Example:\n"
              << "  " << program_name << " --location /scratch --name scratch --output scratch.log\n";
}

int main(int argc, char* argv[]) {
    std::string location;
    std::string name;
    std::string output_file = "output.log";
    std::string config_file;
    bool run_large = false;
    bool run_small = false;
    bool run_random = false;
    
    // Parse command line arguments
    for (int i = 1; i < argc; ++i) {
        std::string arg = argv[i];
        
        if (arg == "--help" || arg == "-h") {
            print_usage(argv[0]);
            return 0;
        } else if (arg == "--location" && i + 1 < argc) {
            location = argv[++i];
        } else if (arg == "--name" && i + 1 < argc) {
            name = argv[++i];
        } else if (arg == "--output" && i + 1 < argc) {
            output_file = argv[++i];
        } else if (arg == "--config" && i + 1 < argc) {
            config_file = argv[++i];
        } else if (arg == "--large-files") {
            run_large = true;
        } else if (arg == "--small-files") {
            run_small = true;
        } else if (arg == "--random-access") {
            run_random = true;
        } else {
            std::cerr << "Unknown option: " << arg << std::endl;
            print_usage(argv[0]);
            return 1;
        }
    }
    
    // Validate required arguments
    if (location.empty()) {
        std::cerr << "Error: --location is required\n" << std::endl;
        print_usage(argv[0]);
        return 1;
    }
    
    if (name.empty()) {
        std::cerr << "Error: --name is required\n" << std::endl;
        print_usage(argv[0]);
        return 1;
    }
    
    // Create location directory if it doesn't exist
    try {
        if (!fs::exists(location)) {
            fs::create_directories(location);
            std::cout << "Created directory: " << location << std::endl;
        }
    } catch (const std::exception& e) {
        std::cerr << "Error creating directory: " << e.what() << std::endl;
        return 1;
    }
    
    // Load configuration
    Config config;
    if (!config_file.empty()) {
        std::cout << "Loading configuration from:" << config_file << std::endl;
        config = Config::load(config_file);
    }
    
    // If no specific benchmark is selected, run all
    if (!run_large && !run_small && !run_random) {
        run_large = run_small = run_random = true;
    }
    
    try {
        std::cout << "FastFileIO C++ Benchmark\n"
                  << "========================\n"
                  << "Location: " << location << "\n"
                  << "Name: " << name << "\n"
                  << "Output: " << output_file << "\n"
                  << std::endl;
        
        if (run_large && run_small && run_random) {
            run_all(location, name, output_file, config);
        } else {
            if (run_large) {
                run_large_files(location, name, output_file, config);
            }
            if (run_small) {
                run_small_files(location, name, output_file, config);
            }
            if (run_random) {
                run_random_access(location, name, output_file, config);
            }
        }
        
        std::cout << "\nBenchmarks completed successfully!" << std::endl;
        std::cout << "Results written to: " << output_file << std::endl;
        
    } catch (const std::exception& e) {
        std::cerr << "Error: " << e.what() << std::endl;
        return 1;
    }
    
    return 0;
}
