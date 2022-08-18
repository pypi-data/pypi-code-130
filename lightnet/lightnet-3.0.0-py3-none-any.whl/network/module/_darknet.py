#
#   Base network structure for Darknet networks
#   Copyright EAVISE
#
import os
import logging
import numpy as np
import torch
import torch.nn as nn
from .. import layer as lnl
from ._lightnet import Lightnet

__all__ = ['Darknet']
log = logging.getLogger(__name__)


class Darknet(Lightnet):
    """ This network module provides functionality to load darknet weight files. """
    header = (0, 2, 0)

    def load(self, weights_file, *args, **kwargs):
        """ This function will load the weights from a file.
        If the file extension is _.pt_, it will be considered as a `pytorch pickle file <http://pytorch.org/docs/stable/notes/serialization.html#recommended-approach-for-saving-a-model>`_.
        Otherwise, the file is considered to be a darknet binary weight file.

        Args:
            weights_file (str): path to file
            *args, \*\*kwargs: Extra arguments passed to :func:`lightnet.network.module.Lightnet.load` when loading pytorch weights

        Note:
            Darknet weight files also contain the number of images the network has been trained on. |br|
            In Lightnet however, this is a parameter from the loss function and as such this value cannot be correctly set on that object.
            This value will thus be ignored by lightnet and when saving a darknet file, this value will be set to zero.
        """
        if os.path.splitext(weights_file)[1] == '.pt':
            log.debug('Loading weights from pytorch file')
            super().load(weights_file, *args, **kwargs)
        else:
            log.debug('Loading weights from darknet file')
            self._load_darknet_weights(weights_file)

    def save(self, weights_file, *args, **kwargs):
        """ This function will save the weights to a file.
        If the file extension is ``.pt``, it will be considered as a `pytorch pickle file <http://pytorch.org/docs/stable/notes/serialization.html#recommended-approach-for-saving-a-model>`_.
        Otherwise, the file is considered to be a darknet binary weight file.

        Args:
            weights_file (str): path to file
            *args, \*\*kwargs: Extra arguments passed to :func:`lightnet.network.module.Lightnet.save` when saving as pytorch weights
        """
        if os.path.splitext(weights_file)[1] == '.pt':
            log.debug('Saving weights to pytorch file')
            super().save(weights_file, *args, **kwargs)
        else:
            log.debug('Saving weights to darknet file')
            self._save_darknet_weights(weights_file)

    def _load_darknet_weights(self, weights_file):
        weights = WeightLoader(weights_file)
        self.header = weights.header

        done_loading = False
        for name, module in self.named_modules(types=weights.layers, recurse_into_matched=False):
            if not done_loading:
                weights.load_layer(module)
                log.debug('Layer loaded: %s', name)
                if weights.start >= weights.size:
                    log.debug('Finished loading weights [%d/%d weights]', weights.start, weights.size)
                    done_loading = True
            else:
                log.warning('No more weigths for layer: %s', name)

        if not done_loading:
            log.debug('Finished loading weights [%d/%d weights]', weights.start, weights.size)

    def _save_darknet_weights(self, weights_file):
        weights = WeightSaver(self.header, 0)

        for name, module in self.named_modules(types=weights.layers, recurse_into_matched=False):
            weights.save_layer(module)
            log.debug('Layer saved: %s', name)

        weights.write_file(weights_file)


