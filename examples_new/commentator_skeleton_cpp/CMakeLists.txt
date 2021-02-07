cmake_minimum_required(VERSION 3.1)
project(commentator_skeleton)

add_executable(commentator_skeleton commentator_skeleton.cpp ../common/participant.cpp)
include_directories(../common)

target_link_libraries(commentator_skeleton)
set_property(TARGET commentator_skeleton PROPERTY CXX_STANDARD 14)
