import io
from pathlib import Path

import numpy as np

from .tract_python import ffi, lib

__version__ = "0.2.1"


def string_at(ptr):
    return ffi.string(ptr[0])


class TractModel:
    def __init__(self, typed_model_plan_ptr, original_path: Path):
        self._typed_model_plan_ptr = typed_model_plan_ptr
        self._original_path = original_path

    @classmethod
    def load_nnef_from_path(cls, path: Path):
        _model = ffi.new("CTypedModelPlan * *")
        exit_code = lib.load_plan_from_nnef_path(
            str(path).encode("utf-8"), _model
        )
        if exit_code:
            lib_error = ffi.new("char * *")
            lib.tract_get_last_error(lib_error)
            lib_error = string_at(lib_error).decode("utf-8")
            raise RuntimeError(f"Error while creating plan: {lib_error}")
        return cls(_model, path)

    def run(self, **kwargs):
        for k, v in kwargs.items():
            if not isinstance(k, str):
                raise TypeError(
                    ".run(**kwargs) need kwargs to have str as keys"
                )
            if not isinstance(v, np.ndarray):
                raise TypeError(
                    ".run(**kwargs) need kwargs to have np.ndarray as values"
                )
        # We use npz format as exchange format between numpy and ndarray
        # this avoid to redefine all bindings for all types both side
        # at cost of some minor serializations slowdown

        # contains inputs npz equivalent
        inputs_buffer = io.BytesIO()
        np.savez(inputs_buffer, **kwargs)
        inputs_buffer.seek(0)
        inputs_buffer_bits = inputs_buffer.read()

        raw_output_ref = ffi.new("char * *")
        npz_outputs_buffer_length_ref = ffi.new("size_t *")
        # Call
        exit_code = lib.run_typed_model_plan(
            self._typed_model_plan_ptr,
            inputs_buffer_bits,
            len(inputs_buffer_bits),
            raw_output_ref,
            npz_outputs_buffer_length_ref,
        )
        outputs_buffer_len = ffi.unpack(npz_outputs_buffer_length_ref, 1)[0]
        raw_output_bytes = ffi.unpack(raw_output_ref[0], outputs_buffer_len)

        if exit_code:
            lib_error = ffi.new("char * *")
            lib.tract_get_last_error(lib_error)
            lib_error = string_at(lib_error).decode("utf-8")
            raise RuntimeError(f"Error while running plan: {lib_error}")
        # reload output.npz
        # raw_output_ref is incorrect for now
        outputs_buffer = io.BytesIO(raw_output_bytes)
        outputs_buffer.seek(0)
        results = np.load(outputs_buffer)
        return dict(results)

    def __repr__(self) -> str:
        klass = self.__class__.__name__
        return f"<{klass} path='{self._original_path}'>"


__all__ = ["TractModel"]
