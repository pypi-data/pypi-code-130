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
import numpy as np
import tensorflow as tf
import keras

from .layers import deserialize_quant_object, Calibrable
from ..tensors import FixedPoint, MAX_BUFFER_BITWIDTH


__all__ = ["QuantizedGELU", "QuantizedReLU"]


@tf.keras.utils.register_keras_serializable()
class QuantizedGELU(Calibrable, keras.layers.Layer):
    """Quantize the `Gaussian Error Linear Units (GELU)<https://arxiv.org/abs/1606.08415>`_
    activation, following the implementation on `i-BERT <https://arxiv.org/abs/2101.01321>`_.

    To quantize non-linear activation functions, three ways are commonly used:
        1. Dequantize the input, make the activation function in float and then quantize the output.
        2. Store the quantized input in a lookup table, and use it to quantize.
        3. Approximate the activation function with a linear function.

    Follow the explanation given on `i-BERT <https://arxiv.org/abs/2101.01321>`_, in order
    to reduce on-chip memory cost and increase efficient hardware performance, the third way
    is used here.

    The GELU activation function is defined as:
    .. math::
        GELU(x) = 0.5*x*[1 + erf(x/\sqrt(2))]

    Where erf(:math:`x`) is the error function. `i-BERT <https://arxiv.org/abs/2101.01321>`_ shows
    that a degree two polynomial approximation to the erf function would be given by
    .. math::
        L(x) = sgn(x)[a(clip(|x|, max = -b) + b)^2 + 1]

    With :math:`a = -0.2888`, :math:`b = -1.769`, and average error / maximum error of
    :math:`8.2\times10^{-3} / 1.8\times10^{-2}` (respectively), within the range :math:`|x| < 1`.

    Args:
        quant_config (dict): quantization configuration of input/output quantizers.
    """
    unsupported_args = {
        'approximate': True}

    def __init__(self, *args, name="i_gelu", quant_config={}, **kwargs):
        super().__init__(*args, name=name, **kwargs)
        self.quant_config = quant_config
        self.bitwidth = self.quant_config.get(
            "buffer_bitwidth", MAX_BUFFER_BITWIDTH) - 1
        assert self.bitwidth >= 0, "The buffer_bitwidth must be a non-negative integer."

        # All constants are in the range |x| < 2. We only need 2bits for the int part
        # and remove the sign bit.
        value_bits = self.quant_config.get("weight_bitwidth", 10) - 1
        frac_bits = value_bits - 2
        # Coefficients of the degree 2 polynomial, used to approximate erf(x/sqrt(2))
        self._a_int = FixedPoint.quantize(-0.2888, frac_bits, value_bits)
        self._b_int = FixedPoint.quantize(-1.769, frac_bits, value_bits)
        self._c_int = FixedPoint.quantize(1.0, frac_bits, value_bits)
        # Coefficients used in i_gelu function
        self._s2_int = FixedPoint.quantize(1.0 / 1.4142, frac_bits, value_bits)
        self._05_int = FixedPoint.quantize(0.5, frac_bits, value_bits)
        self.out_quantizer = deserialize_quant_object(
            self.quant_config, "output_quantizer", False)

    @property
    def _pol_coeff(self):
        """Return the coefficients of the degree 2 polynomial approximation to the erf function."""
        return self._a_int, self._b_int, self._c_int

    @property
    def _gelu_coeff(self):
        """Return the coefficients needed in i-GELU function."""
        return self._s2_int, self._05_int

    def i_poly(self, q_in, q_a, q_b, q_c):
        """Integer-only Computation of Second-order Polynomial :math:`a*(x + b)^2 + c`

        Args:
            q_in (:obj:`FixedPoint`): an integer quantized input tensor.
            q_a (obj:`FixedPoint`): first coefficient of the polynomial, :math:`q_a = S*a`.
            q_b (obj:`FixedPoint`): second coefficient of the polynomial, :math:`q_b = S*b`.
            q_c (obj:`FixedPoint`): third coefficient of the polynomial, :math:`q_c = S*c`.

        Returns:
            :obj:`FixedPoint`: the y-tensor: :math:`y \approx a(x + b)^2 + c`

        Note:
            ``S`` denotes the quantization scale.
        """
        return (q_in + q_b)**2 * q_a + q_c

    def i_erf(self, q_in):
        """Approximate the error function with a degree two polynomial.

        Args:
            q_in (:obj:`FixedPoint`): an integer quantized input tensor.

        Returns:
            :obj:`FixedPoint`: the y-tensor: :math:`y \approx i_erf(x)`
        """
        # Get the coefficients of the degree 2 polynomial
        q_a, q_b, q_c = self._pol_coeff
        # Compute erf function, as a degree 2 polynomial approximation
        q_in_abs = tf.clip_by_value(q_in.abs(), 0, q_b.abs())
        return self.i_poly(q_in_abs, q_a, q_b, q_c) * q_in.sign

    def i_gelu(self, q_in):
        """Approximate the GELU activation function with a degree two polynomial.

        Args:
            q_in (:obj:`FixedPoint`): an integer quantized input tensor.

        Returns:
            :obj:`FixedPoint`: the y-tensor: :math:`y \approx i_gelu(x)`
        """
        # Get coefficients needed in i_gelu function
        q_s2, q_05 = self._gelu_coeff
        # Compute i_erf function
        q_erf = self.i_erf(q_in * q_s2)
        # Compute i-GELU function
        return (q_erf + 1) * q_05 * q_in

    def call(self, inputs, training=None):
        """i-GELU forward in three steps:
            1. Quantize the inputs (if needed)
            2. Pass inputs through the i-GELU function
            3. Update the new quantization scale

        Args:
            inputs (:obj:`FixedPoint`): the inputs tensor.
            training (bool, optional): the training mode. Defaults to None.

        Returns:
            :obj:`FixedPoint`: float of i-GELU(inputs).
        """
        # raise an error if the inputs are not FixedPoint
        if not isinstance(inputs, FixedPoint):
            raise TypeError(f"QuantizedGeLU only accepts FixedPoint inputs.\
                             Receives {type(inputs)} inputs.")

        # 1. Increase the bitwidth to desired value
        inputs = inputs.promote(self.bitwidth)
        # 2. Approximate the GELU function with i-GELU
        outputs = self.i_gelu(inputs)

        # 3. Update the new quantization scale in output quantizer
        if self.out_quantizer is not None:
            outputs = self.out_quantizer(outputs, training=training)
        return outputs

    def get_config(self):
        config = super().get_config()
        config["quant_config"] = self.quant_config
        return config


