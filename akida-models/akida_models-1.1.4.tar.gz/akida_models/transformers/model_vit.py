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
ViT model definition.
Inspired from https://github.com/faustomorales/vit-keras/blob/master/vit_keras/vit.py.
"""

import keras
import json
import warnings
import numpy as np
import scipy as sp
import typing_extensions as tx

from keras.utils.data_utils import get_file

from quantizeml.layers import AddPositionEmbs, ClassToken, ExtractToken
from quantizeml.models import load_model

from ..layer_blocks import transformer_block, norm_to_layer

BASE_WEIGHT_PATH = 'http://data.brainchip.com/models/vit/'


ConfigDict = tx.TypedDict(
    "ConfigDict",
    {
        "dropout": float,
        "mlp_dim": int,
        "num_heads": int,
        "num_layers": int,
        "hidden_size": int,
    },
)

CONFIG_TI: ConfigDict = {
    "dropout": 0.0,
    "mlp_dim": 768,
    "num_heads": 3,
    "num_layers": 12,
    "hidden_size": 192,
}

CONFIG_S: ConfigDict = {
    "dropout": 0.1,
    "mlp_dim": 1536,
    "num_heads": 6,
    "num_layers": 12,
    "hidden_size": 384,
}

CONFIG_B: ConfigDict = {
    "dropout": 0.1,
    "mlp_dim": 3072,
    "num_heads": 12,
    "num_layers": 12,
    "hidden_size": 768,
}

CONFIG_L: ConfigDict = {
    "dropout": 0.1,
    "mlp_dim": 4096,
    "num_heads": 16,
    "num_layers": 24,
    "hidden_size": 1024,
}


def apply_embedding_weights(target_layer, source_weights, num_x_patches, num_y_patches,
                            num_tokens=1):
    """Apply embedding weights to a target layer.

    Args:
        target_layer (:obj:`keras.Layer`): The target layer to which weights will be applied.
        source_weights (list of :obj:`np.array`): The source weights.
        num_x_patches (int, optional): Number of x-patches in embedding layer.
        num_y_patches (int, optional): Number of y-patches in embedding layer.
        num_tokens (int, optional): Number of tokens. Defaults to 1.
    """
    assert isinstance(source_weights, list), "source_weights must be a list of numpy arrays"
    expected_shape = target_layer.weights[0].shape
    if expected_shape != source_weights[0].shape:
        token, grid = source_weights[0][0, :num_tokens], source_weights[0][0, num_tokens:]
        sin = int(np.sqrt(grid.shape[0]))
        sout_x = num_x_patches
        sout_y = num_y_patches
        warnings.warn(
            "Resizing position embeddings from " f"{sin}, {sin} to {sout_x}, {sout_y}",
            UserWarning,
        )
        zoom = (sout_y / sin, sout_x / sin, 1)
        grid = sp.ndimage.zoom(grid.reshape(sin, sin, -1), zoom, order=1).reshape(
            sout_x * sout_y, -1
        )
        new_weights = np.concatenate([token, grid], axis=0)[np.newaxis]
        source_weights = [new_weights] + source_weights[1:]
    target_layer.set_weights(source_weights)


def vit_imagenet(input_shape,
                 patch_size,
                 num_layers,
                 hidden_size,
                 num_heads,
                 name,
                 mlp_dim,
                 classes=1000,
                 dropout=0.1,
                 include_top=True,
                 norm='LN',
                 softmax='softmax',
                 act="GeLU"):
    """Build a ViT model.

    Args:
        input_shape (tuple): image shape tuple
        patch_size (int): the size of each patch (must fit evenly in image size)
        num_layers (int): the number of transformer layers to use.
        hidden_size (int): the number of filters to use
        num_heads (int): the number of transformer heads
        name (str): the model name
        mlp_dim (int): the number of dimensions for the MLP output in the transformers.
        classes (int, optional): number of classes to classify images into, only to be specified if
            `include_top` is True. Defaults to 1000.
        dropout (float, optional): fraction of the units to drop for dense layers. Defaults to 0.1.
        include_top (bool, optional): whether to include the final classification layer. If not,
            the output will have dimensions (batch_size, hidden_size). Defaults to True.
        norm (str, optional): string that values in ['LN', 'GN1', 'BN', 'LMN'] and that allows to
            choose from LayerNormalization, GroupNormalization(groups=1, ...), BatchNormalization
            or LayerMadNormalization layers respectively in the model. Defaults to 'LN'.
        softmax (str, optional): string with values in ['softmax', 'softmax2']
            that allows to choose between softmax and softmax2 in MHA. Defaults
            to 'softmax'.
        act (str, optional): string that values in ['GeLU', 'ReLUx', 'swish'] and that allows to
            choose from GeLU, ReLUx or swish activation in MLP block. Defaults to 'GeLU'.
    """
    assert (input_shape[0] % patch_size == 0) and (
        input_shape[1] % patch_size == 0), "image size must be a multiple of patch_size"

    # Normalize image adding rescaling layer
    x = keras.layers.Input(shape=input_shape)
    y = keras.layers.Rescaling(1 / 127.5, -1, name="Rescale")(x)

    # Build model
    y = keras.layers.Conv2D(
        filters=hidden_size,
        kernel_size=patch_size,
        strides=patch_size,
        padding="valid",
        name="Embedding",
        kernel_initializer=keras.initializers.TruncatedNormal(stddev=0.02),
        bias_initializer="zeros",
    )(y)
    y = keras.layers.Reshape((y.shape[1] * y.shape[2], hidden_size))(y)
    y = ClassToken(name="ClassToken")(y)
    y = AddPositionEmbs(name="Transformer/PosEmbed")(y)
    for n in range(num_layers):
        y, _ = transformer_block(
            y,
            num_heads=num_heads,
            hidden_size=hidden_size,
            mlp_dim=mlp_dim,
            dropout=dropout,
            name=f"Transformer/EncoderBlock_{n}",
            norm=norm,
            softmax=softmax,
            mlp_act=act,
        )
    y = norm_to_layer(norm)(epsilon=1e-6, name="Transformer/EncoderNorm")(y)
    y = ExtractToken(token=0, name="ExtractToken")(y)
    if include_top:
        y = keras.layers.Dense(classes, name="Head")(y)
    return keras.models.Model(inputs=x, outputs=y, name=name)


def vit_ti16(input_shape=(224, 224, 3), classes=1000, norm='LN', softmax='softmax', act='GeLU'):
    """Build ViT-Tiny. All arguments passed to vit_imagenet.

    Args:
        input_shape (tuple, optional): input shape. Defaults to (224, 224, 3).
        classes (int, optional): number of classes. Defaults to 1000.
        norm (str, optional): string that values in ['LN', 'GN1', 'BN', 'LMN'] and that allows to
            choose from LayerNormalization, GroupNormalization(groups=1, ...), BatchNormalization
            or LayerMadNormalization layers respectively in the model. Defaults to 'LN'.
        softmax (str, optional): string with values in ['softmax', 'softmax2'] that allows to choose
            between softmax and softmax2 in attention block. Defaults to 'softmax'.
        act (str, optional): string that values in ['GeLU', 'ReLUx', 'swish'] and that allows to
            choose from GeLU, ReLUx or swish activation inside MLP. Defaults to 'GeLU'.

    Returns:
        keras.Model: the requested model
    """
    return vit_imagenet(
        name="vit-tiny",
        patch_size=16,
        input_shape=input_shape,
        classes=classes,
        norm=norm,
        act=act,
        softmax=softmax,
        **CONFIG_TI
    )


def bc_vit_ti16(input_shape=(224, 224, 3), classes=1000):
    """Build ViT-Tiny, changing all LN by LMN, using softmax2 and ReLU8.

    Args:
        input_shape (tuple, optional): input shape. Defaults to (224, 224, 3).
        classes (int, optional): number of classes. Defaults to 1000.

    Returns:
        keras.Model: the requested model
    """
    return vit_imagenet(
        name="vit-tiny",
        patch_size=16,
        input_shape=input_shape,
        classes=classes,
        norm="LMN",
        softmax="softmax2",
        act="ReLU8",
        **CONFIG_TI
    )


def _get_quant_config():
    """ Retrieves the quantization configuration JSON file from the dataserver.

    Returns:
        dict: the JSON formatted configuration
    """
    file_name = 'quant_config_8bit.json'
    file_hash = '9234af142ae82a9d07fdb2ef7153e0ba4ae4ec34e7c03b2b5c4b29a0f9f09811'
    config_path = get_file(fname=file_name,
                           origin=BASE_WEIGHT_PATH + file_name,
                           file_hash=file_hash,
                           cache_subdir='models')
    with open(config_path) as f:
        quant_config = json.load(f)
    return quant_config


def bc_vit_ti16_imagenet_pretrained():
    """ Helper method to retrieve a `bc_vit_ti16` model that was trained on ImageNet dataset.

    Returns:
        keras.Model, dict: a Keras Model instance and the quantization configuration as a JSON
            formatted dict.
    """
    model_name = 'bc_vit_ti16_224_quant_config_8bit.h5'
    file_hash = '5fffa696cfb052c6cf6f92426f64fb4397f4a8198c995c81365ec66756db0b4d'
    model_path = get_file(fname=model_name,
                          origin=BASE_WEIGHT_PATH + model_name,
                          file_hash=file_hash,
                          cache_subdir='models')
    return load_model(model_path), _get_quant_config()


def vit_s16(input_shape=(224, 224, 3), classes=1000):
    """Build ViT-Small.

    Args:
        input_shape (tuple, optional): input shape. Defaults to (224, 224, 3).
        classes (int, optional): number of classes. Defaults to 1000.

    Returns:
        keras.Model: the requested model
    """
    return vit_imagenet(
        name="vit-s16",
        patch_size=16,
        input_shape=input_shape,
        classes=classes,
        **CONFIG_S
    )


def vit_s32(input_shape=(224, 224, 3), classes=1000):
    """Build ViT-Small.

    Args:
        input_shape (tuple, optional): input shape. Defaults to (224, 224, 3).
        classes (int, optional): number of classes. Defaults to 1000.

    Returns:
        keras.Model: the requested model
    """
    return vit_imagenet(
        name="vit-s32",
        patch_size=32,
        input_shape=input_shape,
        classes=classes,
        **CONFIG_S
    )


def vit_b16(input_shape=(224, 224, 3), classes=1000):
    """Build ViT-B16.

    Args:
        input_shape (tuple, optional): input shape. Defaults to (224, 224, 3).
        classes (int, optional): number of classes. Defaults to 1000.

    Returns:
        keras.Model: the requested model
    """
    return vit_imagenet(
        name="vit-b16",
        patch_size=16,
        input_shape=input_shape,
        classes=classes,
        **CONFIG_B
    )


def vit_b32(input_shape=(224, 224, 3), classes=1000):
    """Build ViT-B32.

    Args:
        input_shape (tuple, optional): input shape. Defaults to (224, 224, 3).
        classes (int, optional): number of classes. Defaults to 1000.

    Returns:
        keras.Model: the requested model
    """
    return vit_imagenet(
        name="vit-b32",
        patch_size=32,
        input_shape=input_shape,
        classes=classes,
        **CONFIG_B
    )


def vit_l16(input_shape=(384, 384, 3), classes=1000):
    """Build ViT-L16.

    Args:
        input_shape (tuple, optional): input shape. Defaults to (384, 384, 3).
        classes (int, optional): number of classes. Defaults to 1000.

    Returns:
        keras.Model: the requested model
    """
    return vit_imagenet(
        name="vit-l16",
        patch_size=16,
        input_shape=input_shape,
        classes=classes,
        **CONFIG_L
    )


def vit_l32(input_shape=(384, 384, 3), classes=1000):
    """Build ViT-L32.

    Args:
        input_shape (tuple, optional): input shape. Defaults to (384, 384, 3).
        classes (int, optional): number of classes. Defaults to 1000.

    Returns:
        keras.Model: the requested model
    """
    return vit_imagenet(
        name="vit-l32",
        patch_size=32,
        input_shape=input_shape,
        classes=classes,
        **CONFIG_L
    )
