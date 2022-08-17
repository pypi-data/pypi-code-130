import mindspore as ms
import mindspore.ops as ops
from mindspore import Tensor
from mindspore.common.initializer import Normal, Zero
import numpy as np
import matplotlib.pyplot as plt

from mindspore_xai.explainer.backprop.backprop_utils import get_bp_weights, GradNet
from ..utils._legacy import match_model_to_data
from ..utils._legacy import convert_to_instance_with_index, convert_to_link, IdentityLink, convert_to_data, \
    convert_to_model


class Gradient:
    def __init__(self, network, data, mode, network_num_outputs, batch_size=50, local_smoothing=0):
        self._network = network
        self._mode = mode
        self._network_num_outputs = network_num_outputs

        if self._network_num_outputs > 1:
            sens_param = True
        else:
            sens_param = False
        self._grad_net = GradNet(self._network, sens_param=sens_param)

        self._data = data
        self._batch_size = batch_size
        self._local_smoothing = local_smoothing

        # calculate expected values
        link = IdentityLink()
        # convert incoming inputs to standardized iml objects
        link = convert_to_link(link)
        model = convert_to_model(network)
        shap_data = convert_to_data(data.asnumpy(), keep_index=False)
        model_null = match_model_to_data(model, shap_data, model_is_cell=True)
        linkfv = np.vectorize(link.f)

        fnull = np.sum((model_null.T * shap_data.weights).T, 0)
        self.expected_value = linkfv(fnull)

        # see if we have a vector output
        self.vector_out = True
        if len(fnull.shape) == 0:
            self.expected_value = float(self.expected_value)

    def _gradient(self, inputs, class_index):
        """Mindspore gradient."""
        if self._mode == "classification":
            weights = get_bp_weights(self._network_num_outputs, Tensor([class_index] * len(inputs), ms.int32))
            grads = self._grad_net(inputs, weights)
        else:
            grads = self._grad_net(inputs)

        return grads

    def shap_values(self, X, targets, nsamples=200, rseed=None, return_variances=False):
        inputs = Tensor(X, ms.float32)
        inputs_batches = inputs.shape[0]
        num_features = inputs.shape[1]
        num_labels = targets.shape[1]

        # (number of samples, number of target labels, number of features)
        output_phis = Tensor(shape=(inputs_batches, num_labels, num_features), dtype=ms.float32,
                             init=Zero()).init_data()
        output_phi_vars = output_phis.copy()

        # samples_input = input to the model
        # samples_delta = (x - x') for the input being explained - may be an interim input
        samples_input = Tensor(shape=(nsamples, num_features), dtype=ms.float32, init=Zero()).init_data()
        samples_delta = samples_input.copy()

        # use random seed if no argument given
        if rseed is None:
            rseed = np.random.randint(0, 1e6)
        np.random.seed(rseed)

        concat = ops.Concat()
        # for each input sample
        for i in range(inputs_batches):
            phis = Tensor(shape=(num_labels, num_features), dtype=ms.float32, init=Zero()).init_data()
            phi_vars = phis.copy()
            # for each label
            for j in range(num_labels):
                # fill in the samples arrays:
                for k in range(nsamples):
                    rind = np.random.choice(self._data.shape[0])
                    t = np.random.uniform()

                    if self._local_smoothing > 0:
                        x = inputs[i].copy() + Tensor(shape=inputs[i].shape, dtype=ms.float32,
                                                      init=Normal()).init_data() * self._local_smoothing
                    else:
                        x = inputs[i].copy()

                    samples_input[k] = (t * x + (1 - t) * (self._data[rind]).copy()).copy()
                    samples_delta[k] = (x - (self._data[rind]).copy()).copy()

                # target label
                find = targets[i][j]
                grads = []
                for b in range(0, nsamples, self._batch_size):
                    batch = samples_input[b:min(b + self._batch_size, nsamples)].copy()
                    grads.append(self._gradient(batch, find))

                grad = concat(grads)
                # assign the attributions to the right part of the output arrays
                samples = grad * samples_delta
                phis[j] = samples.mean(0)
                phi_vars[j] = samples.var(0) / np.sqrt(samples.shape[0])  # estimate variance of means

            output_phis[i] = phis
            output_phi_vars[i] = phi_vars

        if return_variances:
            return output_phis, output_phi_vars

        return output_phis
