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
QuantizedDepthwiseConv2D layer definition.
"""

import tensorflow as tf
from keras import backend
from keras.layers import DepthwiseConv2D

from ..tensors import FixedPoint, MAX_BUFFER_BITWIDTH
from .layers import deserialize_quant_object, Calibrable


__all__ = ["QuantizedDepthwiseConv2D"]


@tf.keras.utils.register_keras_serializable()
class QuantizedDepthwiseConv2D(Calibrable, DepthwiseConv2D):
    """ A depthwise convolutional layer that operates on quantized inputs and weights.
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

        self.buffer_bitwidth = self.quant_config.get("buffer_bitwidth", MAX_BUFFER_BITWIDTH) - 1
        assert self.buffer_bitwidth > 0, "The buffer_bitwidth must be a strictly positive integer."

    def call(self, inputs, training=None):
        # raise an error if the inputs are not FixedPoint or tf.Tensor
        if not isinstance(inputs, (FixedPoint, tf.Tensor)):
            raise TypeError(f"QuantizedDepthwiseConv2D only accepts FixedPoint\
                               or tf.Tensor inputs. Receives {type(inputs)} inputs.")

        # Quantize the weights
        depthwise_kernel = self.weight_quantizer(self.depthwise_kernel, training)

        if isinstance(inputs, tf.Tensor):
            # Assume the inputs are integer stored as float, which is the only tf.Tensor
            # inputs that are allowed
            inputs = FixedPoint.quantize(inputs, 0, 8)

        inputs = inputs.promote(self.buffer_bitwidth)

        outputs = backend.depthwise_conv2d(
            inputs,
            depthwise_kernel,
            strides=self.strides,
            padding=self.padding,
            dilation_rate=self.dilation_rate,
            data_format=self.data_format)

        if self.use_bias:
            outputs = tf.add(outputs, self.bias_quantizer(self.bias, training))

        if self.out_quantizer is not None:
            outputs = self.out_quantizer(outputs)
        return outputs

    def get_config(self):
        config = super().get_config()
        config["quant_config"] = self.quant_config
        return config
