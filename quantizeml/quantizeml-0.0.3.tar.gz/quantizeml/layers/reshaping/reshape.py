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

from ...tensors import FixedPoint


__all__ = ["QuantizedReshape"]


@tf.keras.utils.register_keras_serializable()
class QuantizedReshape(keras.layers.Reshape):
    """A Reshape layer that operates on quantized inputs

    Args:
        target_shape (tuple of ints): Target shape, does not include the samples
            dimension (batch size).
    """

    def call(self, inputs, training=None):
        # raise an error if the inputs are not FixedPoint
        if not isinstance(inputs, FixedPoint):
            raise TypeError(f"QuantizedReshape only accepts FixedPoint inputs.\
                             Receives {type(inputs)} inputs.")
        if tf.rank(inputs.frac_bits) == 1:
            # Different fractional-bits are defined for the last axis, so
            # it must be preserved during the reshape
            tf.assert_equal(self.target_shape[-1], tf.shape(inputs)[-1])
        # Reshape the values
        reshaped_values = super().call(inputs.values)
        # Return a new reshaped FixedPoint
        return FixedPoint(reshaped_values, inputs.frac_bits, inputs.value_bits)
