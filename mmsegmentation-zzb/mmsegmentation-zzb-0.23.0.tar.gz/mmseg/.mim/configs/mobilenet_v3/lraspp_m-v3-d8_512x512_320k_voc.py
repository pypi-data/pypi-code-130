_base_ = [
    '../_base_/models/lraspp_m-v3-d8.py', '../_base_/datasets/pascal_voc12.py',
    '../_base_/default_runtime.py', '../_base_/schedules/schedule_320k.py'
]
norm_cfg = dict(type='SyncBN', eps=0.001, requires_grad=True)
# Re-config the data sampler.
model = dict(decode_head=dict(num_classes=21))
data = dict(samples_per_gpu=4, workers_per_gpu=4)
checkpoint_config = dict(by_epoch=False, interval=8000)
evaluation = dict(interval=8000, metric='mIoU')