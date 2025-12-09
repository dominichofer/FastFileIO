#pragma once
#include <string>
#include <vector>
#include <chrono>

std::vector<std::string> split(const std::string&, char delimiter);

std::string to_string(const std::chrono::system_clock::time_point&);
std::chrono::system_clock::time_point parse_timestamp(const std::string&);

// Format number with apostrophes as thousands separator
std::string format_with_apostrophes(size_t number);
