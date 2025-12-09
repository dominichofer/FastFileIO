cmake_minimum_required(VERSION 3.15)
project(FastFileIO VERSION 1.0 LANGUAGES CXX)

# Set C++ standard
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# Add compile options
if(CMAKE_CXX_COMPILER_ID MATCHES "GNU|Clang")
    add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# Include directories
include_directories(include)

# Source files
set(SOURCES
    src/measurements.cpp
    src/format.cpp
    src/large_files.cpp
    src/small_files.cpp
    src/random_access.cpp
    src/run.cpp
)

# Create library
add_library(fastfileio_lib STATIC ${SOURCES})
target_include_directories(fastfileio_lib PUBLIC 
    $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
    $<INSTALL_INTERFACE:include>
)

# Link with filesystem library if needed (GCC < 9)
if(CMAKE_CXX_COMPILER_ID STREQUAL "GNU" AND CMAKE_CXX_COMPILER_VERSION VERSION_LESS 9.0)
    target_link_libraries(fastfileio_lib PUBLIC stdc++fs)
endif()

# Create executable
add_executable(fastfileio src/main.cpp)
target_link_libraries(fastfileio PRIVATE fastfileio_lib)

# Installation
install(TARGETS fastfileio
    RUNTIME DESTINATION bin
)

install(TARGETS fastfileio_lib
    ARCHIVE DESTINATION lib
    LIBRARY DESTINATION lib
)

install(DIRECTORY include/fastfileio
    DESTINATION include
)

# Print configuration
message(STATUS "FastFileIO Configuration:")
message(STATUS "  C++ Standard: ${CMAKE_CXX_STANDARD}")
message(STATUS "  Compiler: ${CMAKE_CXX_COMPILER_ID} ${CMAKE_CXX_COMPILER_VERSION}")
message(STATUS "  Build Type: ${CMAKE_BUILD_TYPE}")
