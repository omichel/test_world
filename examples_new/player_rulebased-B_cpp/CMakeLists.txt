cmake_minimum_required(VERSION 3.1)
project(player_rulebased-B)

add_executable(player_rulebased-B player_rulebased-B.cpp ../common/participant.cpp)
include_directories(../common)

target_link_libraries(player_rulebased-B)
set_property(TARGET player_rulebased-B PROPERTY CXX_STANDARD 14)