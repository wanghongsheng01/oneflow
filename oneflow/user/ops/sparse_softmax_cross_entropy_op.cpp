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
#include "oneflow/core/framework/framework.h"

namespace oneflow {

namespace {

Maybe<void> InferTensorDescFn(user_op::InferContext* ctx) {
  const user_op::TensorDesc* prediction_desc = ctx->TensorDesc4ArgNameAndIndex("prediction", 0);
  const user_op::TensorDesc* label_desc = ctx->TensorDesc4ArgNameAndIndex("label", 0);
  CHECK_EQ_OR_RETURN(prediction_desc->is_dynamic(), label_desc->is_dynamic());
  CHECK_GE_OR_RETURN(prediction_desc->shape().NumAxes(), 2);
  const int64_t num_out_axes = prediction_desc->shape().NumAxes() - 1;
  CHECK_EQ_OR_RETURN(label_desc->shape().NumAxes(), num_out_axes);
  FOR_RANGE(int64_t, i, 0, num_out_axes) {
    CHECK_EQ_OR_RETURN(prediction_desc->shape().At(i), label_desc->shape().At(i));
  }
  *ctx->OutputIsDynamic("prob", 0) = prediction_desc->is_dynamic();
  // 'prob' is just for compute prediction's grad, prob's grad will be ignored
  *ctx->OutputShape("prob", 0) = prediction_desc->shape();
  user_op::TensorDesc* out_desc = ctx->OutputTensorDesc("out", 0);
  *out_desc->mut_is_dynamic() = prediction_desc->is_dynamic();
  *out_desc->mut_shape() = label_desc->shape();
  return Maybe<void>::Ok();
}

Maybe<void> InferGradTensorDescFn(user_op::InferContext* ctx) {
  const user_op::TensorDesc* prob_desc = ctx->TensorDesc4ArgNameAndIndex("prob", 0);
  const user_op::TensorDesc* label_desc = ctx->TensorDesc4ArgNameAndIndex("label", 0);
  const user_op::TensorDesc* dy_desc = ctx->TensorDesc4ArgNameAndIndex("dy", 0);
  CHECK_EQ_OR_RETURN(prob_desc->is_dynamic(), label_desc->is_dynamic());
  CHECK_GE_OR_RETURN(prob_desc->shape().NumAxes(), 2);
  const int64_t num_out_axes = prob_desc->shape().NumAxes() - 1;
  CHECK_EQ_OR_RETURN(label_desc->shape().NumAxes(), num_out_axes);
  FOR_RANGE(int64_t, i, 0, num_out_axes) {
    CHECK_EQ_OR_RETURN(prob_desc->shape().At(i), label_desc->shape().At(i));
  }
  CHECK_EQ_OR_RETURN(dy_desc->shape(), label_desc->shape());
  *ctx->OutputShape("prediction_diff", 0) = prob_desc->shape();
  *ctx->OutputIsDynamic("prediction_diff", 0) = prob_desc->is_dynamic();
  return Maybe<void>::Ok();
}

Maybe<void> InferDataType(user_op::InferContext* ctx) {
  const user_op::TensorDesc* label_desc = ctx->TensorDesc4ArgNameAndIndex("label", 0);
  CHECK_OR_RETURN(IsIndexDataType(label_desc->data_type()));
  *ctx->OutputDType("prob", 0) = ctx->InputDType("prediction", 0);
  *ctx->OutputDType("out", 0) = ctx->InputDType("prediction", 0);
  return Maybe<void>::Ok();
}

Maybe<void> InferDataTypeGrad(user_op::InferContext* ctx) {
  const user_op::TensorDesc* prob_desc = ctx->TensorDesc4ArgNameAndIndex("prob", 0);
  const user_op::TensorDesc* label_desc = ctx->TensorDesc4ArgNameAndIndex("label", 0);
  CHECK_OR_RETURN(IsIndexDataType(label_desc->data_type()));
  const user_op::TensorDesc* dy_desc = ctx->TensorDesc4ArgNameAndIndex("dy", 0);
  CHECK_EQ_OR_RETURN(dy_desc->data_type(), prob_desc->data_type());
  *ctx->OutputDType("prediction_diff", 0) = prob_desc->data_type();
  return Maybe<void>::Ok();
}

Maybe<void> AddSignature(user_op::SbpContext* ctx) {
  ctx->NewBuilder()
      .Split(user_op::OpArg("prediction", 0), 0)
      .Split(user_op::OpArg("label", 0), 0)
      .Split(user_op::OpArg("prob", 0), 0)
      .Split(user_op::OpArg("out", 0), 0)
      .Build();
  return Maybe<void>::Ok();
}

Maybe<void> AddMsSignature(user_op::SbpContext* ctx) {
  const user_op::TensorDesc& prediction =
      ctx->LogicalTensorDesc4InputArgNameAndIndex("prediction", 0);
  ctx->NewBuilder()
      .Split(user_op::OpArg("prediction", 0), 0)
      .Split(user_op::OpArg("prob", 0), 0)
      .Split(user_op::OpArg("label", 0), 0)
      .Split(user_op::OpArg("out", 0), 0)
      .Build();
  ctx->NewBuilder()
      .Split(user_op::OpArg("prediction", 0), prediction.shape().NumAxes() - 1)
      .Split(user_op::OpArg("prob", 0), prediction.shape().NumAxes() - 1)
      .Broadcast(user_op::OpArg("label", 0))
      .PartialSum(user_op::OpArg("out", 0))
      .Build();
  return Maybe<void>::Ok();
}

Maybe<void> AddGradSignature(user_op::SbpContext* ctx) {
  ctx->NewBuilder()
      .Split(user_op::OpArg("dy", 0), 0)
      .Split(user_op::OpArg("label", 0), 0)
      .Split(user_op::OpArg("prob", 0), 0)
      .Split(user_op::OpArg("prediction_diff", 0), 0)
      .Build();
  return Maybe<void>::Ok();
}

Maybe<void> AddGradMsSignature(user_op::SbpContext* ctx) {
  const user_op::TensorDesc& prob = ctx->LogicalTensorDesc4InputArgNameAndIndex("prob", 0);
  ctx->NewBuilder()
      .Split(user_op::OpArg("prob", 0), 0)
      .Split(user_op::OpArg("label", 0), 0)
      .Split(user_op::OpArg("dy", 0), 0)
      .Split(user_op::OpArg("prediction_diff", 0), 0)
      .Build();
  ctx->NewBuilder()
      .Split(user_op::OpArg("prob", 0), prob.shape().NumAxes() - 1)
      .Broadcast(user_op::OpArg("label", 0))
      .Broadcast(user_op::OpArg("dy", 0))
      .Split(user_op::OpArg("prediction_diff", 0), prob.shape().NumAxes() - 1)
      .Build();
  return Maybe<void>::Ok();
}

template<Maybe<void> (*GetSbpSignature)(user_op::SbpContext*)>
Maybe<void> GetSbpFn(user_op::SbpContext* ctx) {
  JUST(GetSbpSignature(ctx));
  return Maybe<void>::Ok();
}

void GenBackwardOpConf4SparseSoftmaxCrossEntropy(const std::string& op_type_name,
                                                 const user_op::UserOpWrapper& op,
                                                 user_op::AddOpFn AddOp) {
  if (op.NeedGenGradTensor4OpInput("prediction", 0)) {
    user_op::UserOpConfWrapperBuilder builder(op.op_name() + "_grad");
    user_op::UserOpConfWrapper grad_op = builder.Op(op_type_name)
                                             .Input("prob", op.output("prob", 0))
                                             .Input("label", op.input("label", 0))
                                             .Input("dy", op.GetGradTensorWithOpOutput("out", 0))
                                             .Output("prediction_diff")
                                             .Attr("depth", op.attr<int64_t>("depth"))
                                             .Build();
    op.BindGradTensorWithOpInput(grad_op.output("prediction_diff", 0), "prediction", 0);
    AddOp(grad_op);
  }
}

}  // namespace

#define REGISTER_SPAESE_SOFTMAX_CROSS_ENTROPY_USER_OP(op_name, sbp_sig)                \
  REGISTER_USER_OP(op_name)                                                            \
      .Input("prediction")                                                             \
      .Input("label")                                                                  \
      .Output("prob")                                                                  \
      .Output("out")                                                                   \
      .Attr<int64_t>("depth")                                                          \
      .SetTensorDescInferFn(InferTensorDescFn)                                         \
      .SetInputArgModifyFn([](user_op::GetInputArgModifier GetInputArgModifierFn,      \
                              const user_op::UserOpConfWrapper&) {                     \
        user_op::InputArgModifier* label_modifier = GetInputArgModifierFn("label", 0); \
        CHECK(label_modifier != nullptr);                                              \
        label_modifier->set_requires_grad(false);                                      \
      })                                                                               \
      .SetGetSbpFn(GetSbpFn<sbp_sig>)                                                  \
      .SetDataTypeInferFn(InferDataType);

#define REGISTER_SPAESE_SOFTMAX_CROSS_ENTROPY_GRAD_USER_OP(op_name, sbp_sig) \
  REGISTER_USER_OP(op_name)                                                  \
      .Input("label")                                                        \
      .Input("dy")                                                           \
      .Input("prob")                                                         \
      .Output("prediction_diff")                                             \
      .Attr<int64_t>("depth")                                                \
      .SetTensorDescInferFn(InferGradTensorDescFn)                           \
      .SetGetSbpFn(GetSbpFn<sbp_sig>)                                        \
      .SetDataTypeInferFn(InferDataTypeGrad);

REGISTER_SPAESE_SOFTMAX_CROSS_ENTROPY_USER_OP("sparse_softmax_cross_entropy", AddSignature);
REGISTER_SPAESE_SOFTMAX_CROSS_ENTROPY_USER_OP("sparse_softmax_cross_entropy_ms", AddMsSignature);
REGISTER_SPAESE_SOFTMAX_CROSS_ENTROPY_GRAD_USER_OP("sparse_softmax_cross_entropy_grad",
                                                   AddGradSignature);
REGISTER_SPAESE_SOFTMAX_CROSS_ENTROPY_GRAD_USER_OP("sparse_softmax_cross_entropy_ms_grad",
                                                   AddGradMsSignature);

REGISTER_USER_OP_GRAD("sparse_softmax_cross_entropy")
    .SetGenBackwardOpConfFn([](const user_op::UserOpWrapper& op, user_op::AddOpFn AddOp) {
      return GenBackwardOpConf4SparseSoftmaxCrossEntropy("sparse_softmax_cross_entropy_grad", op,
                                                         AddOp);
    });

REGISTER_USER_OP_GRAD("sparse_softmax_cross_entropy_ms")
    .SetGenBackwardOpConfFn([](const user_op::UserOpWrapper& op, user_op::AddOpFn AddOp) {
      return GenBackwardOpConf4SparseSoftmaxCrossEntropy("sparse_softmax_cross_entropy_ms_grad", op,
                                                         AddOp);
    });

}  // namespace oneflow
