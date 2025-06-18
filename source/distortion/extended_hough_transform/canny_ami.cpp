#include "ami/ami_image/image.h"
#include "ami/ami_filters/filters.h"
#include "ami/ami_primitives/subpixel_image_contours.h"
#include "ami/ami_primitives/line_extraction.h"
#include "ami/ami_primitives/image_primitives.h"
#include "ami/ami_lens_distortion/lens_distortion_procedures.h"
#include "ami/ami_utilities/utilities.h"
#include <iostream>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

namespace py = pybind11;
using namespace std;


std::vector<std::tuple<float, float, float, float>> run_canny(const std::string& path,
                                               float low_thresh = 0.7,
                                               float high_thresh = 1.0) {
    ami::image<unsigned char> input(path);
    int width = input.width(), height = input.height();
    int size_ = width * height;

    ami::image<unsigned char> gray(width, height, 1, 0);
    ami::image<unsigned char> edges(width, height, 1, 0);

    for (int i = 0; i < size_; i++) {
        gray[i] = 0.3f * input[i] +
                  0.59f * input[i + size_] +
                  0.11f * input[i + size_ * 2];
    }

    ami::subpixel_image_contours contours = canny(gray, edges, low_thresh, high_thresh);

    const float* x = contours.get_x();
    const float* y = contours.get_y();
    const bool* c = contours.get_c();
    const float* coseno = contours.get_coseno();
    const float* seno = contours.get_seno();
    int N = contours.get_width() * contours.get_height();

    std::vector<std::tuple<float, float, float, float>> result;
    for (int i = 0; i < N; ++i) {
        if (c[i]) {
            result.emplace_back(x[i], y[i], coseno[i], seno[i]);
        }
    }

    return result;
}

PYBIND11_MODULE(canny, m) {
    m.doc() = "Canny edge detection module";

    m.def("hello", []() { return "Hello from C++"; });

    m.def("run_canny", &run_canny, "Run Canny edge detector",
          py::arg("path"), py::arg("low_thresh") = 0.7, py::arg("high_thresh") = 1.0);
}
