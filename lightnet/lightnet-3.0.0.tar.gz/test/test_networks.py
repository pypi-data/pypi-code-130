#
#   Test if network forward function runs
#   Copyright EAVISE
#

import inspect
import pytest
import torch
import lightnet as ln

classification_networks = [
    'Alexnet',
    'Darknet',
    'Darknet19',
    'Darknet53',
    'MobileDarknet19',
    'MobilenetV1',
    'MobilenetV2',
    'Resnet50',
    'Resnet101',
    'Resnet152',
    'VGG11',
    'VGG13',
    'VGG16',
    'VGG19',
]
anchor_detection_networks = [
    'DYolo',
    'MobilenetYolo',
    'MobileYoloV2',
    'MobileYoloV2Upsample',
    'ResnetYolo',
    'TinyYoloV2',
    'TinyYoloV3',
    'YoloV2',
    'YoloV2Upsample',
    'YoloV3',
    'Yolt',
]
oriented_anchor_detection_networks = [
    'O_DYolo',
    'O_YoloV2',
    'O_YoloV3',
    'O_Yolt',
]
masked_anchor_detection_networks = [
    'M_DYolo',
    'M_YoloV2',
    'M_YoloV3',
    'M_Yolt',
    'M_ResnetYolo',
]
corner_detection_networks = [
    'Cornernet',
    'CornernetSqueeze',
]
special_networks = [
    'YoloFusion',
]
ignore_networks = [
    'Yolact50',
    'Yolact101',
]


@pytest.fixture(scope='module')
def input_tensor():
    def _input_tensor(dimension, channels=3, batch=1):
        return torch.rand(batch, channels, dimension, dimension)
    return _input_tensor


# Base classification networks
@pytest.mark.parametrize('network', classification_networks)
def test_classification_cpu(network, input_tensor):
    uut = getattr(ln.models, network)(10).eval()
    it = input_tensor(uut.inner_stride * 3)

    output_tensor = uut(it)
    assert output_tensor.dim() == 2
    assert output_tensor.shape[0] == it.shape[0]
    assert output_tensor.shape[1] == uut.num_classes


@pytest.mark.parametrize('network', classification_networks)
@pytest.mark.cuda
@pytest.mark.skipif(not torch.cuda.is_available(), reason='CUDA not available')
def test_classification_cuda(network, input_tensor):
    uut = getattr(ln.models, network)(10).to('cuda')
    it = input_tensor(uut.inner_stride * 3, batch=2).to('cuda')

    output_tensor = uut(it)
    assert output_tensor.dim() == 2
    assert output_tensor.shape[0] == it.shape[0]
    assert output_tensor.shape[1] == uut.num_classes


# Anchor detection networks
@pytest.mark.parametrize('network', anchor_detection_networks)
def test_anchor_detection_cpu(network, input_tensor):
    uut = getattr(ln.models, network)(20).eval()
    it = input_tensor(uut.inner_stride)

    output_tensor = uut(it)
    if isinstance(output_tensor, torch.Tensor):
        assert output_tensor.dim() == 4
        assert output_tensor.shape[0] == it.shape[0]
        assert output_tensor.shape[1] == uut.anchors.num_anchors * (5 + uut.num_classes)
        assert output_tensor.shape[2] == it.shape[2] // uut.stride
        assert output_tensor.shape[3] == it.shape[3] // uut.stride
    else:
        for i, tensor in enumerate(output_tensor):
            assert tensor.dim() == 4
            assert tensor.shape[0] == it.shape[0]
            assert tensor.shape[1] == uut.anchors.get_scale(i).num_anchors * (5 + uut.num_classes)
            assert tensor.shape[2] == it.shape[2] // uut.stride[i]
            assert tensor.shape[3] == it.shape[3] // uut.stride[i]


