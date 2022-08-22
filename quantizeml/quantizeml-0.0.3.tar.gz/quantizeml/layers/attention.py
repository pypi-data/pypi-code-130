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
import keras
import tensorflow as tf


from ..tensors import FixedPoint, MAX_BUFFER_BITWIDTH
from .reshaping import QuantizedReshape, QuantizedPermute
from .softmax2 import softmax2, QuantizedSoftmax2
from .layers import deserialize_quant_object, Calibrable


__all__ = ["Attention", "string_to_softmax", "QuantizedAttention"]


def string_to_softmax(s):
    """
    Convert a string to a softmax function.
    Available options are 'softmax' for standard softmax, 'softmax2' for
    softmax2.

    Args:
        s (str): string to convert.

    Returns:
        A softmax function.
    """
    if s == "softmax":
        return tf.nn.softmax
    if s == "softmax2":
        return softmax2

    raise NotImplementedError("softmax should be in ['softmax', 'softmax2']"
                              f" but received {s}.")


@tf.keras.utils.register_keras_serializable()
class Attention(keras.layers.Layer):
    """Dot-product attention layer with configurable softmax.

    Inputs are a tuple of tensors:
    - a query tensor of shape [batch, tokens, hidden],
    - a key tensor of shape [batch, tokens, hidden],
    - a value tensor of shape [batch, tokens, hidden].

    The calculation follows the steps:

    1. Split query, key, value per attention heads

        q, k, v : [batch, tokens, hidden] -> [batch, token, num_heads, dim]

    2. Calculate cross-token scores as a query-key dot product:

        scores = tf.matmul(query, key, transpose_b=True)

        scores : [batch, num_heads, token, token]

    3. Rescale score by dividing by the squared-root of dim.

    4. Use scores to calculate a mask

        mask = softmax(scores)

    5. Combine mask with value

        output = tf.matmul(mask, value)

        output: [batch, num_heads, token, dim]

    6. Merge heads to get back to 2D

        output: [batch, num_heads, token, dim] -> [batch, token, hidden]

    Args:

        num_heads (int): the number of attention heads
        softmax (str, optional): 'softmax' or 'softmax2'. Defaults to 'softmax'

    """

    def __init__(self, num_heads, softmax="softmax", **kwargs):
        super().__init__(**kwargs)
        self.num_heads = num_heads
        self.softmax = softmax
        self.softmax_op = string_to_softmax(self.softmax)

    def build(self, input_shape):
        assert len(input_shape) == 3
        self.hidden_size = input_shape[0][-1]
        if self.hidden_size % self.num_heads != 0:
            raise ValueError(
                f"Embedding dimension = {self.hidden_size} should be divisible"
                f" by number of heads = {self.num_heads}"
            )
        self.dim = self.hidden_size // self.num_heads
        self.scale_rep = 1 / tf.math.sqrt(tf.cast(self.dim, dtype=tf.float32))

    def separate_heads(self, x):
        x = keras.layers.Reshape((-1, self.num_heads, self.dim))(x)
        return keras.layers.Permute((2, 1, 3))(x)

    def call(self, inputs, training=None):
        # Separate 2D embeddings per head to obtain 3D inputs
        query = self.separate_heads(inputs[0])
        key = self.separate_heads(inputs[1])
        value = self.separate_heads(inputs[2])
        # Dot product query and key for each head and pairs of tokens
        score = tf.matmul(query, key, transpose_b=True)
        # Rescale the corresponding score
        scaled_score = score * self.scale_rep
        # Apply the configurable softmax operation
        mask = self.softmax_op(scaled_score, axis=-1)
        # Combine each score with value to obtain new embeddings per tokens
        output = tf.matmul(mask, value)
        # Join heads to get back to 2D embeddings per token
        output = keras.layers.Permute((2, 1, 3))(output)
        output = keras.layers.Reshape((-1, self.hidden_size))(output)
        return output, mask

    def get_config(self):
        config = super().get_config()
        config.update(
            {
                "num_heads": self.num_heads,
                "softmax": self.softmax
            }
        )
        return config


@tf.keras.utils.register_keras_serializable()
class QuantizedAttention(Calibrable, Attention):

    def __init__(self, num_heads, softmax='softmax2', quant_config={}, **kwargs):
        if softmax != 'softmax2':
            raise ValueError(
                "Only softmax2 is supported for quantized attention")
        super().__init__(num_heads=num_heads, softmax=softmax, **kwargs)
        self.quant_config = quant_config

        self.out_quantizer = deserialize_quant_object(
            self.quant_config, "output_quantizer", False)

        # Override softmax operation
        softmax_quant_conf = self.quant_config.get("softmax", {})
        self.softmax_op = QuantizedSoftmax2(
            quant_config=softmax_quant_conf, name="quantized_softmax")
        # Extract other quantization parameters
        self.ss_scale_bitwidth = self.quant_config.get("ss_scale_bitwidth", 4)
        self.score_frac_boost = self.quant_config.get("score_frac_boost", 3)
        self.buffer_bitwidth = self.quant_config.get(
            "buffer_bitwidth", MAX_BUFFER_BITWIDTH) - 1

    def build(self, input_shape):
        super().build(input_shape)
        # Quantize dim reciprocal constant.
        # It is always smaller than 1, so all values will be fractional
        value_bits = self.ss_scale_bitwidth
        self.scale_rep = FixedPoint.quantize(
            self.scale_rep, value_bits, value_bits)

    def separate_heads(self, x):
        x = QuantizedReshape((-1, self.num_heads, self.dim))(x)
        return QuantizedPermute((2, 1, 3))(x)

    def call(self, inputs, training=None):
        if any(not isinstance(x, FixedPoint) for x in inputs):
            # If any of the inputs is not a FixedPoint, raise an error
            raise ValueError("QuantizedAttention only accepts FixedPoint inputs")
        # Separate 2D embeddings per head to obtain 3D inputs
        query = self.separate_heads(inputs[0])
        key = self.separate_heads(inputs[1])
        value = self.separate_heads(inputs[2])
        # Promote and increase fractional precision of query to have a
        # score with better precision
        query = query.promote(self.buffer_bitwidth)
        query = query << self.score_frac_boost
        # Dot product query and key for each head and pairs of tokens
        score = tf.matmul(query, key, transpose_b=True)
        # Rescale the corresponding score
        scaled_score = score * self.scale_rep
        # Apply the configurable softmax operation
        mask = self.softmax_op(scaled_score)
        # Promote mask to make sure we don't overflow
        mask = mask.promote(self.buffer_bitwidth)
        # Combine each score with value to obtain new embeddings per tokens
        output = tf.matmul(mask, value)
        # Join heads to get back to 2D embeddings per token
        output = QuantizedPermute((2, 1, 3))(output)
        output = QuantizedReshape((-1, self.hidden_size))(output)
        # Refine output bitwidth precision if needed
        if self.out_quantizer is not None:
            output = self.out_quantizer(output, training=training)
        return output, mask

    def get_config(self):
        config = super().get_config()
        config["quant_config"] = self.quant_config
        return config
