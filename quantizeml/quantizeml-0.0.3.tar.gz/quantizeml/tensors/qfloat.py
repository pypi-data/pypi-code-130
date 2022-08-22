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
import tensorflow as tf

from .qtensor import QTensor, round_through, ceil_through
from .fixed_point import FixedPoint


class QFloat(QTensor):
    """A Tensor of integer values representing quantized float numbers

    Args:
        values (:obj:`tensorflow.Tensor`): a tensor of integer values
        scales (:obj:`tensorflow.Tensor`): a FixedPoint of scales
        value_bits (int): the number of value bits
    """
    scales: FixedPoint = FixedPoint(1.0, 0, 32)

    def __init__(self, values, scales, value_bits):
        self.scales = scales
        # We store integer values in a float tensor
        values = tf.convert_to_tensor(values, dtype=tf.float32)
        self.values = QTensor.clamp(values, value_bits)
        self.shape = self.values.shape
        self.value_bits = value_bits

    @staticmethod
    def quantize(x, float_max, value_bits, scales_bits):
        """Converts a float Tensor to a QFloat

        It first evaluates the maximum integer values that can be stored for
        the specified value bits: int_max = 2^bits - 1.

        It then converts the original float values into integer values so that:

        x_int = round(x * int_max / float_max)

        The resulting integer values are clipped to [-int_max, int_max].

        Args:
            x (:obj:`tensorflow.Tensor`): a tensor of float values.
            float_max (:obj:`tensorflow.Tensor`): a tensor of maximum values
            value_bits (int): the number of value bits
            scales_bits (int): the number of scales bits

        Returns:
            :obj:`QFloat`: the QFloat representation.
        """
        # Evaluate QFloat scales
        scales = float_max / QTensor.int_max(value_bits)
        # Make sure the scales are at least equal to the scales resolution,
        # otherwise they would be quantized to zero
        scales_res = FixedPoint._pow2(-scales_bits)
        scales = tf.math.maximum(scales, scales_res)
        # Quantize the scales to a FixedPoint
        scales_int_bits = ceil_through(tf.experimental.numpy.log2(scales))
        scales_frac_bits = tf.clip_by_value(scales_bits - scales_int_bits,
                                            0, scales_bits)
        fp_scales = FixedPoint.quantize(scales, scales_frac_bits, scales_bits)
        # Quantize the inputs using the approximated FixedPoint scales
        values = round_through(x / fp_scales.to_float())
        return QFloat(values, fp_scales, value_bits)

    def to_float(self):
        """Returns a float representation of the QFloat

        Returns:
            :obj:`tensorflow.Tensor`: the float representation.
        """
        return self.values * self.scales.to_float()
