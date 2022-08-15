# model set tings
norm_cfg = dict(type='BN', eps=0.001, requires_grad=True)
model = dict(
    type='EncoderDecoder',
    backbone=dict(
        type='STDCNet',
        stdc_type='STDCNet1',
        # out_indices=(1, 3, 16),
        in_channels=3,
        channels=(32, 64, 256, 512, 1024),
        bottleneck_type='cat',
        act_cfg=dict(type='ReLU'),
        norm_cfg=norm_cfg),
    decode_head=dict(
        type='BiseNetASPPHead',
        # in_channels=(16, 24, 960),
        # in_index=(0, 1, 2),
        in_channels=(256, 512, 1024),
        in_index=(0, 1, 2,),
        channels=256,
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
