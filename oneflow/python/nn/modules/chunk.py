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
from typing import Optional

import oneflow as flow
from oneflow.python.framework.tensor import Tensor
from oneflow.python.oneflow_export import oneflow_export, experimental_api
from oneflow.python.nn.module import Module


@oneflow_export("chunk")
@experimental_api
class Chunk(Module):
    r"""Splits a tensor into a specific number of chunks. Each chunk is a view of the input tensor. Last chunk will be smaller if the tensor size along the given dimension dim is not divisible by chunks.

    Args:
        input (oneflow.experimental.Tensor): The tensor to split.
        chunks (int): Number of chunks to return.
        dim (int): Dimension along which to split the tensor.

    Returns:
        List of Tensors.

    For example:

    .. code-block:: python
    
        >>> import oneflow.experimental as flow
        >>> import numpy as np
        >>> flow.enable_eager_execution()

        >>> input = flow.Tensor(np.random.randn(2, 2, 3).astype(np.float32))
        >>> out = flow.nn.chunk(input, chunks = 2, dim = 1)
        >>> out
        
    """

    def __init__(self) -> None:
        super().__init__()

    def forward(self, input, chunks, dim):
        if dim is not None:
            assert (
                input.shape[dim] > 0
            ), "chunk expects at least a 1-dimensional tensor"

            assert (
                chunks > 0
            ), "chunk expects `chunks` to be greater than 0"

            dim_size = input.shape[dim]
            chunk_size = (dim_size + chunks - 1) / chunks
            last_chunk_size = dim_size % chunk_size 
            
            start_list = []
            stop_list = []
            step_list = []
            for dim_i in input.dim():
                if dim_i != dim:
                    slice_tup_list = [None, None, None] # start, stop, step
                else:
                    for chunk in chunks:
                        if last_chunk_size == 0:
                            start_list.append(chunk * chunk_size)
                            stop_list.append((chunk + 1) * chunk_size)
                            step_list.append(1)
                        else:
                            if chunk < chunks -1 :
                                start_list.append(chunk * chunk_size)
                                stop_list.append((chunk + 1) * chunk_size)
                                step_list.append(1)
                            else:
                                start_list.append(dim_size - 1 - last_chunk_size)
                                stop_list.append(dim_size - 1)
                                step_list.append(1)


                            
                             


            






            


        
