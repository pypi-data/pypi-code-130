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
"""
QuantizedSeparableConv2D layer definition.
"""

import tensorflow as tf
from keras.layers import SeparableConv2D
from keras.utils import conv_utils
from keras import backend

from ..tensors import FixedPoint, MAX_BUFFER_BITWIDTH
from .layers import deserialize_quant_object, Calibrable


__all__ = ["QuantizedSeparableConv2D"]


@tf.keras.utils.register_keras_serializable()
class QuantizedSeparableConv2D(Calibrable, SeparableConv2D):
    """ A separable convolutional layer that operates on quantized inputs and weights.
    """

    def __init__(self, *args, quant_config={}, **kwargs):
        if 'dilation_rate' in kwargs:
            if kwargs['dilation_rate'] not in [1, [1, 1], (1, 1)]:
                raise ValueError("Keyword argument 'dilation_rate' is not supported in \
                                 QuantizedSeparableConv2D.")
        if 'depth_multiplier' in kwargs:
            if kwargs['depth_multiplier'] != 1:
                raise ValueError("Keyword argument 'depth_multiplier' is not supported in \
                                 QuantizedSeparableConv2D.")

        super().__init__(*args, **kwargs)
        self.quant_config = quant_config

        self.out_quantizer = deserialize_quant_object(
            self.quant_config, "output_quantizer", False)

        # Separable layer has two weights quantizers to handle different max values but they both
        # use the same configuration
        self.dw_weight_quantizer = deserialize_quant_object(
            self.quant_config, "weight_quantizer", True)
        # Duplicate configuration for pointwise, allows to create an object with a different name
        pw_config = {"pw_weight_quantizer": self.quant_config["weight_quantizer"]}
        self.pw_weight_quantizer = deserialize_quant_object(pw_config, "pw_weight_quantizer", True)

        if self.use_bias:
            self.bias_quantizer = deserialize_quant_object(
                self.quant_config, "bias_quantizer", True)

        self.buffer_bitwidth = self.quant_config.get("buffer_bitwidth", MAX_BUFFER_BITWIDTH) - 1
        assert self.buffer_bitwidth > 0, "The buffer_bitwidth must be a strictly positive integer."
        self.intermediate_quantizer = deserialize_quant_object(
            self.quant_config, "intermediate_quantizer", True)

    def call(self, inputs, training=None):
        # raise an error if the inputs are not FixedPoint or tf.Tensor
        if not isinstance(inputs, (FixedPoint, tf.Tensor)):
            raise TypeError(f"QuantizedSeparableConv2D only accepts FixedPoint\
                               or tf.Tensor inputs. Receives {type(inputs)} inputs.")

        # Quantize the weights
        depthwise_kernel = self.dw_weight_quantizer(self.depthwise_kernel, training)
        pointwise_kernel = self.pw_weight_quantizer(self.pointwise_kernel, training)

        if isinstance(inputs, tf.Tensor):
            # Assume the inputs are integer stored as float, which is the only tf.Tensor
            # inputs that are allowed
            inputs = FixedPoint.quantize(inputs, 0, 8)

        inputs = inputs.promote(self.buffer_bitwidth)
        dw_outputs = backend.depthwise_conv2d(
            inputs,
            depthwise_kernel,
            strides=self.strides,
            padding=self.padding,
            dilation_rate=self.dilation_rate,
            data_format=self.data_format)
        dw_outputs_q = self.intermediate_quantizer(dw_outputs, training)
        dw_outputs_q = dw_outputs_q.promote(self.buffer_bitwidth)
        outputs = tf.nn.convolution(
            dw_outputs_q,
            pointwise_kernel,
            strides=[1, 1, 1, 1],
            padding='VALID',
            data_format=conv_utils.convert_data_format(self.data_format, ndim=4))

        if self.use_bias:
            outputs = tf.add(outputs, self.bias_quantizer(self.bias, training))

        if self.out_quantizer is not None:
            outputs = self.out_quantizer(outputs, training)
        return outputs

    def get_config(self):
        config = super().get_config()
        config["quant_config"] = self.quant_config
        return config
