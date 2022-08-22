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
import keras

from ..tensors import FixedPoint, MAX_BUFFER_BITWIDTH
from .layers import deserialize_quant_object, Calibrable, CalibrableVariable, has_shift_info

__all__ = ["QuantizedDense"]


@tf.keras.utils.register_keras_serializable()
class QuantizedDense(Calibrable, keras.layers.Dense):
    """A Dense layer that operates on quantized inputs and weights
    """

    def __init__(self, *args, quant_config={}, **kwargs):
        super().__init__(*args, **kwargs)
        self.quant_config = quant_config
        self.out_quantizer = deserialize_quant_object(
            self.quant_config, "output_quantizer", False)
        self.weight_quantizer = deserialize_quant_object(
            self.quant_config, "weight_quantizer", True)
        if self.use_bias:
            self.bias_quantizer = deserialize_quant_object(
                self.quant_config, "bias_quantizer", True)
        self.buffer_bitwidth = self.quant_config.get(
            "buffer_bitwidth", MAX_BUFFER_BITWIDTH) - 1
        assert self.buffer_bitwidth > 0, "The buffer_bitwidth must be a strictly positive integer."

        # Has shift info evaluated only at init
        self.has_shift_info = has_shift_info()
        if self.has_shift_info:
            # Add objects that will store the shift values.
            self.shift_matmul = CalibrableVariable()
            self.shift_output_bias = CalibrableVariable()
            self.shift_bias_output = CalibrableVariable()
            if self.out_quantizer:
                self.shift_output = CalibrableVariable()

    def call(self, inputs, training=None):
        # raise an error if the inputs are not FixedPoint or tf.Tensor
        if not isinstance(inputs, (FixedPoint, tf.Tensor)):
            raise TypeError(f"QuantizedDense only accepts FixedPoint or tf.Tensor\
                              inputs. Receives {type(inputs)} inputs.")

        # Quantize the weights
        kernel = self.weight_quantizer(self.kernel, training)

        if isinstance(inputs, tf.Tensor):
            # Assume the inputs are integer stored as float, which is the only tf.Tensor
            # inputs that are allowed
            inputs = FixedPoint.quantize(inputs, 0, 8)

        # Prepare inputs before invoking matmul:
        # - promote to a higher bitwidth to avoid overflows,
        # - align all channels on the same fractional bits
        inputs, shift = inputs.promote(self.buffer_bitwidth).align()
        # - update shift values if calibration is enabled
        if self.has_shift_info:
            self.shift_matmul(shift)

        outputs = tf.matmul(inputs, kernel)

        if self.use_bias:
            # Quantize biases
            bias = self.bias_quantizer(self.bias, training)
            # Promote them before alignment to avoid overflow
            bias = bias.promote(self.buffer_bitwidth)
            # Align intermediate outputs and biases before adding them
            outputs, shift = outputs.align(bias)
            if self.has_shift_info:
                self.shift_output_bias(shift)
            bias, shift = bias.align(outputs)
            if self.has_shift_info:
                self.shift_bias_output(shift)
            outputs = tf.add(outputs, bias)

        if self.out_quantizer is not None:
            internal_out_frac_bits = outputs.frac_bits
            outputs = self.out_quantizer(outputs)
            out_frac_bits = tf.cast(self.out_quantizer.frac_bits, tf.float32)
            # update shift values
            shift = out_frac_bits - internal_out_frac_bits
            if self.has_shift_info:
                self.shift_output(shift)
        return outputs

    def get_config(self):
        config = super().get_config()
        config["quant_config"] = self.quant_config
        return config
