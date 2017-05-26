#ifndef ONEFLOW_THREAD_CPU_THREAD_H_
#define ONEFLOW_THREAD_CPU_THREAD_H_

#include "thread/thread.h"

namespace oneflow {

class CpuThread final : public Thread {
 public:
  OF_DISALLOW_COPY_AND_MOVE(CpuThread);
  CpuThread();
  ~CpuThread() = default;

 private:
};

} // namespace oneflow

#endif // ONEFLOW_THREAD_CPU_THREAD_H_
