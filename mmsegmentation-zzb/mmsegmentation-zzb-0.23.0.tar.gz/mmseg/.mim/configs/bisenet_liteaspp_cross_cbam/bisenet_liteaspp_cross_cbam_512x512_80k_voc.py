_base_ = [
    '../_base_/datasets/pascal_voc12.py',
    '../_base_/default_runtime.py', '../_base_/schedules/schedule_80k.py'
]
model = dict(decode_head=dict(num_classes=21))
norm_cfg = dict(type='BN', eps=0.001, requires_grad=True)
# Re-config the data sampler.
optimizer = dict(type='SGD', lr=0.0025, momentum=0.9, weight_decay=0.0005)
data = dict(samples_per_gpu=8, workers_per_gpu=8)
# model set tings
# type表示的都是类
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
        type='CrosseCbamHead',
        # in_channels=(16, 24, 960),
        # in_index=(0, 1, 2),
        dilations=(1, 3),
        in_channels=(256, 512, 1024),
        in_index=(0, 1, 2,),
        channels=128,
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
