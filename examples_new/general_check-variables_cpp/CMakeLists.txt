cmake_minimum_required(VERSION 3.1)
project(general_check-variables)

add_executable(general_check-variables general_check-variables.cpp ../common/participant.cpp)
include_directories(../common)

target_link_libraries(general_check-variables)
set_property(TARGET general_check-variables PROPERTY CXX_STANDARD 14)
