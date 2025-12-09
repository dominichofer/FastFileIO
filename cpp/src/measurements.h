#pragma once
#include <string>
#include <chrono>
#include <memory>
#include <vector>

enum class IoDirection {
    READ,
    WRITE
};

std::string to_string(IoDirection);
IoDirection parse_direction(const std::string&);

struct Measurement {
    std::chrono::system_clock::time_point timestamp;
    std::string location;
    std::string name;
    IoDirection direction;

    virtual std::string to_string() const = 0;
    virtual std::string type_name() const = 0;
};

struct LargeFileBandwidth : public Measurement {
    size_t block_size;
    double bandwidth;

    std::string to_string() const override;
    std::string type_name() const override { return "LargeFileBandwidth"; }

    static LargeFileBandwidth parse(const std::string& line);
};

struct SmallFilesBandwidth : public Measurement {
    double bandwidth;

    std::string to_string() const override;
    std::string type_name() const override { return "SmallFilesBandwidth"; }

    static SmallFilesBandwidth parse(const std::string& line);
};

struct RandomAccess : public Measurement {
    double iops;

    std::string to_string() const override;
    std::string type_name() const override { return "RandomAccess"; }

    static RandomAccess parse(const std::string& line);
};
