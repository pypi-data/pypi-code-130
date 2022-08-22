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
Common utility methods used in quantization models.
"""

import os
import tensorflow_addons as tfa
from keras.models import clone_model, load_model as kload_model, Model

from quantizeml.layers.quantizers import Quantizer, Dequantizer

from ..layers import Calibrable

__all__ = ['load_model', 'deep_clone_model', 'set_calibrate',
           'insert_layer', 'add_shift_info_to_model']


def load_model(model_path, custom_layers={}, compile_model=True):
    """Loads a model with Vision Transformer custom layers.

    Args:
        model_path (str): path of the model to load
        custom_layers (dict, optional): custom layers to add to the model. Defaults to {}.
        compile_model (bool, optional): whether to compile the model. Defaults to True.

    Returns:
        :class:`keras.models.Model`: the loaded model
    """
    # Given that all layers were imported in __init__.py, they are registered.
    # Therefore, we just need append GroupNormalization in the custom layers.
    custom_layers.update({'GroupNormalization': tfa.layers.GroupNormalization})
    return kload_model(model_path, custom_objects=custom_layers, compile=compile_model)


def _deep_copy_variables(src_model, dst_model):
    """ Copy variables from the source model to the destination model.

    Args:
        src_model (keras.Model): the source model
        dst_model (keras.Model): the destination model
    """
    def _assign_variables(src_layer, dst_layer):
        for dst_v in dst_layer.variables:
            for src_v in src_layer.variables:
                if dst_v.name == src_v.name:
                    dst_v.assign(src_v)
                    break

    for layer in src_model.layers:
        new_layer = dst_model.get_layer(layer.name)
        _assign_variables(layer, new_layer)


def deep_clone_model(model, *args, **kwargs):
    """Clone a model, assign variable to variable. Useful when a clone function is used,
    and new layers have not the same number of parameters as the original layer.

    Args:
        model (:class:`keras.models.Model`): model to be cloned
        args, kwargs (optional): arguments pass to :func:`keras.models.clone_model` function

    Returns:
        :class:`keras.models.Model`: the cloned model
    """
    new_model = clone_model(model, *args, **kwargs)
    _deep_copy_variables(model, new_model)
    return new_model


def set_calibrate(model, value):
    """Enable or disable calibration for all layers in a model.

    Args:
        model (:class:`keras.models.Model`): model to be calibrated
        value (bool): True to enable calibration, False to disable it
    """
    for layer in model.layers:
        if isinstance(layer, Calibrable):
            layer.calibration = value


def insert_layer(model, target_layer_name, new_layer):
    """ Inserts the given layer in the model before or after the layer with the name
    target_layer_name depending on the type of new_layer.

    Note that new_layer type is restricted to (Quantizer, Dequantizer) and a Quantizer will be added
    before new_layer while a Dequantizer will be added after

    Args:
        model (keras.Model): the model to update
        target_layer_name (str): name of the layer after which to insert a layer
        new_layer (keras.Layer): layer to insert

    Raises:
        ValueError: when target_layer_name is not found in model or new_layer is not in (Quantizer,
            Dequantizer)

    Returns:
        keras.Model: the new model
    """
    # Check that the model has a layer with then given target_layer_name
    if not any(ly.name == target_layer_name for ly in model.layers):
        raise ValueError(f'{target_layer_name} not found in model.')

    # Check added layer type
    if not isinstance(new_layer, (Quantizer, Dequantizer)):
        raise ValueError(f'Inserted layer must be of type Quantizer or Dequantizer, \
                        received {type(new_layer)}.')

    # Create a clone model to prevent messing with the original model
    clone_model = deep_clone_model(model)

    # Auxiliary dictionary to describe the network graph
    network_dict = {'input_layers_of': {}, 'new_output_tensor_of': {}}

    # Set the input layers of each layer
    for layer in clone_model.layers:
        for node in layer._outbound_nodes:
            layer_name = node.outbound_layer.name
            if layer_name not in network_dict['input_layers_of']:
                network_dict['input_layers_of'].update({layer_name: [layer.name]})
            else:
                network_dict['input_layers_of'][layer_name].append(layer.name)

    # Set the output tensor of the input layer
    network_dict['new_output_tensor_of'].update({clone_model.layers[0].name: clone_model.input})

    # Iterate over all layers after the input
    model_outputs = []
    insert_before = isinstance(new_layer, Quantizer)
    for layer in clone_model.layers[1:]:
        # Determine input tensors
        layer_input = [network_dict['new_output_tensor_of'][layer_aux]
                       for layer_aux in network_dict['input_layers_of'][layer.name]]
        if len(layer_input) == 1:
            layer_input = layer_input[0]

        # Insert layer if name matches the given layer name
        if layer.name == target_layer_name:
            if insert_before:
                # Apply new layer then current layer
                x = new_layer(layer_input)
                x = layer(x)
            else:
                # Apply current layer then new layer
                x = layer(layer_input)
                x = new_layer(x)
        else:
            x = layer(layer_input)

        # Set new output tensor (the original one, or the one of the inserted layer)
        network_dict['new_output_tensor_of'].update({layer.name: x})

        # Save tensor in output list if it is output in initial model
        if layer.name in clone_model.output_names:
            model_outputs.append(x)

    new_model = Model(inputs=clone_model.inputs, outputs=model_outputs)
    _deep_copy_variables(model, new_model)
    return new_model


def add_shift_info_to_model(src_model_path, dst_model_path):
    """Adds shift information support to a model.

    Args:
        src_model_path (str): path of the model to update
        dst_model_path (str): path of the model to write
    """
    # Make sure the src model is loaded without shift info
    os.environ["STORE_SHIFT_INFO"] = "0"
    print(f"Loading {src_model_path}... ", end="")
    model = load_model(src_model_path)
    print("Done")
    print("Cloning with shift info support... ", end="")
    # when setting STORE_SHIFT_INFO to 1, the model is cloned with shift info
    # support
    os.environ["STORE_SHIFT_INFO"] = "1"
    new_model = deep_clone_model(model)
    print("Done")
    print("Saving... ", end="")
    new_model.save(dst_model_path)
    print("Done")
