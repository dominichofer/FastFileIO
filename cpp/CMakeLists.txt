cmake_minimum_required(VERSION 3.15)
project(FastFileIO VERSION 1.0 LANGUAGES CXX)

# Set C++ standard
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Add compile options
if(CMAKE_CXX_COMPILER_ID MATCHES "GNU|Clang")
    add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# Include directories
include_directories(include)

# Source files
set(SOURCES
    src/config.cpp
    src/large_files.cpp
    src/small_files.cpp
    src/random_access.cpp
    src/main.cpp
)

# Create executable
add_executable(fastfileio ${SOURCES})

# Installation
install(TARGETS fastfileio RUNTIME DESTINATION bin)
