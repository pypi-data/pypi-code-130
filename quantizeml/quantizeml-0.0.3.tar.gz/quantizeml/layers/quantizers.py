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
from contextlib import contextmanager
import tensorflow as tf
import keras.backend as K
from keras.layers import Layer

from ..tensors import QTensor, QFloat, FixedPoint
from .layers import Calibrable


@contextmanager
def disable_partitioner(layer):
    partitioner = None
    try:  # Disable variable partitioning when creating the moving tensors
        if hasattr(layer, "_scope") and layer._scope:
            partitioner = layer._scope.partitioner
            layer._scope.set_partitioner(None)
        yield layer
    finally:  # Restore partitioner
        if partitioner:
            layer._scope.set_partitioner(partitioner)


class Quantizer(Calibrable, Layer):
    """The base class for all quantizers.

    The bitwidth defines the number of quantization levels on which the
    values will be quantized.
    For a quantizer that accepts unsigned values, the maximum quantization
    level is 2 ^ bitwidth - 1.
    For a quantizer that accepts signed values, we lose one bit of precision to
    store the sign, so the minimum/maximum level is -/+ 2 ^ (bitwidth - 1) - 1.
    When the quantizer is signed, the quantization interval is always symmetric
    around zero.
    The quantization is actually performed on absolute values, between 0 and
    max_value, where:
    - max_value is either a scalar (per-tensor quantization), or a vector
      (per-axis quantization),
    - max_value is a static value on inference, and an adaptative value on training
      (updated by the moving average algorithm, based on BatchNormalizationLayer).

    Args:
        bitwidth (int): the quantization bitwidth.
        signed (bool, optional): whether the quantizer expects signed values or unsigned.
            Defaults to True.
        axis (str, optional): reduce across all tensor values ('per-tensor') or keep the
            last axis ('per-axis'). Defaults to 'per-tensor'.
        momentum (float, optional): the momentum for the moving average. Defaults to 0.9.

    Note:
        To get more information about the moving average implementation, see the
        `BatchNormalizationLayer <https://bit.ly/3KcEaUh>`_ class:
    """

    # Follow BatchNormalizationLayer, the base class uses V2 behavior by default.
    # To use V1 behavior, set to False.
    _USE_V2_BEHAVIOR = True

    def __init__(self, bitwidth, signed=True, axis="per-tensor", momentum=0.9, **kwargs):
        assert bitwidth > 1
        self.bitwidth = bitwidth
        self.signed = signed
        self.value_bits = bitwidth - 1 if signed else bitwidth
        self._axis = axis
        self.momentum = momentum
        if not (isinstance(axis, str) and axis in ["per-tensor", "per-axis"]):
            raise ValueError(
                f"Only support reduction 'per-tensor' or 'per-axis'. Given {axis}.")
        super().__init__(**kwargs)

    def build(self, input_shape):
        """Build the layer.

        Args:
            input_shape (list): the shape of input tensor.
        """
        # Convert axis to a list of int
        if self._axis == "per-axis" and len(input_shape) > 1:
            self.axis = list(range(len(input_shape) - 1))
        else:
            self.axis = None

        # Declares the constant/vector that will store the maximum values of the input.
        with disable_partitioner(self):
            self.max_value = self.add_weight(
                name="max_value",
                shape=input_shape[-1] if self.axis is not None else (),
                dtype=tf.float32,
                initializer="ones",
                synchronization=tf.VariableSynchronization.ON_READ,
                trainable=False,
                aggregation=tf.VariableAggregation.MEAN,
                experimental_autocast=False,
            )

    @staticmethod
    def _assign_moving_average(variable, value, momentum, inputs_size):
        """Given a variable, assign a new value to it, using a moving average.
        Function taken of `BatchNormalizationLayer <https://bit.ly/3JUcLGd>`_ code.

        Args:
            variable (:obj:`tensorflow.Variable`): the variable to assign.
            value (:obj:`tensorflow.Tensor`): the new value to assign.
            momentum (float): the momentum for the moving average.
            inputs_size (int): the size of the inputs.

        Returns:
            :obj:`tensorflow.Tensor`: the new value of the variable.
        """

        def calculate_update_delta():
            decay = tf.convert_to_tensor(1.0 - momentum, name="decay")
            if decay.dtype != variable.dtype.base_dtype:
                decay = tf.cast(decay, variable.dtype.base_dtype)
            # Expected match shape
            value_r = tf.reshape(value, tf.shape(variable))
            update_delta = (variable - tf.cast(value_r, variable.dtype)) * decay
            if inputs_size is not None:
                update_delta = tf.where(
                    inputs_size > 0, update_delta, K.zeros_like(update_delta))
            return update_delta

        with K.name_scope("AssignMovingAvg") as scope:
            if tf.compat.v1.executing_eagerly_outside_functions():
                return variable.assign_sub(calculate_update_delta(), name=scope)
            else:
                with tf.compat.v1.colocate_with(variable):
                    return tf.compat.v1.assign_sub(variable, calculate_update_delta(), name=scope)

    @staticmethod
    def _assign_new_value(variable, value):
        """Given a variable, assign a new value to it. Function taken of
        `BatchNormalizationLayer <https://bit.ly/3v0gzll>`_ code.

        Args:
            variable (:obj:`tensorflow.Variable`): the variable to assign.
            value (:obj:`tensorflow.Tensor`): the new value to assign.

        Returns:
            :obj:`tensorflow.Tensor`: the new value of the variable.
        """
        with K.name_scope("AssignNewValue") as scope:
            # Expected match shape
            value_r = tf.reshape(value, tf.shape(variable))
            if tf.compat.v1.executing_eagerly_outside_functions():
                return variable.assign(value_r, name=scope)
            else:
                with tf.compat.v1.colocate_with(variable):
                    return tf.compat.v1.assign(variable, value_r, name=scope)

    @staticmethod
    def _update_weights(inputs, variable, axis, input_batch_size=None, momentum=0.9):
        """Given the inputs tensor, a variable is updated with the maximum reduction of
        the absolute input values. This reduction will be used on moving average algorithm.

        Args:
            inputs (:obj:`tensorflow.Tensor`): the inputs tensor.
            variable (:obj:`tensorflow.Variable`): the variable to assign.
            axis (List[int], int or None): the axis to make the reduction.
            input_batch_size (int, optional): the batch size of the inputs. Defaults to None.
            momentum (float, optional): the momentum for the moving average. Defaults to 0.9.

        Note:
            If ``momentum`` is None, the new value calculated over inputs will overwrite
            the variable.
        """
        # Compute the new value for all weights
        max_value = tf.math.reduce_max(tf.math.abs(inputs), axis)
        if momentum == -1.:
            Quantizer._assign_new_value(variable, max_value)
        else:
            Quantizer._assign_moving_average(
                variable, max_value, momentum, input_batch_size)

    def quantize(self, x):
        """Quantize the input tensor.

        Args:
            x (:obj:`tensorflow.Tensor`): the input tensor.

        Returns:
            :obj:`tensorflow.Tensor`: the quantized tensor.
        """
        raise NotImplementedError

    def call(self, inputs, training=None):
        """Update the weights from moving average, and quantize the inputs in three steps:
            1. Convert the inputs to float values,
            2. Update the weights from moving average, only if calibration is enabled and
            3. Quantize the inputs.

        Args:
            inputs (:obj:`tensorflow.Tensor` or :obj:`QTensor`): the inputs tensor.
            training (bool, optional): the training mode. Defaults to None.

        Returns:
            :obj:`tensorflow.Tensor`: the quantized tensor.
        """
        if isinstance(inputs, QTensor):
            inputs = inputs.to_float()
        if self.calibration:
            # Retrieve information from the inputs and update the weights
            input_batch_size = tf.shape(inputs)[0]
            if tf.reduce_all(tf.math.equal(self.max_value, tf.constant(1.))):
                momentum = tf.constant(-1.)
            else:
                momentum = tf.convert_to_tensor(self.momentum)
            self._update_weights(inputs, self.max_value,
                                 self.axis, input_batch_size, momentum)
        return self.quantize(inputs)

    def get_config(self):
        """Get the config of the layer.

        Returns:
            dict: the config of the layer.
        """
        config = super().get_config()
        config.update({"bitwidth": self.bitwidth})
        config.update({"signed": self.signed})
        config.update({"axis": self._axis})
        config.update({"momentum": self.momentum})
        return config


