from pytorch_grad_cam import GradCAM, ScoreCAM, GradCAMPlusPlus, AblationCAM, XGradCAM, EigenCAM, FullGrad
from pytorch_grad_cam.utils.model_targets import ClassifierOutputTarget
from pytorch_grad_cam.utils.image import show_cam_on_image,preprocess_image
from mmseg.datasets import build_dataloader, build_dataset
import numpy as np
import torch
from mmcv.runner import get_dist_info, init_dist
import argparse
import warnings
from mmseg.apis import init_random_seed, set_random_seed, train_segmentor
from mmseg.models import build_segmentor
from argparse import ArgumentParser
from mmseg.apis import inference_segmentor, init_segmentor, show_result_pyplot
from mmseg.core.evaluation import get_palette
from PIL import Image
import matplotlib.pyplot as plt
from torchvision import transforms
from torchvision.models.segmentation import deeplabv3_resnet50
import os
from mmcv.utils import Config, DictAction, get_git_hash
from torchvision.transforms import functional as F
import mmcv
import torch
import argparse
import copy
import os
import os.path as osp
import time
import warnings

import mmcv
import torch
import torch.distributed as dist
from mmcv.cnn.utils import revert_sync_batchnorm
from mmcv.runner import get_dist_info, init_dist
from mmcv.utils import Config, DictAction, get_git_hash

from mmseg import __version__
from mmseg.apis import init_random_seed, set_random_seed, train_segmentor
from mmseg.datasets import build_dataset
from mmseg.models import build_segmentor
from mmseg.utils import collect_env, get_root_logger, setup_multi_processes
from mmseg.datasets import build_dataset
from get_test_data import get_test_data
# parser = ArgumentParser()
# parser.add_argument('--img', help='Image file',default='E:/pycharmwork/canny/image/car.jpg')
# parser.add_argument('--config', help='Config file',default='E:/AI/project/mmsegmentation-master/configs/mobilenet_v3/mobilenetv3_aspp_cam.py')
# parser.add_argument('--checkpoint', help='Checkpoint file',default='E:/AI/project/mmsegmentation-master/work_dirs/mobilnetv3_aspp/iter_76000.pth')
# parser.add_argument(
#     '--device', default='cuda:0', help='Device used for inference')
# parser.add_argument(
#     '--palette',
#     default='cityscapes',
#     help='Color palette used for segmentation map')
# parser.add_argument(
#     '--opacity',
#     type=float,
#     default=0.5,
#     help='Opacity of painted segmentation map. In (0, 1] range.')
# group_gpus = parser.add_mutually_exclusive_group()
# group_gpus.add_argument(
#     '--gpus',
#     type=int,
#     help='(Deprecated, please use --gpu-id) number of gpus to use '
#     '(only applicable to non-distributed training)')
# group_gpus.add_argument(
#     '--gpu-ids',
#     type=int,
#     nargs='+',
#     help='(Deprecated, please use --gpu-id) ids of gpus to use '
#     '(only applicable to non-distributed training)')
# group_gpus.add_argument(
#     '--gpu-id',
#     type=int,
#     default=0,
#     help='id of gpu to use '
#     '(only applicable to non-distributed training)')
# args = parser.parse_args()
def parse_args():
    parser = argparse.ArgumentParser(description='Train a segmentor')
    parser.add_argument('--config', help='train config file path',
                        default='E:/AI/project/mmsegmentation/configs/bisenet_liteaspp_cross_cbam/bisenet_liteaspp_cross_cbam_512x512_80k_voc.py')
    parser.add_argument('--work-dir', help='the dir to save logs and models')
    parser.add_argument('--img', help='Image file',
                        default='E:/pycharmwork/canny/image/car.jpg')
    parser.add_argument(
        '--load-from', help='the checkpoint file to load weights from')
    parser.add_argument(
        '--resume-from', help='the checkpoint file to resume from')
    parser.add_argument(
        '--no-validate',
        action='store_true',
        help='whether not to evaluate the checkpoint during training')
    group_gpus = parser.add_mutually_exclusive_group()
    group_gpus.add_argument(
        '--gpus',
        type=int,
        help='(Deprecated, please use --gpu-id) number of gpus to use '
        '(only applicable to non-distributed training)')
    group_gpus.add_argument(
        '--gpu-ids',
        type=int,
        nargs='+',
        help='(Deprecated, please use --gpu-id) ids of gpus to use '
        '(only applicable to non-distributed training)')
    group_gpus.add_argument(
        '--gpu-id',
        type=int,
        default=0,
        help='id of gpu to use '
        '(only applicable to non-distributed training)')
    parser.add_argument('--seed', type=int, default=None, help='random seed')
    parser.add_argument(
        '--diff_seed',
        action='store_true',
        help='Whether or not set different seeds for different ranks')
    parser.add_argument(
        '--deterministic',
        action='store_true',
        help='whether to set deterministic options for CUDNN backend.')
    parser.add_argument(
        '--options',
        nargs='+',
        action=DictAction,
        help="--options is deprecated in favor of --cfg_options' and it will "
        'not be supported in version v0.22.0. Override some settings in the '
        'used config, the key-value pair in xxx=yyy format will be merged '
        'into config file. If the value to be overwritten is a list, it '
        'should be like key="[a,b]" or key=a,b It also allows nested '
        'list/tuple values, e.g. key="[(a,b),(c,d)]" Note that the quotation '
        'marks are necessary and that no white space is allowed.')
    parser.add_argument(
        '--cfg-options',
        nargs='+',
        action=DictAction,
        help='override some settings in the used config, the key-value pair '
        'in xxx=yyy format will be merged into config file. If the value to '
        'be overwritten is a list, it should be like key="[a,b]" or key=a,b '
        'It also allows nested list/tuple values, e.g. key="[(a,b),(c,d)]" '
        'Note that the quotation marks are necessary and that no white space '
        'is allowed.')
    parser.add_argument(
        '--launcher',
        choices=['none', 'pytorch', 'slurm', 'mpi'],
        default='none',
        help='job launcher')
    parser.add_argument('--local_rank', type=int, default=0)
    parser.add_argument(
        '--auto-resume',
        action='store_true',
        help='resume from the latest checkpoint automatically.')
    args = parser.parse_args()
    if 'LOCAL_RANK' not in os.environ:
        os.environ['LOCAL_RANK'] = str(args.local_rank)

    if args.options and args.cfg_options:
        raise ValueError(
            '--options and --cfg-options cannot be both '
            'specified, --options is deprecated in favor of --cfg-options. '
            '--options will not be supported in version v0.22.0.')
    if args.options:
        warnings.warn('--options is deprecated in favor of --cfg-options. '
                      '--options will not be supported in version v0.22.0.')
        args.cfg_options = args.options

    return args


