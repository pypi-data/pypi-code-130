_base_ = [
    '../_base_/models/mobilenet_liteaspp_cross_se.py', '../_base_/datasets/pascal_voc12.py',
    '../_base_/default_runtime.py', '../_base_/schedules/schedule_80k.py'
]
model = dict(decode_head=dict(num_classes=21))
norm_cfg = dict(type='BN', eps=0.001, requires_grad=True)
# Re-config the data sampler.
optimizer = dict(type='SGD', lr=0.0025, momentum=0.9, weight_decay=0.0005)
data = dict(samples_per_gpu=4, workers_per_gpu=4)
