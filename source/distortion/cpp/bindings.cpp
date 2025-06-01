#include <pybind11/pybind11.h>
#include "hough.hpp"

namespace py = pybind11;

PYBIND11_MODULE(mymodule, m) {
    py::class_<MyMath>(m, "MyMath")
        .def(py::init<>())
        .def("add", &MyMath::add)
        .def("mul", &MyMath::mul);
}
