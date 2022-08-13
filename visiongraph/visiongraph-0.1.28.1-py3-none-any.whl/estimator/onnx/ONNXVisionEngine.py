from typing import Sequence, Optional, Dict, Any, List

import numpy as np

import onnxruntime as rt

from visiongraph.data.Asset import Asset
from visiongraph.estimator.BaseVisionEngine import BaseVisionEngine


class ONNXVisionEngine(BaseVisionEngine):
    def __init__(self, model: Asset, execution_providers: Optional[List[str]] = None,
                 flip_channels: bool = True, normalize: bool = False, padding: bool = False):
        super().__init__(flip_channels, normalize, padding)

        self.model = model
        self.execution_providers = execution_providers

        self.session: Optional[rt.InferenceSession] = None
        self.session_options = rt.SessionOptions()

    def setup(self):
        if self.execution_providers is None:
            self.execution_providers = ["CUDAExecutionProvider",
                                        "OpenVINOExecutionProvider",
                                        "CPUExecutionProvider"]

        self.session = rt.InferenceSession(self.model.path,
                                           providers=self.execution_providers,
                                           sess_options=self.session_options)

        # read input infos
        self.input_names = [e.name for e in self.session.get_inputs()]
        self.output_names = [e.name for e in self.session.get_outputs()]

    def _inference(self, image: np.ndarray, inputs: Optional[Dict[str, Any]] = None) -> Dict[str, np.ndarray]:
        results = self.session.run(self.output_names, inputs)
        result_dict = {n: r for n, r in zip(self.output_names, results)}
        return result_dict

    def get_input_shape(self, input_name: str) -> Sequence[int]:
        for input in self.session.get_inputs():
            if input.name == input_name:
                return input.shape

        return []

    def release(self):
        self.session = None
