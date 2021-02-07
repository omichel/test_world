cmake_minimum_required(VERSION 3.1)
project(player_skeleton)

add_executable(player_skeleton player_skeleton.cpp ../common/participant.cpp)
include_directories(../common)

target_link_libraries(player_skeleton)
set_property(TARGET player_skeleton PROPERTY CXX_STANDARD 14)