args = parse_args()
cfg = Config.fromfile(args.config)
if args.cfg_options is not None:
    cfg.merge_from_dict(args.cfg_options)

# set cudnn_benchmark
if cfg.get('cudnn_benchmark', False):
    torch.backends.cudnn.benchmark = True

# work_dir is determined in this priority: CLI > segment in file > filename
if args.work_dir is not None:
    # update configs according to CLI args if args.work_dir is not None
    cfg.work_dir = args.work_dir
elif cfg.get('work_dir', None) is None:
    # use config filename as default work_dir if cfg.work_dir is None
    cfg.work_dir = osp.join('./work_dirs',
                            osp.splitext(osp.basename(args.config))[0])
if args.load_from is not None:
    cfg.load_from = args.load_from
if args.resume_from is not None:
    cfg.resume_from = args.resume_from
if args.gpus is not None:
    cfg.gpu_ids = range(1)
    warnings.warn('`--gpus` is deprecated because we only support '
                  'single GPU mode in non-distributed training. '
                  'Use `gpus=1` now.')
if args.gpu_ids is not None:
    cfg.gpu_ids = args.gpu_ids[0:1]
    warnings.warn('`--gpu-ids` is deprecated, please use `--gpu-id`. '
                  'Because we only support single GPU mode in '
                  'non-distributed training. Use the first GPU '
                  'in `gpu_ids` now.')
if args.gpus is None and args.gpu_ids is None:
    cfg.gpu_ids = [args.gpu_id]

cfg.auto_resume = args.auto_resume

