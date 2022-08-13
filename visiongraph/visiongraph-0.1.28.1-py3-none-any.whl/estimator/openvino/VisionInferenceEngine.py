from typing import Dict, Optional, Any, Sequence

import numpy as np
from openvino.inference_engine import IECore, IENetwork, ExecutableNetwork

from visiongraph.data.Asset import Asset
from visiongraph.estimator.BaseVisionEngine import BaseVisionEngine


class VisionInferenceEngine(BaseVisionEngine):

    def __init__(self, model: Asset, weights: Asset, flip_channels: bool = True, normalize: bool = False,
                 padding: bool = False, device: str = "CPU"):
        super().__init__(flip_channels, normalize, padding)

        self.device = device

        self.model = model
        self.weights = weights

        self.ie: Optional[IECore] = None
        self.net: Optional[IENetwork] = None
        self.infer_network: Optional[ExecutableNetwork] = None

    def setup(self):
        # setup inference engine
        self.ie = IECore()
        self.net = self.ie.read_network(model=self.model.path, weights=self.weights.path)

        self.input_names = list(self.net.input_info.keys())
        self.output_names = list(self.net.outputs.keys())

        self.infer_network = self.ie.load_network(network=self.net, device_name=self.device)

    def _inference(self, image: np.ndarray, inputs: Optional[Dict[str, Any]] = None) -> Dict[str, np.ndarray]:
        return self.infer_network.infer(inputs=inputs)

    def get_input_shape(self, input_name: str) -> Sequence[int]:
        return self.net.input_info[input_name].input_data.shape

    def release(self):
        pass