@tf.keras.utils.register_keras_serializable()
class QuantizedReLU(Calibrable, keras.layers.Layer):
    """Quantized version of the ReLU activation layer applicable on FixedPoint tensor.
    """
    unsupported_args = {
        'negative_slope': 0,
        'threshold': 0}

    def __init__(self, *args, max_value=6, quant_config={}, **kwargs):
        super().__init__(*args, **kwargs)
        self.quant_config = quant_config

        if max_value is None:
            raise ValueError(
                f"QuantizedRelU layer {self.name} has been initialized with\
                    unsupported None max_value.")
        if isinstance(max_value, np.ndarray):
            self.max_value = int(max_value.item())
        else:
            self.max_value = max_value

        self.out_quantizer = deserialize_quant_object(
            self.quant_config, "output_quantizer", False)

    def call(self, inputs, training=None):
        """ReLU activation function. In other terms:
            1. clip the value between 0 and :attr:`max_value`.
            2. quantize the output if an output_quantizer is set.

        Args:
            inputs (:obj:`FixedPoint` or :obj:`tf.Tensor`): the inputs tensor.
            training (bool, optional): the training mode. Defaults to None.

        Returns:
            :obj:`FixedPoint`: QuantizedReLU outputs.
        """
        # raise an error if the inputs are not FixedPoint
        if not isinstance(inputs, FixedPoint):
            raise TypeError(f"QuantizedReLU only accepts FixedPoint inputs.\
                             Receives {type(inputs)} inputs.")

        outputs = tf.clip_by_value(inputs, 0, self.max_value)
        if self.out_quantizer is not None:
            outputs = self.out_quantizer(outputs, training=training)
        return outputs

    def get_config(self):
        config = super().get_config()
        config.update({"max_value": self.max_value})
        config["quant_config"] = self.quant_config
        return config
