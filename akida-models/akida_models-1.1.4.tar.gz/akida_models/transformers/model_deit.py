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

from keras.utils.data_utils import get_file

from quantizeml.layers import AddPositionEmbs, ClassToken, Add, ExtractToken
from quantizeml.models import load_model

from .model_vit import CONFIG_TI, CONFIG_S, CONFIG_B, _get_quant_config
from ..imagenet.imagenet_utils import IMAGENET_MEAN, IMAGENET_STD
from ..layer_blocks import norm_to_layer, transformer_block

BASE_WEIGHT_PATH = 'http://data.brainchip.com/models/deit/'


def deit_imagenet(input_shape,
                  num_layers,
                  hidden_size,
                  num_heads,
                  name,
                  mlp_dim,
                  patch_size=16,
                  classes=1000,
                  dropout=0.1,
                  include_top=True,
                  distilled=False,
                  norm='LN',
                  softmax='softmax',
                  act="GeLU"):
    """Build a DeiT model.

    Args:
        input_shape (tuple): image shape tuple
        num_layers (int): the number of transformer layers to use.
        hidden_size (int): the number of filters to use
        num_heads (int): the number of transformer heads
        name (str): the model name
        mlp_dim (int): the number of dimensions for the MLP output in the transformers.
        patch_size (int, optional): the size of each patch (must fit evenly in image size). Defaults
            to 16.
        classes (int, optional): number of classes to classify images into, only to be specified if
            `include_top` is True. Defaults to 1000.
        dropout (float, optional): fraction of the units to drop for dense layers. Defaults to 0.1.
        include_top (bool, optional): Whether to include the final classification layer. If not,
            the output will have dimensions (batch_size, hidden_size). Defaults to True.
        distilled (bool, optional): Build model append a distilled token. Defaults to False.
        norm (str, optional): string that values in ['LN', 'GN1', 'BN', 'LMN'] and that allows to
            choose from LayerNormalization, GroupNormalization(groups=1, ...), BatchNormalization
            or LayerMadNormalization layers respectively in the model. Defaults to 'LN'.
        softmax (str, optional): string with values in ['softmax', 'softmax2']
            that allows to choose between softmax and softmax2 in MHA. Defaults
            to 'softmax'.
        act (str, optional): string that values in ['GeLU', 'ReLUx', 'swish'] and that allows to
            choose from GeLU, ReLUx or swish activation in MLP block. Defaults to 'GeLU'.
    """
    assert ((input_shape[0] % patch_size == 0) and
            (input_shape[1] % patch_size == 0)), "image size must be a multiple of patch_size"

    # Normalize image adding rescaling layer
    x = keras.layers.Input(shape=input_shape)
    scale = tuple(1.0 / 255 / std for std in IMAGENET_STD)
    offset = tuple(-mean / std for mean, std in zip(IMAGENET_MEAN, IMAGENET_STD))
    y = keras.layers.Rescaling(scale=scale, offset=offset, name="Rescale")(x)

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
    if distilled:
        y = ClassToken(name="DistToken")(y)
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
    if distilled:
        yd = ExtractToken(token=1, name="ExtractToken_Dist")(y)
    y = ExtractToken(token=0, name="ExtractToken")(y)
    if include_top:
        y = keras.layers.Dense(classes, name="Head")(y)
        if distilled:
            yd = keras.layers.Dense(classes, name="DistHead")(yd)
    if distilled:
        y = Add(name="Add", average=True)([y, yd])

    # Add distilled flag
    model = keras.models.Model(inputs=x, outputs=y, name=name)
    model.isdistilled = distilled
    return model


def deit_ti16(input_shape=(224, 224, 3), classes=1000, distilled=False, norm='LN',
              softmax='softmax', act='GeLU'):
    """Build DeiT-Tiny.

    Args:
        input_shape (tuple, optional): input shape. Defaults to (224, 224, 3).
        classes (int, optional): number of classes. Defaults to 1000.
        distilled (bool, optional): build model appending a distilled token. Defaults to False.
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
    return deit_imagenet(
        name="deit-tiny",
        input_shape=input_shape,
        classes=classes,
        distilled=distilled,
        norm=norm,
        act=act,
        softmax=softmax,
        **CONFIG_TI,
    )


def bc_deit_ti16(input_shape=(224, 224, 3), classes=1000, distilled=False):
    """Build DeiT-Tiny, changing all LN by LMN, using softmax2 and ReLU8.

    Args:
        input_shape (tuple, optional): input shape. Defaults to (224, 224, 3).
        classes (int, optional): number of classes. Defaults to 1000.
        distilled (bool, optional): build model appending a distilled token. Defaults to False.

    Returns:
        keras.Model: the requested model
    """
    return deit_imagenet(
        name="deit-tiny",
        input_shape=input_shape,
        classes=classes,
        distilled=distilled,
        norm="LMN",
        softmax="softmax2",
        act="ReLU8",
        **CONFIG_TI,
    )


def bc_deit_ti16_imagenet_pretrained():
    """ Helper method to retrieve a `bc_deit_ti16` model that was trained on ImageNet dataset.

    Returns:
        keras.Model, dict: a Keras Model instance and the quantization configuration as a JSON
            formatted dict.
    """
    model_name = 'bc_deit_ti16_224_quant_config_8bit.h5'
    file_hash = '98F6FE42B59ECFE1EF17BFC488C2F4897414E0A15335C0A83817257EFD577823'
    model_path = get_file(fname=model_name,
                          origin=BASE_WEIGHT_PATH + model_name,
                          file_hash=file_hash,
                          cache_subdir='models')
    return load_model(model_path), _get_quant_config()


def bc_deit_dist_ti16_imagenet_pretrained():
    """ Helper method to retrieve a `bc_deit_dist_ti16` model that was trained on ImageNet dataset.

    Returns:
        keras.Model, dict: a Keras Model instance and the quantization configuration as a JSON
            formatted dict.
    """
    model_name = 'bc_deit_dist_ti16_224_quant_config_8bit.h5'
    file_hash = '0B204BA36B11C4158C6AFBFEC8B633742EBD052F33FA285FAB5042B54974AC6A'
    model_path = get_file(fname=model_name,
                          origin=BASE_WEIGHT_PATH + model_name,
                          file_hash=file_hash,
                          cache_subdir='models')
    return load_model(model_path), _get_quant_config()


def deit_s16(input_shape=(224, 224, 3), classes=1000, distilled=False):
    """Build DeiT-Small.

    Args:
        input_shape (tuple, optional): input shape. Defaults to (224, 224, 3).
        classes (int, optional): number of classes. Defaults to 1000.
        distilled (bool, optional): build model appending a distilled token. Defaults to False.

    Returns:
        keras.Model: the requested model
    """
    return deit_imagenet(
        name="deit-small",
        input_shape=input_shape,
        classes=classes,
        distilled=distilled,
        **CONFIG_S,
    )


def deit_b16(input_shape=(224, 224, 3), classes=1000, distilled=False):
    """Build DeiT-B16.

    Args:
        input_shape (tuple, optional): input shape. Defaults to (224, 224, 3).
        classes (int, optional): number of classes. Defaults to 1000.
        distilled (bool, optional): build model appending a distilled token. Defaults to False.

    Returns:
        keras.Model: the requested model
    """
    return deit_imagenet(
        name="deit-base",
        input_shape=input_shape,
        classes=classes,
        distilled=distilled,
        **CONFIG_B,
    )