@pytest.mark.parametrize('network', anchor_detection_networks)
@pytest.mark.cuda
@pytest.mark.skipif(not torch.cuda.is_available(), reason='CUDA not available')
def test_anchor_detection_cuda(network, input_tensor):
    uut = getattr(ln.models, network)(20).to('cuda')
    it = input_tensor(uut.inner_stride, batch=2).to('cuda')

    output_tensor = uut(it)
    if isinstance(output_tensor, torch.Tensor):
        assert output_tensor.dim() == 4
        assert output_tensor.shape[0] == it.shape[0]
        assert output_tensor.shape[1] == uut.anchors.num_anchors * (5 + uut.num_classes)
        assert output_tensor.shape[2] == it.shape[2] // uut.stride
        assert output_tensor.shape[3] == it.shape[3] // uut.stride
    else:
        for i, tensor in enumerate(output_tensor):
            assert tensor.dim() == 4
            assert tensor.shape[0] == it.shape[0]
            assert tensor.shape[1] == uut.anchors.get_scale(i).num_anchors * (5 + uut.num_classes)
            assert tensor.shape[2] == it.shape[2] // uut.stride[i]
            assert tensor.shape[3] == it.shape[3] // uut.stride[i]


# Oriented anchor detection networks
@pytest.mark.parametrize('network', oriented_anchor_detection_networks)
def test_oriented_anchor_detection_cpu(network, input_tensor):
    uut = getattr(ln.models, network)(20).eval()
    it = input_tensor(uut.inner_stride)

    output_tensor = uut(it)
    if isinstance(output_tensor, torch.Tensor):
        assert output_tensor.dim() == 4
        assert output_tensor.shape[0] == it.shape[0]
        assert output_tensor.shape[1] == uut.anchors.num_anchors * (6 + uut.num_classes)
        assert output_tensor.shape[2] == it.shape[2] // uut.stride
        assert output_tensor.shape[3] == it.shape[3] // uut.stride
    else:
        for i, tensor in enumerate(output_tensor):
            assert tensor.dim() == 4
            assert tensor.shape[0] == it.shape[0]
            assert tensor.shape[1] == uut.anchors.get_scale(i).num_anchors * (6 + uut.num_classes)
            assert tensor.shape[2] == it.shape[2] // uut.stride[i]
            assert tensor.shape[3] == it.shape[3] // uut.stride[i]


@pytest.mark.parametrize('network', oriented_anchor_detection_networks)
@pytest.mark.cuda
@pytest.mark.skipif(not torch.cuda.is_available(), reason='CUDA not available')
def test_oriented_anchor_detection_cuda(network, input_tensor):
    uut = getattr(ln.models, network)(20).to('cuda')
    it = input_tensor(uut.inner_stride, batch=2).to('cuda')

    output_tensor = uut(it)
    if isinstance(output_tensor, torch.Tensor):
        assert output_tensor.dim() == 4
        assert output_tensor.shape[0] == it.shape[0]
        assert output_tensor.shape[1] == uut.anchors.num_anchors * (6 + uut.num_classes)
        assert output_tensor.shape[2] == it.shape[2] // uut.stride
        assert output_tensor.shape[3] == it.shape[3] // uut.stride
    else:
        for i, tensor in enumerate(output_tensor):
            assert tensor.dim() == 4
            assert tensor.shape[0] == it.shape[0]
            assert tensor.shape[1] == uut.anchors.get_scale(i).num_anchors * (6 + uut.num_classes)
            assert tensor.shape[2] == it.shape[2] // uut.stride[i]
            assert tensor.shape[3] == it.shape[3] // uut.stride[i]


