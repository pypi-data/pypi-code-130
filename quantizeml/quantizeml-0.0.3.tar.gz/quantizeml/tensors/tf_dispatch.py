#!/usr/bin/env python
# ******************************************************************************
# Copyright 2022 Brainchip Holdings Ltd.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ******************************************************************************
import warnings
import tensorflow as tf
import keras
from typing import List, Union

from .qtensor import QTensor, floor_through
from .fixed_point import FixedPoint
from .qfloat import QFloat


def warn_float_conversion(x, op):
    if tf.executing_eagerly():
        x_name = "FixedPoint"
    else:
        x_name = x.name
    warnings.warn(f"Reverting {x_name} to float to perform {op} with Tensor")


def assert_fp_per_tensor(x):
    tf.debugging.assert_rank(x.frac_bits, tf.constant(0))


def assert_qf_per_tensor(x):
    tf.debugging.assert_rank(x.scales.values, tf.constant(0))


def assert_per_tensor(x):
    if isinstance(x, FixedPoint):
        assert_fp_per_tensor(x)
    elif isinstance(x, QFloat):
        assert_qf_per_tensor(x)


@tf.experimental.dispatch_for_binary_elementwise_apis(FixedPoint, tf.Tensor)
def fp_tensor_binary_elementwise_api_handler(api_func, x, y):
    warn_float_conversion(x, api_func)
    return api_func(x.to_float(), y)


@tf.experimental.dispatch_for_binary_elementwise_apis(tf.Tensor, FixedPoint)
def tensor_fp_binary_elementwise_api_handler(api_func, x, y):
    warn_float_conversion(y, api_func)
    return api_func(x, y.to_float())


@tf.experimental.dispatch_for_api(tf.add)
def fp_add(x: FixedPoint, y: FixedPoint):
    return x + y


@tf.experimental.dispatch_for_api(tf.clip_by_value)
def fp_clip_by_value(t: FixedPoint, clip_value_min, clip_value_max, name=None):
    """Clips tensor values to a specified min and max.

    Args:
        t (:obj:`FixedPoint`): the FixedPoint to be clipped.
        clip_value_min (:obj:`FixedPoint`, int): the minimum value.
        clip_value_max (:obj:`FixedPoint`, int): the maximum value.
        name (str, optional): the name for the Tensorflow ops. Defaults to None.

    Returns:
        :obj:`FixedPoint`: the clipped FixedPoint.
    """
    if isinstance(clip_value_min, int):
        clip_value_min = FixedPoint(clip_value_min)
    if isinstance(clip_value_max, int):
        clip_value_max = FixedPoint(clip_value_max)
    if not isinstance(clip_value_min, FixedPoint) or not isinstance(clip_value_max, FixedPoint):
        raise TypeError("Min/max values must be integer or FixedPoint")
    # Adjust the clip min/max values fractional bits
    s_min_values = FixedPoint._lshift(
        clip_value_min.values, (t.frac_bits - clip_value_min.frac_bits))
    s_max_values = FixedPoint._lshift(
        clip_value_max.values, (t.frac_bits - clip_value_max.frac_bits))
    clip_values = tf.clip_by_value(t.values, s_min_values, s_max_values, name)
    return FixedPoint(clip_values, t.frac_bits, t.value_bits)


@tf.experimental.dispatch_for_api(tf.math.reduce_sum)
def fp_reduce_sum(input_tensor: FixedPoint, axis=None, keepdims=False, name=None):
    """Computes the sum of elements across dimensions of a FixedPoint.

    Args:
        input_tensor (:obj:`FixedPoint`): the FixedPoint to be summed.
        axis (list, optional): the dimensions to reduce. If None, reduces all
            dimensions. Defaults to None.
        keepdims (bool, optional): if true, retains reduced dimensions with length 1.
            Defaults to False.
        name (str, optional): the name for the Tensorflow ops. Defaults to None.

    Returns:
        :obj:`FixedPoint`: the summed FixedPoint.
    """
    # The sum fractional bits is the max of all terms
    s_frac_bits = tf.math.reduce_max(input_tensor.frac_bits)
    # Align all terms on the same fractional bits
    input_values = FixedPoint._lshift(
        input_tensor.values, s_frac_bits - input_tensor.frac_bits)
    # Reduce sum
    s_values = tf.math.reduce_sum(
        input_values, axis, keepdims=keepdims, name=name)
    # Return a new FixedPoint
    return FixedPoint(s_values, s_frac_bits, input_tensor.value_bits)


