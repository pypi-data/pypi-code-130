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
from keras.layers import Conv2D
from .layers import deserialize_quant_object, Calibrable
from ..tensors import FixedPoint, MAX_BUFFER_BITWIDTH


__all__ = ["QuantizedConv2D"]


@tf.keras.utils.register_keras_serializable()
class QuantizedConv2D(Calibrable, Conv2D):
    """A convolutional layer that operates on quantized inputs and weights

    Args:
        quant_config (dict, optional): the serialized quantization configuration.
            Defaults to empty configuration.
        padding_value (:obj:`FixedPoint`, :obj:`tf.Tensor`, optional): the value
            used when padding for the 'same' convolution type. If None,
            zero-padding is used. Defaults to None.
    """

    # The padding_value frac_bits for the 'same' convolution type when we use
    # a tf.Tensor for this parameter.
    _PADDING_FRAC_BITS = 1

    def __init__(self, *args, padding_value=None, quant_config={}, **kwargs):
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
        if padding_value is not None:
            # Raise an error if the padding value is not FixedPoint or tf.Tensor
            if not isinstance(padding_value, (FixedPoint, tf.Tensor)):
                raise TypeError(f"QuantizedConv2D only accepts FixedPoint or\
                                tf.Tensor for padding value. Receives\
                                {type(padding_value)} padding_value.")
            if isinstance(padding_value, tf.Tensor):
                padding_value = FixedPoint.quantize(padding_value,
                                                    self._PADDING_FRAC_BITS,
                                                    self.buffer_bitwidth)
            # Raise an error if the padding value is not a scalar
            if tf.size(padding_value.values) != 1:
                raise ValueError(f"The padding value must be a scalar. Receives\
                                 {padding_value}.")
            padding_value = padding_value.promote(self.buffer_bitwidth)
        # _padding_value is a private member because value controls are operated
        # in the constructor.
        self._padding_value = padding_value

    def _apply_padding(self, inputs, strides, kernel_size, padding_value):
        """Apply "SAME" padding to the inputs

        Args:
            inputs (:obj:`FixedPoint`): the inputs tensor.
            strides (tuple): the strides tuple.
            kernel_size (int): the kernel size.
            padding_value (:obj:`FixedPoint`): the padding value to apply.

        Returns:
            :obj:`FixedPoint`: inputs with padding applied.
        """
        _, h, w, _ = inputs.shape
        filter_width = kernel_size[0]
        filter_height = kernel_size[1]
        if h % strides[0] == 0:
            pad_along_height = max(filter_height - strides[0], 0)
        else:
            pad_along_height = max(filter_height - (h % strides[0]), 0)
        if w % strides[1] == 0:
            pad_along_width = max(filter_width - strides[1], 0)
        else:
            pad_along_width = max(filter_width - (w % strides[1]), 0)
        pad_top = pad_along_height // 2
        pad_bottom = pad_along_height - pad_top
        pad_left = pad_along_width // 2
        pad_right = pad_along_width - pad_left
        padding = [[0, 0], [pad_top, pad_bottom], [pad_left, pad_right], [0, 0]]

        # Set the same scale factor as inputs
        padding_value, _ = padding_value.align(inputs)

        input_padding = tf.pad(inputs.values,
                               padding,
                               "CONSTANT",
                               padding_value.values)

        # Return a new FixedPoint
        return FixedPoint(input_padding, inputs.frac_bits, inputs.value_bits)

    def call(self, inputs, training=None):
        # raise an error if the inputs are not FixedPoint or tf.Tensor
        if not isinstance(inputs, (FixedPoint, tf.Tensor)):
            raise TypeError(f"QuantizedConv2D only accepts FixedPoint or tf.Tensor\
                              inputs. Receives {type(inputs)} inputs.")

        # Quantize the weights
        kernel = self.weight_quantizer(self.kernel, training)

        if isinstance(inputs, tf.Tensor):
            # Assume the inputs are integer stored as float, which is the only tf.Tensor
            # inputs that are allowed
            inputs = FixedPoint.quantize(inputs, 0, 8)

        inputs = inputs.promote(self.buffer_bitwidth)

        # We need a custom padding for specifics padding values
        if self.padding == "same" and self._padding_value is not None:
            # Note that we use the custom padding with a padding value to 0.
            inputs = self._apply_padding(inputs,
                                         list(self.strides),
                                         (kernel.shape[1], kernel.shape[0]),
                                         self._padding_value)
            # Padding is already applied
            self.padding = 'valid'

        outputs = self.convolution_op(inputs, kernel)

        if self.use_bias:
            bias = self.bias_quantizer(self.bias, training)
            outputs = tf.add(outputs, bias)

        if self.out_quantizer is not None:
            outputs = self.out_quantizer(outputs, training)
        return outputs

    def get_config(self):
        config = super().get_config()
        config["padding_value"] = self._padding_value
        config["quant_config"] = self.quant_config
        return config