@tf.keras.utils.register_keras_serializable()
class UniformQuantizer(Quantizer):
    """A trivial uniform quantizer that has only one scale for everything.
    Scale is dynamic (depends on inputs), and it can be read via the scale property.

    Args:
        bitwidth (int): the quantization bitwidth.
        scale_bits (int, optional): the number of bits for the scaling. Defaults to 24.
    """

    def __init__(self, bitwidth, scale_bits=24, **kwargs):
        if not isinstance(bitwidth, int) or bitwidth < 2:
            raise ValueError(
                f"Bitwidth should be an int >= 2, currently {bitwidth}")
        self.scale_bits = scale_bits
        super().__init__(bitwidth, **kwargs)

    def quantize(self, x):
        """Quantize float inputs

        Args:
            x(:obj:`tensorflow.Tensor`): a Tensor of float inputs.

        Returns:
            a QFloat
        """
        if not self.signed:
            x = tf.math.maximum(x, 0)
        float_max = tf.stop_gradient(self.max_value)
        return QFloat.quantize(x, float_max, self.value_bits, self.scale_bits)

    def get_config(self):
        """Get the config of the layer.

        Returns:
            dict: the config of the layer.
        """
        config = super().get_config()
        config.update({"scale_bits": self.scale_bits})
        return config