@tf.experimental.dispatch_for_api(tf.linalg.matmul)
def fp_matmul(a: FixedPoint,
              b: QTensor,
              transpose_a=False,
              transpose_b=False,
              adjoint_a=False,
              adjoint_b=False,
              a_is_sparse=False,
              b_is_sparse=False,
              output_type=None,
              name=None):
    """Multiplies matrix `a` by matrix `b`, producing `a` * `b`.

    A `tf.Tensor` of the same type as `a` and `b` where each inner-most matrix
    is the product of the corresponding matrices in `a` and `b`, e.g. if all
    transpose or adjoint attributes are `False`:
    `output[..., i, j] = sum_k (a[..., i, k] * b[..., k, j])`,
    for all indices `i`, `j`.

    Note: This is matrix product, not element-wise product.


    Args:
        a (:obj:`FixedPoint`): a FixedPoint of rank > 1.
        b (:obj:`FixedPoint`): a FixedPoint with same rank as `a`.
        transpose_a (bool, optional): if `True`, `a` is transposed before multiplication.
            Defaults to False.
        transpose_b (bool, optional): if `True`, `b` is transposed before multiplication.
            Defaults to False.
        adjoint_a (bool, optional): if `True`, `a` is conjugated and transposed before
            multiplication. Defaults to False.
        adjoint_b (bool, optional): if `True`, `b` is conjugated and transposed before
            multiplication. Defaults to False.
        a_is_sparse (bool, optional): must be False, argument kept for compatibility with
            original tf.matmul. Defaults to False.
        b_is_sparse (bool, optional): must be False, argument kept for compatibility with
            original tf.matmul. Defaults to False.
        output_type (NoneType, optional): must be None, argument kept for compatibility
            with original tf.matmul. Defaults to None.
        name (str, optional): the name for the operation. Defaults to None.

    Returns:
        :obj:`FixedPoint`: the multiplied FixedPoint.
    """
    if a_is_sparse:
        raise TypeError(
            f"Unsupported argument: a_is_sparse, provided {a_is_sparse}")
    if b_is_sparse:
        raise TypeError(
            f"Unsupported argument: b_is_sparse, provided {b_is_sparse}")
    if output_type is not None:
        raise TypeError(
            f"Unsupported argument: output_type, provided {output_type}")

    # We don't support matmul between vectors
    tf.debugging.assert_rank_at_least(a.values, 2)
    tf.debugging.assert_rank_at_least(b.values, 2)

    if not transpose_a:
        # Since the last dimension is collapsed by the matmul, a must be quantized per-tensor
        assert_fp_per_tensor(a)

    if isinstance(b, FixedPoint):
        if transpose_b:
            # Since the last dimension is collapsed by the matmul, b must be quantized per-tensor
            assert_fp_per_tensor(b)
        b_frac_bits = b.frac_bits
    else:
        b_frac_bits = b.scales.frac_bits
        if transpose_b:
            # We only support tranposed matmul if the QFloat is per-tensor
            assert_qf_per_tensor(b)

    # Do matmul on values
    m_values = floor_through(
        tf.matmul(a.values, b.values, transpose_a, transpose_b, adjoint_a,
                  adjoint_b, name))
    if isinstance(b, QFloat):
        # Multiply by the scales
        m_values *= b.scales.values

    # Return a new FixedPoint
    return FixedPoint(m_values, a.frac_bits + b_frac_bits, a.value_bits)


@tf.experimental.dispatch_for_api(tf.shape)
def fp_shape(input: FixedPoint, out_type=tf.dtypes.int32, name=None):
    return tf.shape(input.values, out_type, name)


@tf.experimental.dispatch_for_api(tf.reshape)
def fp_reshape(tensor: FixedPoint, shape, name=None):
    assert_fp_per_tensor(tensor)
    output = tf.reshape(tensor.values, shape, name)
    return FixedPoint(output, tensor.frac_bits, tensor.value_bits)


@tf.experimental.dispatch_for_api(tf.transpose)
def fp_transpose(a: FixedPoint, perm=None, conjugate=False, name="transpose"):
    assert_fp_per_tensor(a)
    output = tf.transpose(a.values, perm, conjugate, name)
    return FixedPoint(output, a.frac_bits, a.value_bits)


