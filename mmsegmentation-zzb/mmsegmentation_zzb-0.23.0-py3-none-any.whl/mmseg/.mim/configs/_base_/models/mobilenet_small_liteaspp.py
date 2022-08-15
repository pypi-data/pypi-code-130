# model settings
norm_cfg = dict(type='BN', eps=0.001, requires_grad=True)
model = dict(
    type='EncoderDecoder',
    backbone=dict(
        type='MyMobileNetV3',
        arch='small',
        # out_indices=(1, 3, 16),
        out_indices=(3, 6, 9, 13),
        norm_cfg=norm_cfg),
    decode_head=dict(
        type='MobilenetSmallASPPHead',
        # in_channels=(16, 24, 960),
        # in_index=(0, 1, 2),
        in_channels=(24, 40, 96, 576),
        in_index=(0, 1, 2, 3),
        channels=40,
        input_transform='multiple_select',
        dropout_ratio=0.1,
        num_classes=21,
        norm_cfg=norm_cfg,
        act_cfg=dict(type='ReLU'),
        align_corners=False,
        loss_decode=dict(
            type='CrossEntropyLoss', use_sigmoid=False, loss_weight=1.0)),
    # model training and testing settings
    train_cfg=dict(),
    test_cfg=dict(mode='whole'))
