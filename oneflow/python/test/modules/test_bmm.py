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
from collections import OrderedDict

import unittest
import numpy as np

import oneflow.experimental as flow
from test_util import GenArgList


def _test_bmm(test_case, device):
    input1 = flow.Tensor(
        np.random.randn(10, 3, 4), dtype=flow.float32, device=flow.device(device)
    )
    input2 = flow.Tensor(
        np.random.randn(10, 4, 5), dtype=flow.float32, device=flow.device(device)
    )
    of_out = flow.bmm(input1, input2)
    np_out = np.matmul(input1.numpy(), input2.numpy())
    test_case.assertTrue(np.allclose(of_out.numpy(), np_out, 1e-5, 1e-5))


def _test_bmm_backward(test_case, device):
    input1 = flow.Tensor(
        [
            [
                [-0.0036776792258024216, 1.9946473836898804, -0.423959881067276],
                [1.0892143249511719, 0.04005361348390579, -0.27883127331733704],
            ],
            [
                [-0.970306396484375, 0.017771577462553978, 0.019596196711063385],
                [0.27402883768081665, -0.8192587494850159, -0.3135920464992523],
            ],
        ],
        dtype=flow.float32,
        device=flow.device(device),
        requires_grad=True,
    )
    input2 = flow.Tensor(
        [
            [
                [1.118346929550171, -0.930071234703064],
                [1.1238232851028442, 1.373764157295227],
                [0.17178462445735931, -1.1010534763336182],
            ],
            [
                [0.6694859862327576, 0.9250285029411316],
                [-1.0835869312286377, 0.4192655086517334],
                [1.2616937160491943, 0.33809131383895874],
            ],
        ],
        dtype=flow.float32,
        device=flow.device(device),
        requires_grad=True,
    )
    of_out = flow.bmm(input1, input2)
    of_out = of_out.sum()
    of_out.backward()
    np_grad = [
        [
            [0.18827569484710693, 2.4975874423980713, -0.9292688369750977],
            [0.18827569484710693, 2.4975874423980713, -0.9292688369750977],
        ],
        [
            [1.5945144891738892, -0.6643214225769043, 1.5997850894927979],
            [1.5945144891738892, -0.6643214225769043, 1.5997850894927979],
        ],
    ]
    test_case.assertTrue(
        np.allclose(input1.grad.numpy(), np_grad, atol=1e-05, rtol=1e-05)
    )


@unittest.skipIf(
    not flow.unittest.env.eager_execution_enabled(),
    ".numpy() doesn't work in lazy mode",
)
class TestModule(flow.unittest.TestCase):
    def test_bmm(test_case):
        arg_dict = OrderedDict()
        arg_dict["test_fun"] = [
            _test_bmm,
            _test_bmm_backward,
        ]
        arg_dict["device"] = ["cpu", "cuda"]
        for arg in GenArgList(arg_dict):
            arg[0](test_case, *arg[1:])


if __name__ == "__main__":
    unittest.main()
