#
#   Module Utilities
#   Copyright EAVISE
#
import torch

__all__ = ['get_module_device', 'get_module_shape']


def get_module_device(module, default=None):
    """
    This function tries to get the device from a module, and returns the default if it cannot be determined.

    The function goes through all parameters of a module and checks its device.
    If all parameters have the same device, this is considered the module device and returned.
    Otherwise we return the default if given or raise a RuntimeError.

    Args:
        module (nn.Module): Module to check
        default (torch.device, optional): Default device to return; Default **raise RuntimeError**

    Example:
        >>> module = torch.nn.Conv2d(3, 32, 3, 1, 1)
        >>> ln.util.get_module_device(module)
        device(type='cpu')

        >>> module = torch.nn.Conv2d(3, 32, 3, 1, 1)
        >>> module.to('cuda')  # doctest: +SKIP
        >>> ln.util.get_module_device(module)   # doctest: +SKIP
        device(type='cuda', index=0)
    """
    device = None
    for param in module.parameters():
        if device is None:
            device = param.device
        elif device != param.device:
            device = None
            break

    if device is not None:
        return device

    if default is not None:
        return torch.device(default)

    raise RuntimeError('Could not determine device from module.')


def get_module_shape(module, input_shape):
    """
    This function tries to get the output shape(s) from a module.

    We first generate a random tensor of the specified ``input_shape`` and run it through the module.
    Afterwards we return the shape of the output tensor(s).
    If anything goes wrong, a RuntimeError is raised.

    Args:
        module (nn.Module): Module to check
        input_shape (tuple): Shape of the input tensor

    Returns:
        torch.Size or list<torch.Size>: Module output shape(s)

    Example:
        >>> # Get the output shape of simple layers
        >>> module = torch.nn.Conv2d(3, 32, 3, 1, 1)
        >>> ln.util.get_module_shape(module, (1, 3, 16, 16))
        torch.Size([1, 32, 16, 16])

        >>> # The function also works with multiple outputs and with module on other devices
        >>> module = ln.network.layer.FeatureExtractor(ln.network.backbone.VGG.A(3, 512), ['8_conv'], True)
        >>> module.to('cuda')   # doctest: +SKIP
        >>> ln.util.get_module_shape(module, (1, 3, 92, 92))
        [torch.Size([1, 512, 2, 2]), torch.Size([1, 512, 11, 11])]
    """
    device = get_module_device(module, 'cpu')
    mode = module.training

    try:
        with torch.no_grad():
            module.train(False)
            test_input = torch.rand(*input_shape, device=device, requires_grad=False)
            output = module(test_input)

            if isinstance(output, torch.Tensor):
                return output.shape
            else:
                return [o.shape for o in output]
    except BaseException as err:
        raise RuntimeError('Could not determine output shape from module.') from err
    finally:
        module.train(mode)