# init distributed env first, since logger depends on the dist info.
if args.launcher == 'none':
    distributed = False
else:
    distributed = True
    init_dist(args.launcher, **cfg.dist_params)
    # gpu_ids is used to calculate iter when resuming checkpoint
    _, world_size = get_dist_info()
    cfg.gpu_ids = range(world_size)

# create work_dir
mmcv.mkdir_or_exist(osp.abspath(cfg.work_dir))
# dump config
cfg.dump(osp.join(cfg.work_dir, osp.basename(args.config)))
# init the logger before other steps
timestamp = time.strftime('%Y%m%d_%H%M%S', time.localtime())
log_file = osp.join(cfg.work_dir, f'{timestamp}.log')
logger = get_root_logger(log_file=log_file, log_level=cfg.log_level)

# set multi-process settings
setup_multi_processes(cfg)

# init the meta dict to record some important information such as
# environment info and seed, which will be logged
meta = dict()
# log env info
env_info_dict = collect_env()
env_info = '\n'.join([f'{k}: {v}' for k, v in env_info_dict.items()])
dash_line = '-' * 60 + '\n'
logger.info('Environment info:\n' + dash_line + env_info + '\n' +
            dash_line)
meta['env_info'] = env_info

# log some basic info
logger.info(f'Distributed training: {distributed}')
logger.info(f'Config:\n{cfg.pretty_text}')

# set random seeds
seed = init_random_seed(args.seed)
seed = seed + dist.get_rank() if args.diff_seed else seed
logger.info(f'Set random seed to {seed}, '
            f'deterministic: {args.deterministic}')
set_random_seed(seed, deterministic=args.deterministic)
cfg.seed = seed
meta['seed'] = seed
meta['exp_name'] = osp.basename(args.config)

model = build_segmentor(
    cfg.model,
    train_cfg=cfg.get('train_cfg'),
    test_cfg=cfg.get('test_cfg'))
model.init_weights()

# SyncBN is not support for DP
if not distributed:
    warnings.warn(
        'SyncBN is only supported with DDP. To be compatible with DP, '
        'we convert SyncBN to BN. Please use dist_train.sh which can '
        'avoid this error.')
    model = revert_sync_batchnorm(model)

logger.info(model)

datasets = [build_dataset(cfg.data.train)]
if len(cfg.workflow) == 2:
    val_dataset = copy.deepcopy(cfg.data.val)
    val_dataset.pipeline = cfg.data.train.pipeline
    datasets.append(build_dataset(val_dataset))
if cfg.checkpoint_config is not None:
    # save mmseg version, config file content and class names in
    # checkpoints as meta data
    cfg.checkpoint_config.meta = dict(
        mmseg_version=f'{__version__}+{get_git_hash()[:7]}',
        config=cfg.pretty_text,
        CLASSES=datasets[0].CLASSES,
        PALETTE=datasets[0].PALETTE)
# add an attribute for visualization convenience
model.CLASSES = datasets[0].CLASSES
# passing checkpoint meta for saving best checkpoint

from mmseg.apis import inference_segmentor_cam
meta.update(cfg.checkpoint_config.meta)
data_loaders = [
        build_dataloader(
            ds,
            cfg.data.samples_per_gpu,
            cfg.data.workers_per_gpu,
            # cfg.gpus will be ignored if distributed
            len(cfg.gpu_ids),
            dist=distributed,
            seed=cfg.seed,
            drop_last=True) for ds in datasets
    ]
out_put = model(*data_loaders)
for i in data_loaders:
    if i == 'img':
        print(f"i={i}")
# train_segmentor(
#     model,
#     datasets,
#     cfg,
#     distributed=distributed,
#     validate=(not args.no_validate),
#     timestamp=timestamp,
#     meta=meta)



# print(f"读取的数据={data_loaders}")
# img_path = "E:/pycharmwork/canny/image/car.jpg"
# assert os.path.exists(img_path), "file: '{}' dose not exist.".format(img_path)
# img = Image.open(img_path).convert('RGB')
# img = F.resize(img,(500,500))
# img = np.array(img, dtype=np.uint8)
# rgb_img = np.float32(img) / 255
# input_tensor = preprocess_image(rgb_img,
#                                 mean=[0.485, 0.456, 0.406],
#                                 std=[0.229, 0.224, 0.225])
model.eval()

