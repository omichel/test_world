cmake_minimum_required(VERSION 3.1)
project(general_frame-skip)

find_package(Threads REQUIRED)

add_executable(general_frame-skip general_frame-skip.cpp ../common/participant.cpp)
include_directories(../common)

target_link_libraries(general_frame-skip Threads::Threads)
set_property(TARGET general_frame-skip PROPERTY CXX_STANDARD 14)
