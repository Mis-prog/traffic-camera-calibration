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
#include <pybind11/numpy.h>

namespace py = pybind11;
using namespace std;


std::vector<std::tuple<float, float, float, float> > run_canny(const std::string &path,
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

    const float *x = contours.get_x();
    const float *y = contours.get_y();
    const bool *c = contours.get_c();
    const float *coseno = contours.get_coseno();
    const float *seno = contours.get_seno();
    int N = contours.get_width() * contours.get_height();

    std::vector<std::tuple<float, float, float, float> > result;
    for (int i = 0; i < N; ++i) {
        if (c[i]) {
            result.emplace_back(x[i], y[i], coseno[i], seno[i]);
        }
    }

    return result;
}


py::dict run_hough_py(
    const std::vector<float>& xs,
    const std::vector<float>& ys,
    const std::vector<float>& dxs,
    const std::vector<float>& dys,
    int width,
    int height,
    float distance_point_line_max,
    int max_lines = 30,
    float angle_resolution = 0.1f,
    float distance_resolution = 1.0f,
    float initial_distortion_param = -0.1f,
    float final_distortion_param = 0.1f,
    float distortion_param_resolution = 0.01f,
    float angle_point_orientation_max_diff = 15.0f
) {
    if (xs.size() != ys.size() || xs.size() != dxs.size() || xs.size() != dys.size()) {
        throw std::runtime_error("All input vectors must be the same size.");
    }

    subpixel_image_contours contours(width, height);

    int total = width * height;
    for (int i = 0; i < total; ++i) {
        contours.get_c()[i] = false;
        contours.get_x()[i] = 0.0f;
        contours.get_y()[i] = 0.0f;
        contours.get_coseno()[i] = 0.0f;
        contours.get_seno()[i] = 0.0f;
    }

    for (size_t i = 0; i < xs.size(); ++i) {
        int xi = static_cast<int>(xs[i]);
        int yi = static_cast<int>(ys[i]);
        if (xi < 0 || xi >= width || yi < 0 || yi >= height) continue;

        int idx = yi * width + xi;
        contours.get_x()[idx] = xs[i];
        contours.get_y()[idx] = ys[i];
        contours.get_coseno()[idx] = dxs[i];
        contours.get_seno()[idx] = dys[i];
        contours.get_c()[idx] = true;
    }

    lens_distortion_model ldm;
    ldm.set_distortion_center({width / 2.0, height / 2.0});
    ldm.get_d() = {1.0, 0.0};

    image_primitives primitives;

    double score;
    double best_param;
    std::vector<float> flat_acc;
    int acc_w, acc_h;

    std::tie(score, best_param, flat_acc, acc_w, acc_h) =
        line_equation_distortion_extraction_improved_hough_quotient(
            contours,
            primitives,
            distance_point_line_max,
            max_lines,
            angle_resolution,
            distance_resolution,
            initial_distortion_param,
            final_distortion_param,
            distortion_param_resolution,
            angle_point_orientation_max_diff,
            true,
            ldm
        );

    py::array_t<float> accumulator({acc_w, acc_h});
    auto buf = accumulator.mutable_unchecked<2>();
    for (int j = 0; j < acc_w; ++j)
        for (int i = 0; i < acc_h; ++i)
            buf(j, i) = flat_acc[j * acc_h + i];

    py::list lines;
    for (const auto& line : primitives.get_lines()) {
        py::dict l;
        l["a"] = line.get_a();
        l["b"] = line.get_b();
        l["c"] = line.get_c();
        py::list pts;
        for (const auto& p : line.get_points()) {
            pts.append(py::make_tuple(p.x, p.y));
        }
        l["points"] = pts;
        lines.append(l);
    }

    py::dict out;
    out["score"] = score;
    out["best_param"] = best_param;
    out["accumulator"] = accumulator;
    out["lines"] = lines;
    return out;
}


PYBIND11_MODULE(ami, m) {
    m.doc() = "Canny edge detection module";

    m.def("hello", []() { return "Hello from C++"; });

    m.def("run_canny", &run_canny, "Run Canny edge detector",
          py::arg("path"), py::arg("low_thresh") = 0.7, py::arg("high_thresh") = 1.0);


    m.def("run_hough", &run_hough_py,
          py::arg("xs"),
          py::arg("ys"),
          py::arg("dxs"),
          py::arg("dys"),
          py::arg("width"),
          py::arg("height"),
          py::arg("distance_point_line_max") = 3.0f,
          py::arg("max_lines") = 30,
          py::arg("angle_resolution") = 0.1f,
          py::arg("distance_resolution") = 1.0f,
          py::arg("initial_distortion_param") = 0.0f,
          py::arg("final_distortion_param") = 2.0f,
          py::arg("distortion_param_resolution") = 0.1f,
          py::arg("angle_point_orientation_max_diff") = 2.0f
    );
}
