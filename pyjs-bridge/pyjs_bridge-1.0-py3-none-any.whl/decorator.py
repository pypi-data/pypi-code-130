from functools import update_wrapper, partialmethod
import inspect
from .registry import *
from .pillar import server_out_call
import uuid


class Expose:
    def __init__(self, func):
        update_wrapper(self, func)
        register_function(func)

    def __call__(self, *args, **kwargs):
        raise AssertionError("This is an exposed function, which cannot be called directly from backend.")


def client_object_init(self, transport, transport_type, token_data):
    self.client_id = uuid.uuid4()
    self.transport = transport
    self.transport_type = transport_type
    self.token_data = token_data
    self.expired = False


def client_object_hash(self):
    return hash(self.client_id)


def client_object_eq(self, another):
    return self.client_id == another.client_id


def blend_args(signature, args, kwargs):
    for i, (arg, t, default) in enumerate(signature):
        if i < len(args):
            kwargs[arg] = args[i]
        else:
            if default is not None and arg not in kwargs:
                kwargs[arg] = default
    return kwargs


def send_message(self, *args, **kwargs):
    function_call, signature = args[0]
    return server_out_call(self, function_call, blend_args(signature, args[1:], kwargs))


class Client_interface:
    def __init__(self, the_class):
        update_wrapper(self, the_class)
        functions = inspect.getmembers(the_class, predicate=inspect.isfunction)
        class_content = {
            "__init__": client_object_init,
            "__hash__": client_object_hash,
            "__eq__": client_object_eq
        }
        class_info = []
        for n, f in functions:
            _, signature = read_signature("", "", f)
            class_content[n] = partialmethod(send_message, (n, signature[1:]))
            class_info.append((n, signature[1:], f.__doc__))
        new_class = type("Client_object", (object, ), class_content)
        register_client(new_class, class_info)

    def __call__(self, transport):
        raise AssertionError("This is a class interface, which cannot be called directly from backend.")
