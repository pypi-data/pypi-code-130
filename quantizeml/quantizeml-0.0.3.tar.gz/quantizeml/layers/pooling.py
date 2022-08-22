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

from keras.layers import MaxPool2D, GlobalAveragePooling2D

from . import Calibrable, deserialize_quant_object
from ..tensors import FixedPoint, MAX_BUFFER_BITWIDTH

__all__ = ["QuantizedMaxPool2D", "QuantizedGlobalAveragePooling2D"]


@tf.keras.utils.register_keras_serializable()
class QuantizedMaxPool2D(MaxPool2D):
    """A max pooling layer that operates on quantized inputs.

    """
    def call(self, inputs):
        # Raise an error if the inputs are not FixedPoint
        if not isinstance(inputs, FixedPoint):
            raise TypeError(f"QuantizedMaxPool2D only accepts FixedPoint inputs. \
                             Receives {type(inputs)} inputs.")

        outputs = super().call(inputs.values)
        return FixedPoint(outputs, inputs.frac_bits, inputs.value_bits)


@tf.keras.utils.register_keras_serializable()
class QuantizedGlobalAveragePooling2D(Calibrable, GlobalAveragePooling2D):
    """A global average pooling layer that operates on quantized inputs.

    """
    def __init__(self, quant_config={}, **kwargs):
        super().__init__(**kwargs)
        self.spatial_size_inv = None
        self.quant_config = quant_config
        self.out_quantizer = deserialize_quant_object(self.quant_config, "output_quantizer")

    def build(self, input_shape):
        super().build(input_shape)
        # Build the reciprocal of the spatial size
        spatial_size_inv = 1 / (input_shape[1] * input_shape[2])
        self.spatial_size_inv = FixedPoint.quantize(
            spatial_size_inv, MAX_BUFFER_BITWIDTH, MAX_BUFFER_BITWIDTH)

    def call(self, inputs, training=None):
        # Raise an error if the inputs are not FixedPoint
        if not isinstance(inputs, FixedPoint):
            raise TypeError(f"QuantizedMaxPool2D only accepts FixedPoint inputs. \
                             Receives {type(inputs)} inputs.")

        # Promote input to prevent overflow in the reduce_sum op
        inputs = inputs.promote(MAX_BUFFER_BITWIDTH)
        inputs_sum = tf.reduce_sum(inputs, axis=[1, 2], keepdims=self.keepdims)
        inputs_mean = inputs_sum * self.spatial_size_inv
        return self.out_quantizer(inputs_mean, training=training)

    def get_config(self):
        config = super().get_config()
        config.update({"quant_config": self.quant_config})
        return config
