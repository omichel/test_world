cmake_minimum_required(VERSION 3.1)
project(general_image-fetch)

find_package(OpenCV REQUIRED COMPONENTS core highgui)

add_executable(general_image-fetch general_image-fetch.cpp ../common/participant.cpp)
include_directories(
  ../common
  ../extlibs/cppcodec
  )

target_link_libraries(general_image-fetch
  ${OpenCV_LIBS}
  ${OpenCV_LIBRARIES}
  )
set_property(TARGET general_image-fetch PROPERTY CXX_STANDARD 14)
