cmake_minimum_required(VERSION 3.15)
project(distorsion)

set(CMAKE_CXX_STANDARD 17)


find_package(Python3 3.10 EXACT REQUIRED COMPONENTS Interpreter Development)

add_subdirectory(extern/pybind11)
add_library(mymodule MODULE  hough.cpp)
target_link_libraries(mymodule PRIVATE pybind11::module)

set_target_properties(mymodule PROPERTIES
    PREFIX ""        # Без префикса 'lib'
    SUFFIX ".pyd"    # Чтобы получить mymodule.pyd, а не .dll
)