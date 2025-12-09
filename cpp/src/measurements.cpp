#include "measurements.h"
#include "format.h"
#include <sstream>
#include <iomanip>
#include <ctime>

std::string to_string(IoDirection dir) {
    switch (dir) {
        case IoDirection::READ: return "read";
        case IoDirection::WRITE: return "write";
    }
    return "UNKNOWN";
}

IoDirection parse_direction(const std::string& s) {
    if (s == "read") return IoDirection::READ;
    if (s == "write") return IoDirection::WRITE;
    throw std::runtime_error("Invalid direction: " + s);
}

std::string Measurement::to_string() const {
    std::ostringstream oss;
    oss << to_string(timestamp) << ","
        << location << ","
        << name << ","
        << ::to_string(direction);
    return oss.str();
}

std::string LargeFileBandwidth::to_string() const {
    std::ostringstream oss;
    oss << Measurement::to_string() << ","
        << block_size << ","
        << std::fixed << std::setprecision(2) << bandwidth;
    return oss.str();
}

LargeFileBandwidth LargeFileBandwidth::parse(const std::string& line) {
    auto parts = split(line, ',');
    if (parts.size() != 6) {
        throw std::runtime_error("Invalid LargeFileBandwidth format: expected 6 fields, got " + std::to_string(parts.size()));
    }
    
    auto timestamp = parse_timestamp(parts[0]);
    auto direction = parse_direction(parts[3]);
    size_t block_size = std::stoull(parts[4]);
    double bandwidth = std::stod(parts[5]);
    
    LargeFileBandwidth m;
    m.timestamp = timestamp;
    m.location = parts[1];
    m.name = parts[2];
    m.direction = direction;
    m.block_size = block_size;
    m.bandwidth = bandwidth;
    return m;
}

std::string SmallFilesBandwidth::to_string() const {
    std::ostringstream oss;
    oss << Measurement::to_string() << ","
        << std::fixed << std::setprecision(2) << bandwidth;
    return oss.str();
}

SmallFilesBandwidth SmallFilesBandwidth::parse(const std::string& line) {
    auto parts = split(line, ',');
    if (parts.size() != 5) {
        throw std::runtime_error("Invalid SmallFilesBandwidth format: expected 5 fields, got " + std::to_string(parts.size()));
    }
    
    auto timestamp = parse_timestamp(parts[0]);
    auto direction = parse_direction(parts[3]);
    double bandwidth = std::stod(parts[4]);
    
    SmallFilesBandwidth m;
    m.timestamp = timestamp;
    m.location = parts[1];
    m.name = parts[2];
    m.direction = direction;
    m.bandwidth = bandwidth;
    return m;
}

std::string RandomAccess::to_string() const {
    std::ostringstream oss;
    oss << Measurement::to_string() << ","
        << std::fixed << std::setprecision(2) << iops;
    return oss.str();
}

RandomAccess RandomAccess::parse(const std::string& line) {
    auto parts = split(line, ',');
    if (parts.size() != 5) {
        throw std::runtime_error("Invalid RandomAccess format: expected 5 fields, got " + std::to_string(parts.size()));
    }
    
    auto timestamp = parse_timestamp(parts[0]);
    auto direction = parse_direction(parts[3]);
    double iops = std::stod(parts[4]);
    
    RandomAccess m;
    m.timestamp = timestamp;
    m.location = parts[1];
    m.name = parts[2];
    m.direction = direction;
    m.iops = iops;
    return m;
}
