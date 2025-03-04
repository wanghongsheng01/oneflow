"""
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
"""
import unittest
from collections import OrderedDict

import numpy as np

import oneflow.experimental as flow
from test_util import GenArgList, type_name_to_flow_type


def _test_sort(test_case, data_shape, axis, descending, data_type, device):
    input = flow.Tensor(
        np.random.randn(*data_shape),
        dtype=type_name_to_flow_type[data_type],
        device=flow.device(device),
    )
    (of_values, of_indices) = flow.sort(input, dim=axis, descending=descending)
    np_input = -input.numpy() if descending else input.numpy()
    np_indices = np.argsort(np_input, axis=axis)
    np_out = np.sort(np_input, axis=axis)
    np_values = -np_out if descending else np_out
    test_case.assertTrue(
        np.array_equal(of_values.numpy().flatten(), np_values.flatten())
    )
    test_case.assertTrue(
        np.array_equal(of_indices.numpy().flatten(), np_indices.flatten())
    )


def _test_tensor_sort(test_case, data_shape, axis, descending, data_type, device):
    input = flow.Tensor(
        np.random.randn(*data_shape),
        dtype=type_name_to_flow_type[data_type],
        device=flow.device(device),
    )
    (of_values, of_indices) = input.sort(dim=axis, descending=descending)
    np_input = -input.numpy() if descending else input.numpy()
    np_indices = np.argsort(np_input, axis=axis)
    np_out = np.sort(np_input, axis=axis)
    np_values = -np_out if descending else np_out
    test_case.assertTrue(
        np.array_equal(of_values.numpy().flatten(), np_values.flatten())
    )
    test_case.assertTrue(
        np.array_equal(of_indices.numpy().flatten(), np_indices.flatten())
    )


@unittest.skipIf(
    not flow.unittest.env.eager_execution_enabled(),
    ".numpy() doesn't work in lazy mode",
)
class TestSort(flow.unittest.TestCase):
    def test_sort(test_case):
        arg_dict = OrderedDict()
        arg_dict["test_fun"] = [_test_sort, _test_tensor_sort]
        arg_dict["data_shape"] = [(2, 6, 5, 4), (3, 4, 8)]
        arg_dict["axis"] = [-1, 0, 2]
        arg_dict["descending"] = [True, False]
        arg_dict["data_type"] = ["double", "float32", "int32"]
        arg_dict["device"] = ["cpu", "cuda"]
        for arg in GenArgList(arg_dict):
            arg[0](test_case, *arg[1:])


if __name__ == "__main__":
    unittest.main()