@tf.experimental.dispatch_for_api(tf.broadcast_to)
def fp_brodcast_to(input: FixedPoint, shape, name=None):
    """Broadcast a FixedPoint tensor for a compatible shape.

    Args:
        input (:obj:`FixedPoint`): a FixedPoint to broadcast.
        shape (:obj:`tf.Tensor`): an 1-D `int` Tensor representing
            the shape of the desired output. Must be one of the
            following types: `int32`, `int64`.
        name (str, optional): a name for the operation. Defaults to None.

    Returns:
        :obj:`FixedPoint`: the brodcasted output. Has the same
            type as `input`.
  """
    # Check first that the last dimension is unchanged
    tf.assert_equal(input.shape[-1], shape[-1], message="To brodcast FixedPoint input,\
                        last dimension should remain unchanged")
    output = tf.broadcast_to(input.values, shape, name)
    return FixedPoint(output, input.frac_bits, input.value_bits)


@tf.experimental.dispatch_for_api(tf.concat)
def fp_concat(values: List[FixedPoint], axis, name="concat"):
    """Concatenates FixedPoint tensors along one dimension.

    Args:
        values (List of :obj:`FixedPoint`): List of FixedPoint tensors
            to concatenate.
        axis (list): Dimension along which to concatenate.
        name (str, optional): the name for the Tensorflow ops.
            Defaults to "concat".

    Returns:
        :obj:`FixedPoint`: the concatenate output FixedPoint.
    """
    if len(values) == 1:
        return FixedPoint(values[0].values, values[0].frac_bits, values[0].value_bits)

    # For now we only support concatenation of one or two elements
    tf.assert_equal(
        len(values),
        2, f"We only support concatenation of one or two FixedPoint. \
           Receives {len(values)} tensors as input.")

    # For now we don't support concatenation over last dimension
    rank_input = tf.rank(values[0].values)
    if axis < 0:
        dim = axis + rank_input
    else:
        dim = axis
    tf.Assert(tf.math.not_equal(dim, rank_input - 1),
              ['we do not support concatenation over last axis. axis is:', axis])

    # FixedPoint tensors to concatenate should be per-tensor
    assert_fp_per_tensor(values[0])
    assert_fp_per_tensor(values[1])

    tf.assert_equal(values[0].frac_bits, values[1].frac_bits, message=f"the two\
            FixedPoint must have the same frac_bits. Receives {values[0].frac_bits}\
            and {values[1].frac_bits}")
    values_out = tf.concat([values[0].values, values[1].values], axis, name)

    return FixedPoint(
        values_out, values[0].frac_bits, max(
            values[0].value_bits, values[1].value_bits))


@tf.experimental.dispatch_for_api(tf.math.reduce_max)
def fp_reduce_max(input_tensor: FixedPoint,
                  axis=None,
                  keepdims=False,
                  name=None):
    """Computes the maximum of elements across dimensions of a FixedPoint.

    Args:
        input_tensor (:obj:`FixedPoint`): the FixedPoint to be estimated.
        axis (list, optional): the dimensions to reduce. If None, reduces all
            dimensions. Defaults to None.
        keepdims (bool, optional): if true, retains reduced dimensions with length 1.
            Defaults to False.
        name (str, optional): the name for the Tensorflow ops. Defaults to None.

    Returns:
        :obj:`FixedPoint`: the maximum FixedPoint.
    """
    # We only support reduce_max if the input is per-tensor
    assert_fp_per_tensor(input_tensor)

    # Reduce max
    s_values = tf.math.reduce_max(input_tensor.values,
                                  axis,
                                  keepdims=keepdims,
                                  name=name)
    # Return a new FixedPoint
    return FixedPoint(s_values, input_tensor.frac_bits, input_tensor.value_bits)


@tf.experimental.dispatch_for_api(tf.compat.v1.gather)
def fp_gather(params: Union[FixedPoint, QFloat], indices, validate_indices=None,
              name=None, axis=None, batch_dims=0):
    """Gather slices from params along axis.

    Args:
        params (:obj:`FixedPoint`, :obj:`QFloat`): the input QTensor.
        indices (int, list): the indices to gather.
        validate_indices (bool, optional): whether to validate the indices. Defaults to None.
        name (str, optional): the name for the Tensorflow ops. Defaults to None.
        axis (int, optional): the axis to gather along. Defaults to None.
        batch_dims (int, optional): the number of batch dimensions to keep. Defaults to 0.

    Returns:
        :obj:`QTensor`: a QTensor containing the gathered values.
    """
    # We do not support gather along the last axis if the QTensor is per-axis
    if axis in (-1, len(params.shape)):
        assert_per_tensor(params)
    # Create a new QTensor, gather the indices in a desired axis
    x_gather = tf.gather(params.values, indices, validate_indices, axis, batch_dims, name)
    if isinstance(params, QFloat):
        return QFloat(x_gather, params.scales, params.value_bits)
    if isinstance(params, FixedPoint):
        return FixedPoint(x_gather, params.frac_bits, params.value_bits)
    raise ValueError("Params must be a FixedPoint or QFloat")


