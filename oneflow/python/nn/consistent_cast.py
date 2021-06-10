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
from __future__ import absolute_import
import re
import functools
from inspect import isfunction
from typing import Union, Optional, Tuple, List, Callable
import oneflow as flow
from oneflow.python.oneflow_export import oneflow_export
from oneflow.python.nn.module import Module
import oneflow.python.framework.session_context as session_ctx
import oneflow.python.nn.consistent_cast_util as consistent_cast_util


@oneflow_export("consistent_cast")
def api_consistent_cast(
    parallel_distribution: Tuple[
        List[Union[Tuple[str], str]], List[Union[Tuple[str], str]]
    ],
    placement_signature: Optional[
        Tuple[List[flow.placement], List[flow.placement],]
    ] = None,
):
    def check_input_is_valid(parallel_distribution, placement_signature):
        assert len(parallel_distribution) == len(placement_signature)
        for i in range(len(parallel_distribution)):
            if isinstance(parallel_distribution[i], (tuple, list)):
                assert len(parallel_distribution[i]) == len(
                    placement_signature[i].hierarchy
                )
                for sbp_parallel_str in parallel_distribution:
                    assert re.match("^B|P|(S\(\d+\))$", sbp_parallel_str) is not None, (
                        "Distribute %s is not valid" % sbp_parallel_str
                    )
            else:
                assert (
                    re.match("^B|P|(S\(\d+\))$", parallel_distribution[0]) is not None
                ), ("Distribute %s is not valid" % parallel_distribution)
                assert len(placement_signature[i].hierarchy) == 1

    if placement_signature is None:
        cur_scope = flow.current_scope()
        placement_signature = (
            [cur_scope.device_parallel_desc_symbol for _ in parallel_distribution[0]],
            [cur_scope.device_parallel_desc_symbol for _ in parallel_distribution[1]],
        )
    check_input_is_valid(parallel_distribution[0], placement_signature[0])
    check_input_is_valid(parallel_distribution[1], placement_signature[1])

    def mirrored_entity_consistent_cast(mirrored_entity: Callable):
        assert callable(mirrored_entity), "mirrored_entity is not callable"
        if isfunction(mirrored_entity):

            @functools.wraps(mirrored_entity)
            def wrapped_func(*args):
                args = list(args)
                sess = session_ctx.GetDefaultSession()
                with sess.consistent_scope():
                    args = consistent_cast_util.cast_input_to_consistent(
                        args, parallel_distribution[0], placement_signature[0]
                    )
                    consistent_output = mirrored_entity(*args)
                    return consistent_cast_util.cast_output_from_consistent(
                        consistent_output,
                        parallel_distribution[1],
                        placement_signature[1],
                    )

            return wrapped_func
        else:
            return mirrored_entity.to_consistent(
                parallel_distribution, placement_signature
            )

    return mirrored_entity_consistent_cast
