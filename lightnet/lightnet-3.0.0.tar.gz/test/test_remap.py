#
#   Test if network weight remapping works
#   Copyright EAVISE
#
import re
import inspect
import pytest
import torch
import lightnet as ln

remaps = [
    # source,                   target,                             remap
    (ln.models.Darknet,         ln.models.TinyYoloV2,               ln.models.TinyYoloV2.remap_darknet),
    (ln.models.Darknet,         ln.models.TinyYoloV3,               ln.models.TinyYoloV3.remap_darknet),
    (ln.models.Darknet19,       ln.models.DYolo,                    ln.models.DYolo.remap_darknet19),
    (ln.models.Darknet19,       ln.models.O_DYolo,                  ln.models.O_DYolo.remap_darknet19),
    (ln.models.Darknet19,       ln.models.M_DYolo,                  ln.models.M_DYolo.remap_darknet19),
    (ln.models.Darknet19,       ln.models.YoloV2,                   ln.models.YoloV2.remap_darknet19),
    (ln.models.Darknet19,       ln.models.O_YoloV2,                 ln.models.O_YoloV2.remap_darknet19),
    (ln.models.Darknet19,       ln.models.M_YoloV2,                 ln.models.M_YoloV2.remap_darknet19),
    (ln.models.Darknet19,       ln.models.YoloV2Upsample,           ln.models.YoloV2Upsample.remap_darknet19),
    (ln.models.Darknet53,       ln.models.YoloV3,                   ln.models.YoloV3.remap_darknet53),
    (ln.models.Darknet53,       ln.models.O_YoloV3,                 ln.models.O_YoloV3.remap_darknet53),
    (ln.models.Darknet53,       ln.models.M_YoloV3,                 ln.models.M_YoloV3.remap_darknet53),
    (ln.models.Darknet19,       ln.models.Yolt,                     ln.models.Yolt.remap_darknet19),
    (ln.models.Darknet19,       ln.models.O_Yolt,                   ln.models.O_Yolt.remap_darknet19),
    (ln.models.Darknet19,       ln.models.M_Yolt,                   ln.models.M_Yolt.remap_darknet19),
    (ln.models.MobileDarknet19, ln.models.MobileYoloV2,             ln.models.MobileYoloV2.remap_mobile_darknet19),
    (ln.models.MobileDarknet19, ln.models.MobileYoloV2Upsample,     ln.models.MobileYoloV2Upsample.remap_mobile_darknet19),
    (ln.models.MobilenetV1,     ln.models.MobilenetYolo,            ln.models.MobilenetYolo.remap_mobilenet_v1),
    (ln.models.Resnet50,        ln.models.Yolact50,                 ln.models.Yolact50.remap_resnet),
    (ln.models.Resnet50,        ln.models.ResnetYolo,               ln.models.ResnetYolo.remap_resnet50),
    (ln.models.Resnet50,        ln.models.M_ResnetYolo,             ln.models.M_ResnetYolo.remap_resnet50),
    (ln.models.Resnet101,       ln.models.Yolact101,                ln.models.Yolact101.remap_resnet),
]

# Difficult to test (usually remaps from other repos)
remap_skips = [
    ln.models.Cornernet.remap_princeton_vl,
    ln.models.CornernetSqueeze.remap_princeton_vl,
    ln.models.Alexnet.remap_torchvision,
    ln.models.VGG11.remap_torchvision,
    ln.models.VGG13.remap_torchvision,
    ln.models.VGG16.remap_torchvision,
    ln.models.VGG19.remap_torchvision,
    ln.models.Resnet50.remap_torchvision,
    ln.models.Resnet101.remap_torchvision,
    ln.models.Resnet152.remap_torchvision,
    ln.models.Yolact50.remap_dbolya,
    ln.models.Yolact101.remap_dbolya,
]


@pytest.mark.parametrize('remap', remaps)
def test_remapping(remap, tmp_path):
    # Create networks
    source = remap[0](1000)
    target = remap[1](20)

    # Save weights
    weight_file = str(tmp_path / 'weights.pt')
    source.save(weight_file, remap=remap[2])

    # Check that there are only missing layers and no wrong layers in weight file
    weight_keys = list(torch.load(weight_file, 'cpu').keys())
    weight_keys.remove('_LN_MODEL_VERSION')

    target_keys = target.state_dict().keys()
    assert len(set(weight_keys) - set(target_keys)) == 0

    # Check if loading works
    target.load(weight_file, strict=False)


# All remaps tested?
def test_all_remaps_tested():
    networks = [
        getattr(ln.models, net) for net in dir(ln.models)
        if (inspect.isclass(getattr(ln.models, net)))
        and (issubclass(getattr(ln.models, net), torch.nn.Module))
    ]

    for net in networks:
        net_remaps = [
            (r, getattr(net, r)) for r in dir(net)
            if r.startswith('remap') and not re.match(r'^remap_v\d+$', r)
        ]
        tested_remaps = [r[2] for r in remaps if r[1] == net]

        for remap in net_remaps:
            if remap[1] in remap_skips:
                continue
            if remap[1] not in tested_remaps:
                raise NotImplementedError(f'Remap [{remap[0]}] of Network [{net.__name__}] is not being tested!')
