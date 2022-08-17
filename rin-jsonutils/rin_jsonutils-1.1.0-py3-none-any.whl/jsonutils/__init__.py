import json
from functools import partial

from .typing import JSONSerializable, JSONType
from .advanced_json_encoder import AdvancedJSONEncoder, IResolver, ResolveError, ResolverPriority

__all__ = [
    "get_default_encoder", "set_default_encoder", "get_default_decoder", "set_default_decoder",
    "AdvancedJSONEncoder", "IResolver", "ResolveError", "ResolverPriority",
    "coder_switch", "JSONSerializable", "JSONType"
]

original_json_default_encoder: json.JSONEncoder = json._default_encoder
original_json_default_decoder: json.JSONDecoder = json._default_decoder


def get_default_encoder() -> json.JSONEncoder:
    return json._default_encoder


def set_default_encoder(encoder: json.JSONEncoder) -> None:
    json._default_encoder = encoder


def get_default_decoder() -> json.JSONDecoder:
    return json._default_decoder


def set_default_decoder(decoder: json.JSONDecoder) -> None:
    json._default_decoder = decoder


def create_default_advanced_encoder() -> AdvancedJSONEncoder:
    from .resolvers import NumpyResolver, IterableResolver, DateTimeResolver, NumberResolver, JSONSerializableResolver
    resolvers = {
        "serializable": JSONSerializableResolver(),
        "numpy": NumpyResolver(),
        "iterable": IterableResolver(),
        "datetime": DateTimeResolver(),
        "number": NumberResolver()
    }
    encoder = AdvancedJSONEncoder()
    for n, r in resolvers.items():
        encoder.add_resolver(n, r)
    return encoder


from ._coder_switch import CoderSwitch

coder_switch = CoderSwitch("basic")
coder_switch.register("basic", original_json_default_encoder, original_json_default_decoder)
coder_switch.register("advanced", create_default_advanced_encoder(), original_json_default_decoder)

use = coder_switch.use
register_coder = coder_switch.register
get_coder = coder_switch.get_coder
get_all_coders = coder_switch.get_all_coders
get_current_coder = coder_switch.get_current_coder

use_basic_coders = partial(coder_switch.use, "basic")
use_advanced_coders = partial(coder_switch.use, "advanced")
