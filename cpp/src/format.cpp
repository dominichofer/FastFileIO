#include "format.h"
#include <algorithm>
#include <chrono>
#include <sstream>
#include <iomanip>
#include <ctime>


std::vector<std::string> split(const std::string& s, char delimiter) {
    std::vector<std::string> tokens;
    std::string token;
    std::istringstream tokenStream(s);
    while (std::getline(tokenStream, token, delimiter)) {
        tokens.push_back(token);
    }
    return tokens;
}

std::string to_string(const std::chrono::system_clock::time_point& tp) {
    auto time_t = std::chrono::system_clock::to_time_t(tp);
    auto ms = std::chrono::duration_cast<std::chrono::milliseconds>(
        tp.time_since_epoch()) % 1000;
    
    std::tm tm;
    gmtime_r(&time_t, &tm);
    
    std::ostringstream oss;
    oss << std::put_time(&tm, "%Y-%m-%dT%H:%M:%S");
    oss << '.' << std::setfill('0') << std::setw(3) << ms.count() << 'Z';
    return oss.str();
}

std::chrono::system_clock::time_point parse_timestamp(const std::string& s) {
    std::tm tm = {};
    std::istringstream ss(s);
    ss >> std::get_time(&tm, "%Y-%m-%dT%H:%M:%S");
    
    if (ss.fail()) {
        throw std::runtime_error("Failed to parse timestamp: " + s);
    }
    
    auto time_t = timegm(&tm);
    auto tp = std::chrono::system_clock::from_time_t(time_t);
    
    // Parse milliseconds if present
    if (ss.peek() == '.') {
        ss.ignore(); // skip '.'
        int ms;
        ss >> ms;
        tp += std::chrono::milliseconds(ms);
    }
    
    return tp;
}

std::string format_with_apostrophes(size_t number) {
    std::string num_str = std::to_string(number);
    std::string result;
    int count = 0;
    
    for (auto it = num_str.rbegin(); it != num_str.rend(); ++it) {
        if (count == 3) {
            result += '\'';
            count = 0;
        }
        result += *it;
        count++;
    }
    
    std::reverse(result.begin(), result.end());
    return result;
}
