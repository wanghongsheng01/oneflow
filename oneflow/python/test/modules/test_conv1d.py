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
import oneflow.experimental.nn as nn
from test_util import GenArgList


def _test_conv1d_bias_false(test_case, device):
    np_arr = np.array(
        [[[1.28795946, -0.29217920, 0.20338029, 0.78604293, -1.89607573]]]
    )
    input = flow.Tensor(
        np_arr, dtype=flow.float32, device=flow.device(device), requires_grad=True
    )
    weight = np.array(
        [
            [[0.10197904, 0.33723050, -0.25743008]],
            [[0.27720425, -0.52435774, -0.38381988]],
            [[0.56016803, -0.10063095, -0.10760903]],
        ]
    )
    m = nn.Conv1d(1, 3, 3, stride=1, bias=False)
    m.weight = flow.nn.Parameter(flow.Tensor(weight))
    m = m.to(device)
    output = m(input)
    np_out = np.array(
        [
            [
                [-0.01954307, -0.16356121, 0.77392507],
                [0.43217283, -0.48933625, 0.37196174],
                [0.72899038, -0.26872110, 0.23886177],
            ]
        ]
    )
    test_case.assertTrue(np.allclose(output.numpy(), np_out, 1e-6, 1e-6))
    output = output.sum()
    output.backward()
    np_grad = np.array(
        [[[0.93935132, 0.65159315, -0.09726584, -1.03661716, -0.74885899]]]
    )
    test_case.assertTrue(np.allclose(input.grad.numpy(), np_grad, 1e-6, 1e-6))


def _test_conv1d_bias_true(test_case, device):
    np_arr = np.array(
        [
            [
                [0.90499806, -1.11683071, 0.71605605, -0.56754625, 0.61944169],
                [-0.31317389, -0.26271924, 0.95579433, 0.52468461, 1.48926127],
            ]
        ]
    )
    input = flow.Tensor(
        np_arr, dtype=flow.float32, device=flow.device(device), requires_grad=True
    )
    weight = np.array(
        [
            [
                [0.01997352, 0.23834395, 0.00526353],
                [-0.04861857, -0.22751901, -0.06725175],
            ],
            [
                [0.13344523, -0.35202524, 0.15168799],
                [-0.25714493, -0.17459838, 0.28768948],
            ],
            [
                [0.10671382, -0.28205597, -0.39752254],
                [0.36393702, 0.07843742, -0.33898622],
            ],
            [
                [0.20485674, 0.04222689, -0.18986180],
                [0.22519711, -0.15910202, -0.35057363],
            ],
        ]
    )
    bias = np.array([0.01012857, 0.38912651, -0.01600273, -0.38833040])
    m = nn.Conv1d(2, 4, 3, stride=1, bias=True)
    m.weight = flow.nn.Parameter(flow.Tensor(weight))
    m.bias = flow.nn.Parameter(flow.Tensor(bias))
    m = m.to(device)
    np_out = np.array(
        [
            [
                [-0.22349545, -0.08447243, -0.37358052],
                [1.41303730, -0.04644597, 0.86949122],
                [-0.34765026, -0.31004351, -0.14158708],
                [-0.74985039, -0.87430149, -0.77354753],
            ]
        ]
    )
    output = m(input)
    test_case.assertTrue(np.allclose(output.numpy(), np_out, 1e-6, 1e-6))
    output = output.sum()
    output.backward()
    np_grad = np.array(
        [
            [
                [0.46498930, 0.11147892, -0.31895390, -0.78394318, -0.43043283],
                [0.28337064, -0.19941133, -0.66853344, -0.95190406, -0.46912211],
            ]
        ]
    )
    test_case.assertTrue(np.allclose(input.grad.numpy(), np_grad, 1e-6, 1e-6))


