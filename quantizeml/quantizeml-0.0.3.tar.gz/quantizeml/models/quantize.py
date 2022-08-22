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

import re
import warnings

from keras import Model

from .utils import deep_clone_model
from ..layers import (QuantizedDense, QuantizedLayerNormalization, QuantizedAddPositionEmbs,
                      QuantizedClassToken, QuantizedGELU, QuantizedReLU, QuantizedAdd, QDropout,
                      QuantizedReshape, QuantizedAttention, QuantizedConv2D, QuantizedMaxPool2D,
                      QuantizedGlobalAveragePooling2D, QuantizedExtractToken, Dequantizer,
                      Quantizer, QuantizedSeparableConv2D, QuantizedFlatten)

# Mapper to match float layer with its quantized version
CUSTOM_QLAYERS = {
    "Conv2D": QuantizedConv2D, "Dense": QuantizedDense, "Add": QuantizedAdd,
    "AddPositionEmbs": QuantizedAddPositionEmbs, "ClassToken": QuantizedClassToken,
    "GELU": QuantizedGELU, "ReLU": QuantizedReLU, "Dropout": QDropout,
    "LayerMadNormalization": QuantizedLayerNormalization, "Reshape": QuantizedReshape,
    "Attention": QuantizedAttention, 'MaxPooling2D': QuantizedMaxPool2D,
    'GlobalAveragePooling2D': QuantizedGlobalAveragePooling2D,
    "ExtractToken": QuantizedExtractToken, "SeparableConv2D": QuantizedSeparableConv2D,
    "Flatten": QuantizedFlatten
}


def quantize(model, q_config, add_dequantizer=True):
    """Quantizes the model using the provided configuration.

    Applying the quantization configuration is done in two steps, giving priority to the first:

    1. Match the quantization configuration from the layer name, as long as the final part of its
       name matches with the configuration key.
       Example: To quantize all "Transformer/EncoderBlock_x/MlpBlock/activation" layers, a
       configuration with the key "activation" or "MlpBlock/activation" will be enough. This allows
       the possibility to have a specific configuration for the activation function of block 5 using
       the "Transformer/EncoderBlock_5/MlpBlock/activation" key.

       Notes:
            * If configuration for all blocks are not defined, a global configuration is required.
            * To avoid ambiguity, the key with the most details in terms of hierarchy should be
              selected, e.g. "activation" key in the quantization configuration will be enough to
              quantize all "activation" layers. However, if it is required to define a different
              configuration in all MLP blocks activations, configuration key should be
              "MlpBlock/activation" instead.

    2. Match the quantization configuration from the layer name, as long as the format
       '.../ParentLayer<_i>/SubParentLayer<_j>/.../Layer<_k>' matches with layer.name, where {i, j,
       k} are optional integers. Example: "EncoderBlock/add" key will quantize all layers ending
       with the format "EncoderBlock_i/add_j" ("EncoderBlock_0/add_0", "EncoderBlock_0/add_1",
       "EncoderBlock_1/add_0", "EncoderBlock_1/add_1", ...).

        Note:
            The configuration priority in this case is defined by the number of hierarchical terms
            and the detail in subindices from the end to the beginning of the key name. That is
            "EncoderBlock/add_0" will have priority over "EncoderBlock/add" and
            "EncoderBlock_0/add". The "EncoderBlock_0/add_0" case is covered by the previous point.

    Args:
        model (keras.Model): the model to quantize
        q_config (dict): quantization configuration
        add_dequantizer (bool, optional): allows to convert output to float. Defaults to True.

    Returns:
        keras.Model: the quantized model
    """
    # Add "/" at the beginning of the names, to avoid ambiguity (e.g. "Dense" and "DropoutDense")
    q_config = {key if key[0] == "/" else "/" + key: value for key, value in q_config.items()}

    # This iterates through the <key, config> in the JSON, and creates a regexp based on the key.
    # The regexp is built by:
    #   - identifying items with the '/' separator,
    #   - replace trailing <_N> in each item by a matching pattern,
    #   - concatenate back items matching patterns.
    q_config_regex = {re.compile("/" + "(?:|_[\d]+)/".join(key[1:].split('/')) + "(?:|_[\d]+)$"):
                      (key[1:], obj) for key, obj in q_config.items()}

    def _replace_layer(layer):
        config = layer.get_config()

        # Function to handle unsupported arguments in config
        def pop_unsupported_args(class_type):
            for arg, default_value in getattr(class_type, "unsupported_args", {}).items():
                if (arg in config and config[arg] != default_value):
                    raise RuntimeError(
                        f"Argument '{arg}' in layer '{layer.name}' is only "
                        f"supported with default value '{default_value}'. "
                        f"Receives '{config[arg]}'.")
                config.pop(arg, None)

        # Function that return a quantized layer given its float version
        def get_quantize_layer(layer, quantize_config={}):
            """Quantize float layer in three steps:
                - first, we get its quantized version,
                - second, remove unsupported arguments,
                - then, we return the quantized layer with config updated
            """
            class_name = layer.__class__.__name__
            # 1.1 Check if qlayer exists in custom layers
            if class_name in CUSTOM_QLAYERS:
                qlayer = CUSTOM_QLAYERS[class_name]
            # 1.2 Else, return the float version of the layer
            else:
                qlayer = layer
                warnings.warn(
                    f"'{class_name}' is not supported to quantize. It will be ignored.")

            # 2. Remove unsupported arguments
            pop_unsupported_args(qlayer)

            # 3. Instantiate quantized layer
            if len(quantize_config) > 0:
                config['quant_config'] = quantize_config
            return qlayer.from_config(config)

        # Replace float layer by quantized layer in three different ways:
        # 1. Check if layer is in quant_config (to quantize specific layers)
        layer_name = layer.name if layer.name[0] == "/" else "/" + layer.name
        match_name = [key for key in q_config.keys() if layer_name.endswith(key)]
        if len(match_name) > 0:
            # In case of multiple matches, take the most hierarchical specific one
            match_name = sorted(match_name, key=lambda x: len(
                x.split('/')), reverse=True)[0]
            match_conf = q_config[match_name]
            return get_quantize_layer(layer, match_conf)

        # 2. Suppose that the layer name has the following format:
        #    .../ParentLayer<_i>/SubParentLayer<_j>/.../Layer<_k>, where ijk are integers and
        #    <_i>, <_j>, <_k> are optional.
        #    Match the pattern and replace the layer with a quantized version.
        match_tuples = []
        for rkey, qobj in q_config_regex.items():
            if rkey.search(layer_name):
                match_tuples.append(qobj)
        if len(match_tuples) > 0:
            # In case of multiple matches, takes the configurations with the highest hierarchy
            max_hierarchy = max([len(qobj[0].split('/'))
                                for qobj in match_tuples])
            match_tuples = {tuple(qobj[0].split('/')[::-1]): qobj[1]
                            for qobj in match_tuples if len(qobj[0].split('/')) == max_hierarchy}
            # And then, chooses the configuration with the most detailed sub-indices,
            # from the end to the beginning.
            #
            # For example, if the layer name is: A_1/B_2/C_3/D_4, and the config keys are:
            # keys = [B_2/C/D, B/C_3/D], the code will search the first exact match from bottom
            # to top, following:
            # First step (layer_name[0], keys[0]): if D_4 == D ? No, go to next step
            # Second step (layer_name[0], keys[1]): if D_4 == D ? No, go to next step
            # Third step (layer_name[1], keys[0]): if C_3 == C ? No, go to next step
            # Fourth step (layer_name[1], keys[1]): if C_3 == C_3 ? Yes, match with config[key[1]]
            #
            # Note: If only exist this keys in config file, keys[0] will be used in the following
            # layers: A_i/B_2/C_j/D_k, for all ijk in [0, ..., n] and j != 3.
            for (idx, pattern) in enumerate(layer_name[1:].split('/')[::-1]):
                match_tuples_copy = {}
                for (key, match_conf) in match_tuples.items():
                    if key[idx] == pattern:
                        match_tuples_copy[key] = match_conf
                # If only one match is found, it is used as the configuration
                if len(match_tuples_copy) == 1:
                    match_conf = list(match_tuples_copy.values())[0]
                    break
                # If length of keys is smaller than hierarchical name, use the last match_conf
                if idx + 1 >= max_hierarchy:
                    break
                # Update match_tuples only when patterns match, in case of a tie
                if len(match_tuples_copy) > 1:
                    match_tuples = match_tuples_copy
            return get_quantize_layer(layer, match_conf)

        # 3. Special cases for Embedding layers
        #    Cases covered in previous steps

        # If no match, return the qlayer with config unchanged
        return get_quantize_layer(layer)

    new_model = deep_clone_model(model, clone_function=_replace_layer)
    out = new_model.outputs

    # Append Dequantizer at the end of the model to convert the output to float value
    if add_dequantizer and not isinstance(new_model.layers[-1], Dequantizer):
        out = Dequantizer(name="float_output")(out)
    return Model(new_model.input, out)


