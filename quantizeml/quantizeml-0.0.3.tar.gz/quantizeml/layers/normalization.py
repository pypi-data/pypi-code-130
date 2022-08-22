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
from tensorflow.python.framework import ops

from .layers import deserialize_quant_object, Calibrable
from ..tensors import FixedPoint, reciprocal_lut, MAX_BUFFER_BITWIDTH


__all__ = ["QuantizedLayerNormalization", "LayerMadNormalization"]


@tf.keras.utils.register_keras_serializable()
class LayerMadNormalization(keras.layers.LayerNormalization):
    """Approximates the :obj:`keras.layers.LayerNormalization` (LN), replacing the computation of
    the standard deviation by the mean average deviation (mad).

    Taking into account the complexity of the calculate required in the standard deviation,
    the LayerMadNormalization (LMN) is intended to replace the :math:`std(x)` by :math:`mad(x)`,
    defined as:

    .. math::
        mad(x) = |x - mean(x)|

    Then, the equation of the layer is defined as:

    .. math::
        LMN(x) = \gamma(x - mean(x))/mad(x) + \beta

    .. note::
        A tuning step in the switching procedure between the LN to LMN layer will be required
        to find the :math:`(\gamma, \beta)` parameters that match the standard deviation changes.
    """

    def _moments(self, inputs, axes, *args, name=None, **kwargs):
        """Compute the mean and mean absolute deviation (mad) power of two.

        Args:
            inputs (:obj:`tensorflow.Tensor`): input tensor.
            axes (array of ints): axes along which to compute mean and mad.
            name (str, optional): name used to scope the operations that compute the moments.
                Defaults to None.
            *args, **kwargs (dict, optional): additional arguments of :func:`tf.math.reduce_mean`.

        Returns:
            :obj:`tensorflow.Tensor`, :obj:`tensorflow.Tensor`: mean around the axis and
                mean absolute deviation (mad) power of two around the axis.
        """
        # Compute the mean and mad
        with ops.name_scope(name, "_moments", [inputs, axes]):
            mean = tf.math.reduce_mean(
                inputs, axes, *args, **kwargs, name="mean")
            mad = tf.math.reduce_mean(tf.math.abs(
                inputs - mean), axes, *args, **kwargs, name="mad")
        return mean, mad ** 2

    def call(self, inputs, training=None):
        """Use the same call as the parent, changing tf.nn.moments instead of self._moments."""
        # Compute the axis along which to reduce the mean / variance
        input_shape = inputs.shape
        ndims = len(input_shape)

        # Broadcasting only necessary for norm when the axis is not just the last dimension
        broadcast_shape = [1] * ndims
        for dim in self.axis:
            broadcast_shape[dim] = input_shape.dims[dim].value

        def _broadcast(v):
            if (v is not None and len(v.shape) != ndims and self.axis != [ndims - 1]):
                return tf.reshape(v, broadcast_shape)
            return v

        input_dtype = inputs.dtype
        if input_dtype in ('float16', 'bfloat16') and self.dtype == 'float32':
            # If mixed precision is used, cast inputs to float32 so that this is at
            # least as numerically stable as the fused version.
            inputs = tf.cast(inputs, 'float32')

        # Calculate the moments on the last axis (layer activations).
        mean, variance = self._moments(inputs, self.axis, keepdims=True)
        scale, offset = _broadcast(self.gamma), _broadcast(self.beta)

        # Compute layer normalization using the batch_normalization function.
        outputs = tf.nn.batch_normalization(
            inputs,
            mean,
            variance,
            offset=offset,
            scale=scale,
            variance_epsilon=self.epsilon)
        outputs = tf.cast(outputs, input_dtype)

        # If some components of the shape got lost due to adjustments, fix that.
        outputs.set_shape(input_shape)

        return outputs


@tf.keras.utils.register_keras_serializable()
class QuantizedLayerNormalization(Calibrable, LayerMadNormalization):

    def __init__(self, *args, quant_config={}, **kwargs):
        super().__init__(*args, **kwargs)
        self.quant_config = quant_config
        self.buf_bits = self.quant_config.get(
            "buffer_bitwidth", MAX_BUFFER_BITWIDTH) - 1
        self.out_quantizer = deserialize_quant_object(
            self.quant_config, "output_quantizer", False)
        self.buffer_bitwidth = self.quant_config.get(
            "buffer_bitwidth", MAX_BUFFER_BITWIDTH) - 1
        self.mad_rec_frac_bits = self.quant_config.get("mad_rec_frac_bits", 16)
        assert self.buffer_bitwidth > 0, "The buffer_bitwidth must be a strictly positive integer."
        assert self.mad_rec_frac_bits >= 0, "The mad_rec_frac_bits must be a non-negative integer."
        self.gamma_quantizer = deserialize_quant_object(
            self.quant_config, "gamma_quantizer", True)
        self.beta_quantizer = deserialize_quant_object(
            self.quant_config, "beta_quantizer", True)
        self.mad_quantizer = deserialize_quant_object(
            self.quant_config, "mad_quantizer", True)

    def call(self, inputs, training=None):
        """The quantized version of the LayerNormalization with Integer-only operations.

            This normalizes the input tensor then returns a quantized output.

            inputs (:obj:`FixedPoint`): the inputs tensor.
            training (bool, optional): the training mode. Defaults to None.

            Returns:
                :obj:`FixedPoint`: output tensor.
        """
        # raise an error if the inputs are not FixedPoint
        if not isinstance(inputs, FixedPoint):
            raise TypeError(f"QuantizedLayerNormalization only accepts FixedPoint\
                              inputs. Receives {type(inputs)} inputs.")

        nb_channels = inputs.shape[-1]

        # Increase the value_bits of inputs
        inputs = inputs.promote(self.buffer_bitwidth)

        # Compute the Mean of the inputs
        sum_x = tf.math.reduce_sum(inputs, self.axis, keepdims=True)
        mean_x = sum_x // nb_channels

        # Compute the Absolute Deviation (MAD)
        x_shifted = inputs - mean_x
        mad_sum = tf.math.reduce_sum(
            x_shifted.abs(), self.axis, keepdims=True, name="mad")
        mad = mad_sum // nb_channels

        mad = self.mad_quantizer(mad, training=training)

        # Convert the learnable parameters gamma and beta in FixedPoint
        gamma = self.gamma_quantizer(self.gamma, training=training)
        beta = self.beta_quantizer(self.beta, training=training)

        # Find the FixedPoint Reciprocal of the FixedPoint mad
        mad_inv = reciprocal_lut(
            mad, self.mad_rec_frac_bits, self.buffer_bitwidth)

        # In FixedPoint arithmetic the value/frac bits of an operation result are controlled
        # by the left term. In the multiplication below, we want to keep the higher
        # frac_bits value, which is owned by "mad_inv" variable. Hence "mad_inv" should
        # be the left term.
        outputs = mad_inv * gamma * x_shifted + beta
        outputs.values.set_shape(inputs.shape)

        # If no quantizer output is provided return the FixedPoint output tensor directly
        if self.out_quantizer is None:
            return outputs

        return self.out_quantizer(outputs, training=training)

    def get_config(self):
        config = super().get_config()
        config["quant_config"] = self.quant_config
        return config