def _test_conv1d_dilation(test_case, device):
    np_arr = np.array(
        [[[-0.43016902, 1.74619496, -0.57338119, 0.25563857, 0.12575546]]]
    )
    input = flow.Tensor(
        np_arr, dtype=flow.float32, device=flow.device(device), requires_grad=True
    )
    weight = np.array(
        [
            [[-0.35057205, -0.31304273, 0.46250814]],
            [[-0.40786612, 0.36518192, 0.46280444]],
            [[-0.00921835, -0.38710043, 0.47566161]],
        ]
    )
    m = nn.Conv1d(1, 3, 3, stride=1, bias=False)
    m.weight = flow.nn.Parameter(flow.Tensor(weight))
    m = m.to(device)
    output = m(input)
    np_out = np.array(
        [
            [
                [-0.66102189, -0.31443936, 0.17914855],
                [0.54776692, -0.80329150, 0.38541752],
                [-0.94472277, 0.32745653, -0.03385513],
            ]
        ]
    )
    test_case.assertTrue(np.allclose(output.numpy(), np_out, 1e-6, 1e-6))
    output = output.sum()
    output.backward()
    np_grad = np.array(
        [[[-0.76765651, -1.10261774, 0.29835641, 1.06601286, 1.40097415]]]
    )
    test_case.assertTrue(np.allclose(input.grad.numpy(), np_grad, 1e-6, 1e-6))


def _test_conv1d_stride(test_case, device):
    np_arr = np.array(
        [[[-1.01312506, -0.40687919, 1.59853160, 0.53594196, -1.89935565]]]
    )
    input = flow.Tensor(
        np_arr, dtype=flow.float32, device=flow.device(device), requires_grad=True
    )
    weight = np.array(
        [
            [[0.57514840, 0.26589182, -0.02654600]],
            [[-0.10313249, -0.20797005, -0.48268208]],
            [[-0.22216944, -0.14962578, 0.57433963]],
        ]
    )
    m = nn.Conv1d(1, 3, 3, stride=2, bias=False)
    m.weight = flow.nn.Parameter(flow.Tensor(weight))
    m = m.to(device)
    output = m(input)
    np_out = np.array(
        [
            [
                [-0.73331773, 1.11231577],
                [-0.58247775, 0.64046454],
                [1.20406508, -1.52621090],
            ]
        ]
    )
    test_case.assertTrue(np.allclose(output.numpy(), np_out, 1e-6, 1e-6))
    output = output.sum()
    output.backward()
    np_grad = np.array(
        [[[0.24984647, -0.09170401, 0.31495798, -0.09170401, 0.06511152]]]
    )
    test_case.assertTrue(np.allclose(input.grad.numpy(), np_grad, 1e-6, 1e-6))


def _test_conv1d_group_bias_true(test_case, device):
    np_arr = np.array(
        [
            [
                [1.48566079, 0.54937589, 0.62353903, -0.94114172, -0.60260266],
                [0.61150503, -0.50289607, 1.41735041, -1.85877609, -1.04875529],
            ]
        ]
    )
    input = flow.Tensor(
        np_arr, dtype=flow.float32, device=flow.device(device), requires_grad=True
    )
    weight = np.array(
        [
            [[0.25576305, 0.40814576, -0.05900212]],
            [[-0.24829513, 0.42756805, -0.01354307]],
            [[0.44658303, 0.46889144, 0.41060263]],
            [[0.30083328, -0.52216130, 0.12215579]],
        ]
    )
    bias = np.array([-0.03368823, -0.42125040, -0.42130581, -0.17434336])
    m = nn.Conv1d(2, 4, 3, groups=2, stride=1, bias=True)
    m.weight = flow.nn.Parameter(flow.Tensor(weight))
    m.bias = flow.nn.Parameter(flow.Tensor(bias))
    m = m.to(device)
    np_out = np.array(
        [
            [
                [0.53372419, 0.41684598, -0.22277816],
                [-0.56368178, -0.27830642, -0.97031319],
                [0.19794616, -0.74452549, -1.09052706],
                [0.44534814, -1.29277706, 1.09451222],
            ]
        ]
    )
    output = m(input)
    test_case.assertTrue(np.allclose(output.numpy(), np_out, 1e-6, 1e-6))
    output = output.sum()
    output.backward()
    np_grad = np.array(
        [
            [
                [0.00746793, 0.84318173, 0.77063656, 0.76316863, -0.07254519],
                [0.74741632, 0.69414645, 1.22690487, 0.47948855, 0.53275841],
            ]
        ]
    )
    test_case.assertTrue(np.allclose(input.grad.numpy(), np_grad, 1e-6, 1e-6))


