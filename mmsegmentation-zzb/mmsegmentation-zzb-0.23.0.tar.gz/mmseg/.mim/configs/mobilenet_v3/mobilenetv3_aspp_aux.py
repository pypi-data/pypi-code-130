_base_ = [
     '../_base_/datasets/pascal_voc12.py',
     '../_base_/default_runtime.py',
     '../_base_/schedules/schedule_80k.py',
     # '../_base_/models/lraspp_m-v3-d8.py',
]
# model settings
norm_cfg = dict(type='BN',requires_grad=True)
optimizer = dict(type='SGD', lr=0.0025, momentum=0.9, weight_decay=0.0005)
model = dict(
    type='EncoderDecoder',
    backbone=dict(
        type='MobileNetV3',
        arch='large',
        out_indices=(1, 3, 16),
        norm_cfg=norm_cfg),
    decode_head=dict(
        type='ASPPHead',
        in_channels=960,
        in_index=2,
        channels=128,
        dilations=(1,12,24,36),
        dropout_ratio=0.1,
        num_classes=21,
        norm_cfg=norm_cfg,
        # act_cfg=dict(type='ReLU'),
        align_corners=False,
        loss_decode=dict(
            type='CrossEntropyLoss', use_sigmoid=False, loss_weight=1.0)),
    # model training and testing settings
    auxiliary_head=dict(
        type='FCNHead',
        in_channels=24,
        channels=12,
        in_index=1,
        num_convs=1,
        concat_input=False,
        dropout_ratio=0.1,
        num_classes=21,
        norm_cfg=norm_cfg,
        align_corners=False,
        loss_decode=dict(
            type='CrossEntropyLoss', use_sigmoid=False, loss_weight=1.0)),
    train_cfg=dict(),
    test_cfg=dict(mode='whole'))