def dump_config(model, skip_default=False):
    """Dump the quantization configuration of a quantized model, exporting the configuration for
    each quantized layer.

    Args:
        model (keras.Model): a quantized model.
        skip_default (bool, optional): remove default values on each quantizer. Defaults to False.

    Returns:
        dict: the configuration of the model.
    """
    # Get the simplest configuration by default of one quantizer
    dump_obj = {"signed": True, "axis": "per-tensor", "bitwidth": None, "scale_bits": None}

    # Function that update the configuration of each quantizer in one layer, reducing the
    # parameters if short_form is True, otherwise adding the default parameters.
    def _update_config(config):
        for conf_value in config.values():
            if isinstance(conf_value, dict):
                # Check if current config is a singular quantizer
                try:
                    scale_bits = conf_value.pop("scale_bits", None)
                    Quantizer(**conf_value)
                    if scale_bits is not None:
                        conf_value["scale_bits"] = scale_bits
                except:
                    _update_config(conf_value)
                    continue

                # Remove extra keys
                keys_to_pop = [key for key in conf_value.keys() if key not in dump_obj]
                for ckey in keys_to_pop:
                    conf_value.pop(ckey)

                # Update the configuration of a singular quantizer follows:
                # * skip_default=True: removes default values, given by Quantizer.get_config()
                # * skip_default=False: keeps only [bitwidth, signed, axis, scale_bits] parameters
                for dkey, dval in dump_obj.items():
                    if not skip_default and dval is not None and dkey not in conf_value:
                        conf_value[dkey] = dval
                    elif skip_default and dval == conf_value.get(dkey, -1):
                        conf_value.pop(dkey)

    # Get the configuration of the model, iterating over each layer and updating on config.
    config = {}
    for layer in model.layers:
        # Try to take the current quantized configuration
        ly_config = layer.get_config().get('quant_config')

        # Only append quantized configuration
        if layer.__class__ in CUSTOM_QLAYERS.values() and ly_config is not None:
            _update_config(ly_config)
            config[layer.name] = ly_config

    return config
