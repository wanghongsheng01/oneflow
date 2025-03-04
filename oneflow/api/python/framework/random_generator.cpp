/*
Copyright 2020 The OneFlow Authors. All rights reserved.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
*/
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "oneflow/api/python/of_api_registry.h"
#include "oneflow/core/framework/random_generator.h"

namespace py = pybind11;

namespace oneflow {

ONEFLOW_API_PYBIND11_MODULE("", m) {
  py::class_<one::Generator, std::shared_ptr<one::Generator>>(m, "Generator")
      .def("manual_seed", &one::Generator::set_current_seed)
      .def("initial_seed", &one::Generator::current_seed);

  m.def("manual_seed", [](uint64_t seed) { return one::ManualSeed(seed); });
  m.def("create_generator",
        [](const std::string& device) { return one::Generator::New(device).GetPtrOrThrow(); });
  m.def("create_generator", [](const std::string& device, uint64_t seed) {
    return one::Generator::New(device, seed).GetPtrOrThrow();
  });
}

}  // namespace oneflow