# if torch.cuda.is_available():
#     model = model.cuda()
#     input_tensor = input_tensor.cuda()

# output = model(*data_loaders)
# print(f"经过模型后output={output}")


# target_layers = [model.backbone.backbone.stages[-1]]
# print(target_layers)
# data_transform = transforms.Compose([transforms.ToTensor(),
#                                     transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])])
# load image


# input_tensor = input_tensor.cuda()
# img = Image.open(img_path).convert('RGB')
# img = np.array(img, dtype=np.uint8)

# [C, H, W]
# img_tensor = data_transform(img)
# input_tensor = torch.unsqueeze(img_tensor, dim=0) # Create an input tensor image for your model..

# Note: input_tensor can be a batch tensor with several images!
# class SegmentationModelOutputWrapper(torch.nn.Module):
#     def __init__(self, model):
#         super(SegmentationModelOutputWrapper, self).__init__()
#         self.model = model
#
#     def forward(self, x):
#         return self.model(x)["out"]
#
#
# model = SegmentationModelOutputWrapper(model)
# output = model(**data)

normalized_masks = torch.nn.functional.softmax(output, dim=1).cpu()
sem_classes = [
    '__background__', 'aeroplane', 'bicycle', 'bird', 'boat', 'bottle', 'bus',
    'car', 'cat', 'chair', 'cow', 'diningtable', 'dog', 'horse', 'motorbike',
    'person', 'pottedplant', 'sheep', 'sofa', 'train', 'tvmonitor'
]
sem_class_to_idx = {cls: idx for (idx, cls) in enumerate(sem_classes)}

car_category = sem_class_to_idx["car"]
car_mask = normalized_masks[0, :, :, :].argmax(axis=0).detach().cpu().numpy()
car_mask_uint8 = 255 * np.uint8(car_mask == car_category)
car_mask_float = np.float32(car_mask == car_category)

both_images = np.hstack((img, np.repeat(car_mask_uint8[:, :, None], 3, axis=-1)))
Image.fromarray(both_images)


from pytorch_grad_cam import GradCAM
class SemanticSegmentationTarget:
    def __init__(self, category, mask):
        self.category = category
        self.mask = torch.from_numpy(mask)
        if torch.cuda.is_available():
            self.mask = self.mask.cuda()

    def __call__(self, model_output):
        return (model_output[self.category, :, :] * self.mask).sum()


target_layers = [model.model.backbone.layer4]
targets = [SemanticSegmentationTarget(car_category, car_mask_float)]
with GradCAM(model=model,
             target_layers=target_layers,
             use_cuda=torch.cuda.is_available()) as cam:
    grayscale_cam = cam(input_tensor=input_tensor, targets=targets)[0, :]
    cam_image = show_cam_on_image(img.astype(dtype=np.float32) / 255., grayscale_cam, use_rgb=True)

Image.fromarray(cam_image)

plt.imshow(cam_image)
plt.show()



# # Construct the CAM object once, and then re-use it on many images:
# cam = GradCAM(model=model, target_layers=target_layers, use_cuda=True)
#
# # You can also use it within a with statement, to make sure it is freed,
# # In case you need to re-create it inside an outer loop:
# # with GradCAM(model=model, target_layers=target_layers, use_cuda=args.use_cuda) as cam:
# #   ...
#
# # We have to specify the target we want to generate
# # the Class Activation Maps for.
# # If targets is None, the highest scoring category
# # will be used for every image in the batch.
# # Here we use ClassifierOutputTarget, but you can define your own custom targets
# # That are, for example, combinations of categories, or specific outputs in a non standard model.
# targets = [0]
#
# # You can also pass aug_smooth=True and eigen_smooth=True, to apply smoothing.
# grayscale_cam = cam(input_tensor=input_tensor, targets=targets)
#
# # In this example grayscale_cam has only one image in the batch:
# grayscale_cam = grayscale_cam[0, :]
# visualization = show_cam_on_image(img.astype(dtype=np.float32) / 255., grayscale_cam, use_rgb=True)
# plt.imshow(visualization)
# plt.show()
