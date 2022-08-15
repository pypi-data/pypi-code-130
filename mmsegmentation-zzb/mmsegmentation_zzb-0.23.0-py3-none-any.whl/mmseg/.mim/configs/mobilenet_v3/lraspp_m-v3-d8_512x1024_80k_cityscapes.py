_base_ = [
    '../_base_/models/lraspp_m-v3-d8.py', '../_base_/datasets/cityscapes.py',
    '../_base_/default_runtime.py', '../_base_/schedules/schedule_80k.py'
]

# model = dict(pretrained='open-mmlab://contrib/mobilenet_v3_large')

# Re-config the data sampler.
data = dict(samples_per_gpu=2, workers_per_gpu=2)
optimizer = dict(type='SGD', lr=0.005, momentum=0.9, weight_decay=0.0005)
norm_cfg = dict(type='SyncBN', eps=0.001, requires_grad=True)
runner = dict(type='IterBasedRunner', max_iters=80000)
checkpoint_config = dict(by_epoch=False, interval=8000)
evaluation = dict(interval=8000, metric='mIoU', pre_eval=True)