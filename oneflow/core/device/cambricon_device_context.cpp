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
#include "oneflow/core/device/cambricon_device_context.h"
#include "oneflow/core/thread/thread_context.h"

namespace oneflow {

#ifdef WITH_CAMBRICON

REGISTER_DEVICE_CONTEXT(DeviceType::kCambricon, ([](const ThreadCtx& thread_ctx) -> DeviceCtx* {
                          CambriconQueueHandle* cambricon_queue = nullptr;
                          cambricon_queue = thread_ctx.g_cambricon_queue.get();
                          return new CambriconDeviceCtx(cambricon_queue);
                        }));

#endif  // WITH_CAMBRICON

}  // namespace oneflow