def _test_conv1d_group_large_out_bias_true(test_case, device):
    np_arr = np.array(
        [
            [
                [2.17964911, 0.91623521, 1.24746692, 0.73605931, -0.23738743],
                [-0.70412433, 0.10727754, 1.02078640, -0.09711888, -1.10814202],
            ]
        ]
    )
    input = flow.Tensor(
        np_arr, dtype=flow.float32, device=flow.device(device), requires_grad=True
    )
    weight = np.array(
        [
            [[-2.07307473e-01, 1.28563240e-01, 3.71991515e-01]],
            [[-4.16422307e-01, 3.26921181e-05, -3.85845661e-01]],
            [[-1.82592362e-01, 1.43281639e-01, 4.19321984e-01]],
            [[-2.71174580e-01, 4.21470925e-02, 3.77335936e-01]],
            [[5.46190619e-01, -2.11819887e-01, -2.97858030e-01]],
            [[3.34832489e-01, 2.55918801e-01, -5.56600206e-02]],
        ]
    )
    bias = np.array(
        [-0.56865668, 0.17631066, -0.43992457, -0.24307285, -0.53672957, -0.52927947]
    )
    m = nn.Conv1d(2, 6, 3, groups=2, stride=1, bias=True)
    m.weight = flow.nn.Parameter(flow.Tensor(weight))
    m.bias = flow.nn.Parameter(flow.Tensor(bias))
    m = m.to(device)
    np_out = np.array(
        [
            [
                [-0.43867296, -0.32441288, -0.82094181],
                [-1.21264362, -0.48919463, -0.25154343],
                [-0.18354186, -0.11983716, -0.66178048],
                [0.33756858, -0.26578707, -0.94211930],
                [-1.24808860, -0.66543078, 0.37145507],
                [-0.79440582, -0.22671542, -0.15066233],
            ]
        ]
    )
    output = m(input)
    test_case.assertTrue(np.allclose(output.numpy(), np_out, 1e-6, 1e-6))
    output = output.sum()
    output.backward()
    np_grad = np.array(
        [
            [
                [-0.80632210, -0.53444451, -0.12897667, 0.67734540, 0.40546784],
                [0.60984850, 0.69609451, 0.71991241, 0.11006390, 0.02381789],
            ]
        ]
    )
    test_case.assertTrue(np.allclose(input.grad.numpy(), np_grad, 1e-6, 1e-6))


def _test_conv1d_group_large_in_bias_true(test_case, device):
    np_arr = np.array(
        [
            [
                [0.73829210, 0.32275710, -0.73204273, -0.01697334, 1.72585976],
                [0.52866709, 0.28417364, 1.12931311, 1.73048413, -0.60748184],
                [0.43222603, 0.78825170, -0.62105948, 0.10097823, 0.81639361],
                [0.36671457, 0.24468753, -0.58248740, -0.74464536, -0.38901371],
            ]
        ]
    )
    input = flow.Tensor(
        np_arr, dtype=flow.float32, device=flow.device(device), requires_grad=True
    )
    weight = np.array(
        [
            [
                [-0.29574063, -0.31176069, 0.17234495],
                [0.06092392, 0.30691007, -0.36685407],
            ],
            [
                [0.26149744, 0.07149458, 0.32097560],
                [0.18960869, -0.37148297, -0.13602243],
            ],
        ]
    )
    bias = np.array([-0.35048512, -0.00937920])
    m = nn.Conv1d(4, 2, 3, groups=2, stride=1, bias=True)
    m.weight = flow.nn.Parameter(flow.Tensor(weight))
    m.bias = flow.nn.Parameter(flow.Tensor(bias))
    m = m.to(device)
    np_out = np.array(
        [[[-1.09048378, -0.49156523, 0.99150705], [0.01852397, 0.54882324, 0.31657016]]]
    )
    output = m(input)
    test_case.assertTrue(np.allclose(output.numpy(), np_out, 1e-6, 1e-6))
    output = output.sum()
    output.backward()
    np_grad = np.array(
        [
            [
                [-0.29574063, -0.60750133, -0.43515638, -0.13941574, 0.17234495],
                [0.06092392, 0.36783397, 0.00097990, -0.05994400, -0.36685407],
                [0.26149744, 0.33299202, 0.65396762, 0.39247018, 0.32097560],
                [0.18960869, -0.18187428, -0.31789672, -0.50750542, -0.13602243],
            ]
        ]
    )
    test_case.assertTrue(np.allclose(input.grad.numpy(), np_grad, 1e-6, 1e-6))