class WeightLoader:
    """ Load darknet weight files into pytorch layers """
    layers = (
        lnl.Conv2dBatchReLU,
        lnl.Conv2dReLU,
        nn.Conv2d,
        nn.Linear,
    )

    def __init__(self, filename):
        with open(filename, 'rb') as fp:
            self.header = tuple(np.fromfile(fp, count=3, dtype=np.int32))
            ver_num = self.header[0]*100+self.header[1]*10+self.header[2]
            log.debug('Loading weight file: version %d.%d.%d', *self.header)

            if ver_num <= 19:
                log.warning('Weight file uses sizeof to compute variable size, which might lead to undefined behaviour. (choosing int=int32, float=float32)')
                self.seen = int(np.fromfile(fp, count=1, dtype=np.int32)[0])
            elif ver_num <= 29:
                log.warning('Weight file uses sizeof to compute variable size, which might lead to undefined behaviour. (choosing int=int32, float=float32, size_t=int64)')
                self.seen = int(np.fromfile(fp, count=1, dtype=np.int64)[0])
            else:
                log.error('New weight file syntax! Loading of weights might not work properly. Please submit an issue with the weight file version number. [Run with DEBUG logging level]')
                self.seen = int(np.fromfile(fp, count=1, dtype=np.int64)[0])

            self.buf = np.fromfile(fp, dtype=np.float32)

        self.start = 0
        self.size = self.buf.size

    def load_layer(self, layer):
        """ Load weights for a layer from the weights file """
        if type(layer) == nn.Conv2d:
            self._load_conv(layer)
        elif type(layer) == lnl.Conv2dReLU:
            self._load_conv(layer.layers[0])
        elif type(layer) == lnl.Conv2dBatchReLU:
            self._load_convbatch(layer)
        elif type(layer) == nn.Linear:
            self._load_fc(layer)
        else:
            raise NotImplementedError(f'The layer you are trying to load is not supported [{type(layer)}]')

    def _load_conv(self, model):
        num_b = model.bias.numel()
        model.bias.data.copy_(torch.from_numpy(self.buf[self.start:self.start+num_b])
                                   .view_as(model.bias.data))
        self.start += num_b

        num_w = model.weight.numel()
        model.weight.data.copy_(torch.from_numpy(self.buf[self.start:self.start+num_w])
                                     .view_as(model.weight.data))
        self.start += num_w

    def _load_convbatch(self, model):
        num_b = model.layers[1].bias.numel()
        model.layers[1].bias.data.copy_(torch.from_numpy(self.buf[self.start:self.start+num_b])
                                             .view_as(model.layers[1].bias.data))
        self.start += num_b
        model.layers[1].weight.data.copy_(torch.from_numpy(self.buf[self.start:self.start+num_b])
                                               .view_as(model.layers[1].weight.data))
        self.start += num_b
        model.layers[1].running_mean.copy_(torch.from_numpy(self.buf[self.start:self.start+num_b])
                                                .view_as(model.layers[1].running_mean))
        self.start += num_b
        model.layers[1].running_var.copy_(torch.from_numpy(self.buf[self.start:self.start+num_b])
                                               .view_as(model.layers[1].running_var))
        self.start += num_b

        num_w = model.layers[0].weight.numel()
        model.layers[0].weight.data.copy_(torch.from_numpy(self.buf[self.start:self.start+num_w])
                                               .view_as(model.layers[0].weight.data))
        self.start += num_w

    def _load_fc(self, model):
        num_b = model.bias.numel()
        model.bias.data.copy_(torch.from_numpy(self.buf[self.start:self.start+num_b])
                                   .view_as(model.bias.data))
        self.start += num_b

        num_w = model.weight.numel()
        model.weight.data.copy_(torch.from_numpy(self.buf[self.start:self.start+num_w])
                                     .view_as(model.weight.data))
        self.start += num_w


class WeightSaver:
    """ Save darknet weight files from pytorch layers """
    layers = (
        lnl.Conv2dBatchReLU,
        lnl.Conv2dReLU,
        nn.Conv2d,
        nn.Linear,
    )

    def __init__(self, header, seen):
        self.weights = []
        self.header = np.array(header, dtype=np.int32)
        ver_num = self.header[0]*100+self.header[1]*10+self.header[2]
        if ver_num <= 19:
            self.seen = np.int32(seen)
        elif ver_num <= 29:
            self.seen = np.int64(seen)
        else:
            log.error('New weight file syntax! Saving of weights might not work properly. Please submit an issue with the weight file version number. [Run with DEBUG logging level]')
            self.seen = np.int64(seen)

    def write_file(self, filename):
        """ Save the accumulated weights to a darknet weightfile """
        log.debug('Writing weight file: version %d.%d.%d', *self.header)
        with open(filename, 'wb') as fp:
            self.header.tofile(fp)
            self.seen.tofile(fp)
            for np_arr in self.weights:
                np_arr.tofile(fp)
        log.info('Weight file saved as %s', filename)

    def save_layer(self, layer):
        """ save weights for a layer """
        if type(layer) == nn.Conv2d:
            self._save_conv(layer)
        elif type(layer) == lnl.Conv2dReLU:
            self._save_conv(layer.layers[0])
        elif type(layer) == lnl.Conv2dBatchReLU:
            self._save_convbatch(layer)
        elif type(layer) == nn.Linear:
            self._save_fc(layer)
        else:
            raise NotImplementedError(f'The layer you are trying to save is not supported [{type(layer)}]')

    def _save_conv(self, model):
        self.weights.append(model.bias.cpu().data.numpy())
        self.weights.append(model.weight.cpu().data.numpy())

    def _save_convbatch(self, model):
        self.weights.append(model.layers[1].bias.cpu().data.numpy())
        self.weights.append(model.layers[1].weight.cpu().data.numpy())
        self.weights.append(model.layers[1].running_mean.cpu().numpy())
        self.weights.append(model.layers[1].running_var.cpu().numpy())
        self.weights.append(model.layers[0].weight.cpu().data.numpy())

    def _save_fc(self, model):
        self.weights.append(model.bias.cpu().data.numpy())
        self.weights.append(model.weight.cpu().data.numpy())
