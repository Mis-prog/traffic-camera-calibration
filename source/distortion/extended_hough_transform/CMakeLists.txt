cmake_minimum_required(VERSION 3.15)


set(Python3_ROOT_DIR "C:/Users/akmur/AppData/Local/Programs/Python/Python310")
set(Python_EXECUTABLE "${Python3_ROOT_DIR}/python.exe")

find_package(Python3 REQUIRED COMPONENTS Interpreter Development)


add_subdirectory(pybind11)

set(SOURCES
        ami/ami_primitives/subpixel_image_contours.cpp
        ami/ami_lens_distortion/lens_distortion_procedures.cpp
        ami/ami_primitives/line_extraction.cpp
        ami/ami_lens_distortion/lens_distortion_model.cpp
        ami/ami_primitives/line_points.cpp
        ami/ami_image/io_png/io_png.cpp
        ami/ami_lens_distortion/lens_distortion.cpp
        ami/ami_pol/ami_pol.cpp
        ami/ami_utilities/utilities.cpp
)

find_package(PNG REQUIRED)
include_directories(${PNG_INCLUDE_DIRS})
set(EXTRA_LIBS ${EXTRA_LIBS} ${PNG_LIBRARIES})

add_library(canny MODULE canny_ami.cpp ${SOURCES})
target_include_directories(canny PRIVATE ${Python3_INCLUDE_DIRS})
target_link_libraries(canny
        PRIVATE
        pybind11::module
        ${EXTRA_LIBS}
)

set_target_properties(canny PROPERTIES
        PREFIX ""        # Без префикса 'lib'
        SUFFIX ".pyd"    # Чтобы получить mymodule.pyd, а не .dll
)