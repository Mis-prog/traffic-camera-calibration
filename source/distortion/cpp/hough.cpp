#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <cmath>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

namespace py = pybind11;

py::array_t<float> hough_transform_with_orientation(
    py::array_t<uint8_t> edges,
    py::array_t<float> orientations,
    float angle_resolution_deg,
    float rho_resolution)
{
    auto buf_edges = edges.unchecked<2>();
    auto buf_orient = orientations.unchecked<2>();

    int height = buf_edges.shape(0);
    int width = buf_edges.shape(1);

    int diag_len = static_cast<int>(std::hypot(width, height));
    int num_thetas = static_cast<int>(180.0 / angle_resolution_deg);
    int num_rhos = 2 * diag_len;

    py::array_t<float> accumulator({num_rhos, num_thetas});
    auto acc = accumulator.mutable_unchecked<2>();

    double deg2rad = M_PI / 180.0;

    for (int y = 0; y < height; y++) {
        for (int x = 0; x < width; x++) {
            if (buf_edges(y, x)) {
                float theta = buf_orient(y, x);
                for (int t = 0; t < num_thetas; t++) {
                    double angle = t * angle_resolution_deg * deg2rad;
                    double rho = x * std::cos(angle) + y * std::sin(angle);
                    int r_idx = static_cast<int>((rho + diag_len) / rho_resolution);
                    if (r_idx >= 0 && r_idx < num_rhos)
                        acc(r_idx, t) += 1.0f;
                }
            }
        }
    }

    return accumulator;
}

PYBIND11_MODULE(mymodule, m) {
    m.def("hough_transform_with_orientation", &hough_transform_with_orientation,
          py::arg("edges"),
          py::arg("orientations"),
          py::arg("angle_resolution_deg") = 1.0f,
          py::arg("rho_resolution") = 1.0f,
          "Hough transform using edge image and orientation map");
}