def _test_conv1d_compilcate(test_case, device):
    np_arr = np.array(
        [
            [
                [-1.00674784, 0.51784992, 0.39896572, 0.11018554, 0.91136694],
                [1.95886874, 0.89779067, 0.47482130, 0.33313531, -0.49350029],
                [-0.19280219, 0.04023677, 1.66438103, -0.83563608, 0.15925731],
                [1.49166429, 1.45189261, -1.86512125, 0.34329697, 0.20413807],
            ]
        ]
    )
    input = flow.Tensor(
        np_arr, dtype=flow.float32, device=flow.device(device), requires_grad=True
    )
    weight = np.array(
        [
            [
                [-0.36045218, 0.37349278, 0.04565236],
                [0.02423280, -0.09459515, -0.30684742],
            ],
            [
                [-0.30345008, -0.11965130, -0.26765293],
                [0.09876197, 0.03346226, 0.27484050],
            ],
            [
                [-0.37798449, 0.00242459, -0.34125558],
                [-0.05174343, -0.10443231, 0.09526101],
            ],
            [
                [0.34196907, -0.32667893, 0.40264183],
                [0.38025281, 0.26807079, -0.09074812],
            ],
        ]
    )
    bias = np.array([-0.03499984, -0.21616256, 0.13312563, -0.24104381])
    m = nn.Conv1d(4, 4, 3, groups=2, stride=2, padding=2, dilation=2, bias=True)
    m.weight = flow.nn.Parameter(flow.Tensor(weight))
    m.bias = flow.nn.Parameter(flow.Tensor(bias))
    m = m.to(device)
    np_out = np.array(
        [
            [
                [-0.72379637, 0.67248386, 0.21977007],
                [-0.00643994, -0.12861520, -0.41589433],
                [-0.76877236, 0.29273134, -0.42040929],
                [1.06121790, -0.73787093, -0.37839717],
            ]
        ]
    )
    output = m(input)
    test_case.assertTrue(np.allclose(output.numpy(), np_out, 1e-6, 1e-6))
    output = output.sum()
    output.backward()
    np_grad = np.array(
        [
            [
                [-0.41006082, 0.00000000, -0.63206136, 0.00000000, 0.03184089],
                [0.06186188, 0.00000000, 0.02985496, 0.00000000, -0.09313981],
                [-0.36026976, 0.00000000, -0.29888350, 0.00000000, -0.26286808],
                [0.49214786, 0.00000000, 0.49666074, 0.00000000, 0.16815135],
            ]
        ]
    )
    test_case.assertTrue(np.allclose(input.grad.numpy(), np_grad, 1e-6, 1e-6))


@unittest.skipIf(
    not flow.unittest.env.eager_execution_enabled(),
    ".numpy() doesn't work in lazy mode",
)
class TestConv1d(flow.unittest.TestCase):
    def test_conv1d(test_case):
        arg_dict = OrderedDict()
        arg_dict["test_fun"] = [
            _test_conv1d_bias_true,
            _test_conv1d_bias_false,
            _test_conv1d_dilation,
            _test_conv1d_stride,
            _test_conv1d_group_bias_true,
            _test_conv1d_group_large_out_bias_true,
            _test_conv1d_group_large_in_bias_true,
            _test_conv1d_compilcate,
        ]
        arg_dict["device"] = ["cuda", "cpu"]

        for arg in GenArgList(arg_dict):
            arg[0](test_case, *arg[1:])


if __name__ == "__main__":
    unittest.main()
