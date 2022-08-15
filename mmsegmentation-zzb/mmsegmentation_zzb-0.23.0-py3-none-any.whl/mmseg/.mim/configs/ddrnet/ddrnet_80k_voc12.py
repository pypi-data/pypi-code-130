# _base_ = [
#     '../_base_/datasets/pascal_voc12.py',
#     '../_base_/default_runtime.py', '../_base_/schedules/schedule_80k.py'
# ]
# # model settings
# from mmseg.models.backbones.ddrnet import BasicBlock
# norm_cfg = dict(type='BN', requires_grad=True)
# model = dict(
#     type='EncoderDecoder',
#     pretrained=None,
#     backbone=dict(
#         type='ResNetV1c',
#         depth=18,
#         num_stages=4,
#         out_indices=(0, 1, 2, 3),
#         strides=(1, 2, 1, 1),
#         norm_cfg=norm_cfg,
#         norm_eval=False,
#         style='pytorch'),
#     decode_head=dict(
#         type='DdrNetHead',
#         in_channels=21,
#         in_index=0,
#         channels=21,
#         dropout_ratio=0.1,
#         num_classes=21,
#         norm_cfg=norm_cfg,
#         align_corners=False,
#         loss_decode=dict(
#             type='CrossEntropyLoss', use_sigmoid=False, loss_weight=1.0)),
#     # auxiliary_head=dict(
#     #     type='FCNHead',
#     #     in_channels=1024,
#     #     in_index=2,
#     #     channels=256,
#     #     num_convs=1,
#     #     concat_input=False,
#     #     dropout_ratio=0.1,
#     #     num_classes=19,
#     #     norm_cfg=norm_cfg,
#     #     align_corners=False,
#     #     loss_decode=dict(
#     #         type='CrossEntropyLoss', use_sigmoid=False, loss_weight=0.4)),
#     # model training and testing settings
#     train_cfg=dict(),
#     test_cfg=dict(mode='whole'))
_base_ = [
    '../_base_/datasets/pascal_voc12.py',
    '../_base_/default_runtime.py', '../_base_/schedules/schedule_80k.py'
]
# model settings
optimizer = dict(type='SGD', lr=0.01, momentum=0.9, weight_decay=0.0005)
norm_cfg = dict(type='BN', requires_grad=True)
data = dict(
    samples_per_gpu=4,
    workers_per_gpu=4,)
model = dict(
    type='EncoderDecoder',
    pretrained=None,
    backbone=dict(
        type='DualResNet',
        depth=18,
        num_stages=2,
        out_indices=(0, 1),
        dilations=(1, 1),
        strides=(1, 2),
        norm_cfg=norm_cfg,
        norm_eval=False,
        style='pytorch',
        contract_dilation=True),
    decode_head=dict(
        type='FCNHead',
        in_channels=256,
        in_index=1,
        channels=128,
        dropout_ratio=0.1,
        num_classes=21,
        norm_cfg=norm_cfg,
        align_corners=False,
        loss_decode=dict(
            type='CrossEntropyLoss', use_sigmoid=False, loss_weight=1.0)),
    auxiliary_head=dict(
        type='FCNHead',
        in_channels=64,
        in_index=0,
        channels=32,
        num_convs=1,
        concat_input=False,
        dropout_ratio=0.1,
        num_classes=21,
        norm_cfg=norm_cfg,
        align_corners=False,
        loss_decode=dict(
            type='CrossEntropyLoss', use_sigmoid=False, loss_weight=0.4)),
    # model training and testing settings
    train_cfg=dict(),
    test_cfg=dict(mode='whole'))

