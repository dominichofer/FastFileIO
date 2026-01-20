cmake_minimum_required(VERSION 3.15)
project(FastFileIO VERSION 1.0 LANGUAGES CXX)

# Set C++ standard
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Add compile options
if(CMAKE_CXX_COMPILER_ID MATCHES "GNU|Clang")
	set(CMAKE_CXX_FLAGS "-march=native -w")
	set(CMAKE_CXX_FLAGS_DEBUG "-g")
	set(CMAKE_CXX_FLAGS_RELEASE "-O3 -DNDEBUG")
elseif(MSVC)
	set(CMAKE_CXX_FLAGS "/std:c++latest /EHsc /MP")
	set(CMAKE_CXX_FLAGS_DEBUG "/Od /MDd")
	set(CMAKE_CXX_FLAGS_RELEASE "/Ox /MD /GL")
endif()

set(SOURCES
	src/main.cpp
)

add_executable(fastfileio ${SOURCES})
install(TARGETS fastfileio RUNTIME DESTINATION bin)