# Masked anchor detection networks
@pytest.mark.parametrize('network', masked_anchor_detection_networks)
def test_masked_anchor_detection_cpu(network, input_tensor):
    uut = getattr(ln.models, network)(20).eval()
    it = input_tensor(uut.inner_stride)
    box_output, mask_output = uut(it)

    if isinstance(box_output, torch.Tensor):
        assert box_output.dim() == 4
        assert box_output.shape[0] == it.shape[0]
        assert box_output.shape[1] == uut.anchors.num_anchors * (5 + uut.num_classes + uut.num_masks)
        assert box_output.shape[2] == it.shape[2] // uut.stride
        assert box_output.shape[3] == it.shape[3] // uut.stride
    else:
        for i, box_output in enumerate(box_output):     # noqa: B020
            assert box_output.dim() == 4
            assert box_output.shape[0] == it.shape[0]
            assert box_output.shape[1] == uut.anchors.get_scale(i).num_anchors * (5 + uut.num_classes + uut.num_masks)
            assert box_output.shape[2] == it.shape[2] // uut.stride[i]
            assert box_output.shape[3] == it.shape[3] // uut.stride[i]

    if isinstance(mask_output, torch.Tensor):
        assert mask_output.dim() == 4
        assert mask_output.shape[0] == it.shape[0]
        assert mask_output.shape[1] == uut.num_masks
        assert mask_output.shape[2] == it.shape[2] // uut.mask_stride
        assert mask_output.shape[3] == it.shape[3] // uut.mask_stride
    else:
        for i, mask_output in enumerate(mask_output):   # noqa: B020
            assert mask_output.dim() == 4
            assert mask_output.shape[0] == it.shape[0]
            assert mask_output.shape[1] == uut.num_masks
            assert mask_output.shape[2] == it.shape[2] // uut.mask_stride[i]
            assert mask_output.shape[3] == it.shape[3] // uut.mask_stride[i]


@pytest.mark.parametrize('network', masked_anchor_detection_networks)
@pytest.mark.cuda
@pytest.mark.skipif(not torch.cuda.is_available(), reason='CUDA not available')
def test_masked_anchor_detection_cuda(network, input_tensor):
    uut = getattr(ln.models, network)(20).to('cuda')
    it = input_tensor(uut.inner_stride, batch=2).to('cuda')
    box_output, mask_output = uut(it)

    if isinstance(box_output, torch.Tensor):
        assert box_output.dim() == 4
        assert box_output.shape[0] == it.shape[0]
        assert box_output.shape[1] == uut.anchors.num_anchors * (5 + uut.num_classes + uut.num_masks)
        assert box_output.shape[2] == it.shape[2] // uut.stride
        assert box_output.shape[3] == it.shape[3] // uut.stride
    else:
        for i, box_output in enumerate(box_output):     # noqa: B020
            assert box_output.dim() == 4
            assert box_output.shape[0] == it.shape[0]
            assert box_output.shape[1] == uut.anchors.get_scale(i).num_anchors * (5 + uut.num_classes + uut.num_masks)
            assert box_output.shape[2] == it.shape[2] // uut.stride[i]
            assert box_output.shape[3] == it.shape[3] // uut.stride[i]

    if isinstance(mask_output, torch.Tensor):
        assert mask_output.dim() == 4
        assert mask_output.shape[0] == it.shape[0]
        assert mask_output.shape[1] == uut.num_masks
        assert mask_output.shape[2] == it.shape[2] // uut.mask_stride
        assert mask_output.shape[3] == it.shape[3] // uut.mask_stride
    else:
        for i, mask_output in enumerate(mask_output):   # noqa: B020
            assert mask_output.dim() == 4
            assert mask_output.shape[0] == it.shape[0]
            assert mask_output.shape[1] == uut.num_masks
            assert mask_output.shape[2] == it.shape[2] // uut.mask_stride[i]
            assert mask_output.shape[3] == it.shape[3] // uut.mask_stride[i]


