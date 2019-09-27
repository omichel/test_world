cmake_minimum_required(VERSION 3.1)
project(reporter_skeleton)

add_executable(reporter_skeleton reporter_skeleton.cpp ../common/participant.cpp)
include_directories(../common)

target_link_libraries(reporter_skeleton)
set_property(TARGET reporter_skeleton PROPERTY CXX_STANDARD 14)