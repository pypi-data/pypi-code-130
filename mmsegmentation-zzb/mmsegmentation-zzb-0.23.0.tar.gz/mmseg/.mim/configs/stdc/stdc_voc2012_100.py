_base_ = [
    '../_base_/models/stdc_voc.py', '../_base_/datasets/pascal_voc12.py',
    '../_base_/default_runtime.py', '../_base_/schedules/schedule_80k.py'
]
optimizer = dict(lr=0.05)
lr_config = dict(warmup='linear', warmup_iters=1000)
data = dict(
    samples_per_gpu=16,
    workers_per_gpu=2,
)