# Corner detection networks
@pytest.mark.parametrize('network', corner_detection_networks)
def test_corner_detection_cpu(network, input_tensor):
    uut = getattr(ln.models, network)(20).eval()
    it = input_tensor(uut.inner_stride)

    output_tensor = uut(it)
    if isinstance(output_tensor, torch.Tensor):
        assert output_tensor.dim() == 4
        assert output_tensor.shape[0] == it.shape[0]
        assert output_tensor.shape[1] == (uut.num_classes + 3) * 2
        assert output_tensor.shape[2] == it.shape[2] // uut.stride
        assert output_tensor.shape[3] == it.shape[3] // uut.stride
    else:
        for tensor in output_tensor:
            assert tensor.dim() == 4
            assert tensor.shape[0] == it.shape[0]
            assert tensor.shape[1] == (uut.num_classes + 3) * 2
            assert tensor.shape[2] == it.shape[2] // uut.stride
            assert tensor.shape[3] == it.shape[3] // uut.stride


@pytest.mark.parametrize('network', corner_detection_networks)
@pytest.mark.cuda
@pytest.mark.skipif(not torch.cuda.is_available(), reason='CUDA not available')
def test_corner_detection_cuda(network, input_tensor):
    uut = getattr(ln.models, network)(20).to('cuda')
    it = input_tensor(uut.inner_stride, batch=2).to('cuda')

    output_tensor = uut(it)
    if isinstance(output_tensor, torch.Tensor):
        assert output_tensor.dim() == 4
        assert output_tensor.shape[0] == it.shape[0]
        assert output_tensor.shape[1] == (uut.num_classes + 3) * 2
        assert output_tensor.shape[2] == it.shape[2] // uut.stride
        assert output_tensor.shape[3] == it.shape[3] // uut.stride
    else:
        for tensor in output_tensor:
            assert tensor.dim() == 4
            assert tensor.shape[0] == it.shape[0]
            assert tensor.shape[1] == (uut.num_classes + 3) * 2
            assert tensor.shape[2] == it.shape[2] // uut.stride
            assert tensor.shape[3] == it.shape[3] // uut.stride


# YoloFusion
def test_yolofusion_cpu(input_tensor):
    it = input_tensor(ln.models.YoloFusion.inner_stride, 4)

    for fusion in (0, 1, 10, 22, 27):
        uut = ln.models.YoloFusion(20, fuse_layer=fusion).eval()
        output_tensor = uut(it)
        assert output_tensor.dim() == 4
        assert output_tensor.shape[0] == it.shape[0]
        assert output_tensor.shape[1] == uut.anchors.num_anchors * (5 + uut.num_classes)
        assert output_tensor.shape[2] == it.shape[2] // uut.stride
        assert output_tensor.shape[3] == it.shape[3] // uut.stride


@pytest.mark.cuda
@pytest.mark.skipif(not torch.cuda.is_available(), reason='CUDA not available')
def test_yolofusion_cuda(input_tensor):
    it = input_tensor(ln.models.YoloFusion.inner_stride * 2, 4).to('cuda')

    for fusion in (0, 1, 10, 22, 27):
        uut = ln.models.YoloFusion(20, fuse_layer=fusion).to('cuda')
        output_tensor = uut(it)
        assert output_tensor.dim() == 4
        assert output_tensor.shape[0] == it.shape[0]
        assert output_tensor.shape[1] == uut.anchors.num_anchors * (5 + uut.num_classes)
        assert output_tensor.shape[2] == it.shape[2] // uut.stride
        assert output_tensor.shape[3] == it.shape[3] // uut.stride


# All networks tested?
def test_all_networks_tested():
    networks = [
        net for net in dir(ln.models)
        if (inspect.isclass(getattr(ln.models, net)))
        and (issubclass(getattr(ln.models, net), torch.nn.Module))
    ]

    tested_networks = set(
        classification_networks
        + anchor_detection_networks
        + oriented_anchor_detection_networks
        + masked_anchor_detection_networks
        + corner_detection_networks
        + special_networks
        + ignore_networks,
    )
    for net in networks:
        if net not in tested_networks:
            raise NotImplementedError(f'Network [{net}] is not being tested!')