@tf.experimental.dispatch_for_api(keras.backend.depthwise_conv2d)
def fp_depthwise_conv2d(x: FixedPoint,
                        depthwise_kernel: QTensor,
                        strides=(1, 1),
                        padding='valid',
                        data_format=None,
                        dilation_rate=(1, 1)):
    """ 2D convolution with separable filters.

    Args:
        x (obj:`FixedPoint`): input tensor.
        depthwise_kernel (:obj:`QTensor`): convolution kernel for the depthwise convolution.
        strides (tuple, optional): strides tuple (length 2). Defaults to (1, 1).
        padding (str, optional): `"same"` or `"valid"`. Default to 'valid'.
        data_format (str, optional): `"channels_last"` or `"channels_first"`. Defaults to None.
        dilation_rate (tuple, optional): tuple of integers, dilation rates for the separable
            convolution. Defaults to (1, 1).

    Returns:
        :obj:`FixedPoint`: output tensor.

    """
    # Evaluate the maximum number of fractional bits
    input_frac_bits = tf.reduce_max(x.frac_bits)

    # If x has multiple fractional bits, we must align the values along the last dimension before
    # the convolution collapses it
    x = tf.cond(tf.rank(x.frac_bits) > 0,
                lambda: x << (input_frac_bits - x.frac_bits),
                lambda: x)

    if isinstance(depthwise_kernel, FixedPoint):
        filters_frac_bits = depthwise_kernel.frac_bits
    else:
        filters_frac_bits = depthwise_kernel.scales.frac_bits

    # Do convolution on values
    conv_values = floor_through(
        keras.backend.depthwise_conv2d(x.values, depthwise_kernel.values, strides, padding,
                                       data_format, dilation_rate))
    if isinstance(depthwise_kernel, QFloat):
        # Multiply by the scales
        conv_values *= depthwise_kernel.scales.values

    # Return a new FixedPoint
    return FixedPoint(conv_values, input_frac_bits + filters_frac_bits, x.value_bits)


@tf.experimental.dispatch_for_api(tf.nn.convolution)
def fp_convolution(
        input: FixedPoint,
        filters: QTensor,
        strides=None, padding="VALID", data_format=None, dilations=None, name=None):
    """Perform the convolution operation between input and filter tensors.

    Args:
        input (:obj:`FixedPoint`): The input FixedPoint.
        filters (:obj:`QTensor`): The filters Qtensor.
        strides (list, optional): Sequence of N ints >= 1.  Specifies the output stride.
        padding (str, optional): A string, either `"VALID"` or `"SAME"`. The padding algorithm.
            Defaults to "VALID"
        data_format (str, optional): Specifies whether the channel dimension of
            the `input` and output is the last dimension (default, or if `data_format`
            does not start with "NC"), or the second dimension (if `data_format`
            starts with "NC").  For N=1, the valid values are "NWC" (default) and
            "NCW".  For N=2, the valid values are "NHWC" (default) and "NCHW".
            For N=3, the valid values are "NDHWC" (default) and "NCDHW".
        dilations (list, optional): Alias for dilation_rate. Sequence of N ints >= 1.
            Specifies the filter upsampling/input downsampling rate. Default to None.
        name (str, optional): the name for the Tensorflow ops. Defaults to None.

    Returns:
        :obj:`FixedPoint`: a FixedPoint containing the output values.
    """
    # Evaluate the maximum number of fractional bits
    input_frac_bits = tf.reduce_max(input.frac_bits)

    # If a has multiple fractional bits, we must align the values along the
    # last dimension before the convolution collapses it
    input = tf.cond(tf.rank(input.frac_bits) > 0,
                    lambda: input << (input_frac_bits - input.frac_bits),
                    lambda: input)

    if isinstance(filters, FixedPoint):
        filters_frac_bits = filters.frac_bits
    else:
        filters_frac_bits = filters.scales.frac_bits

    # Do convolution on values
    conv_values = floor_through(
        tf.nn.convolution(input.values, filters.values, strides, padding, data_format,
                          dilations, name))
    if isinstance(filters, QFloat):
        # Multiply by the scales
        conv_values *= filters.scales.values

    # Return a new FixedPoint
    return FixedPoint(conv_values, input_frac_bits + filters_frac_bits, input.value_bits)