@tf.keras.utils.register_keras_serializable()
class FixedPointQuantizer(Quantizer):
    """A uniform quantizer that aligns its quantization range to a Power-of-two

    Args:
        bitwidth (int): the quantization bitwidth.
        signed (bool): whether the quantizer expects signed values or unsigned.
    """

    @property
    def int_bits(self):
        # Clamp the max_value to the next power-of-two
        ln_max = tf.math.log(tf.cast(self.max_value, tf.float32))
        log2_max = ln_max / tf.math.log(2.)
        int_bits = tf.cast(tf.math.ceil(log2_max), tf.int32)
        return tf.clip_by_value(int_bits, 0, self.value_bits)

    @property
    def frac_bits(self):
        # Evaluate fractional bits
        return self.value_bits - self.int_bits

    def quantize(self, x):
        """Quantize float inputs

        Args:
            x(:obj:`tensorflow.Tensor`): a Tensor of float inputs.

        Returns:
            a FixedPoint
        """
        frac_bits = tf.stop_gradient(self.frac_bits)
        if not self.signed:
            x = tf.math.maximum(x, 0)
        return FixedPoint.quantize(x, frac_bits, self.value_bits)


@tf.keras.utils.register_keras_serializable()
class Dequantizer(Layer):

    def call(self, inputs, training=None):
        """Convert QTensor inputs to float.

        Args:
            inputs (:obj:`tensorflow.Tensor` or :obj:`QTensor`): the inputs tensor(s).
            training (bool, optional): the training mode. Defaults to None.

        Returns:
            :obj:`tensorflow.Tensor`: the quantized tensor(s).
        """
        def dequantize(x):
            if isinstance(x, QTensor):
                return x.to_float()
            return x

        if isinstance(inputs, (list, tuple)):
            return [dequantize(x) for x in inputs]

        return dequantize(inputs)
