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
from mmseg.apis import inference_segmentor_cam, init_segmentor_cam, show_result_pyplot
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
from mmseg.apis import inference_segmentor, init_segmentor, show_result_pyplot
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
parser = ArgumentParser()
parser.add_argument('--img', help='Image file',default='E:/pycharmwork/canny/image/car.jpg')
parser.add_argument('--config', help='Config file',
                    default='E:/AI/project/mmsegmentation/configs/bisenet_liteaspp_cross_cbam/bisenet_liteaspp_cross_cbam_512x512_80k_voc.py')
parser.add_argument('--checkpoint', help='Checkpoint file',
                    default='E:/AI/project/mmsegmentation/work_dirs/bisenet_liteaspp_cross_cbam_512x512_80k_voc/iter_80000.pth')
parser.add_argument(
    '--device', default='cuda:0', help='Device used for inference')
parser.add_argument(
    '--palette',
    default='cityscapes',
    help='Color palette used for segmentation map')
parser.add_argument(
    '--opacity',
    type=float,
    default=0.5,
    help='Opacity of painted segmentation map. In (0, 1] range.')

args = parser.parse_args()
cfg = Config.fromfile(args.config)
img_path = "E:/pycharmwork/canny/image/car.jpg"
assert os.path.exists(img_path), "file: '{}' dose not exist.".format(img_path)
img = Image.open(img_path).convert('RGB')
img = F.resize(img,(512,500))
img = np.array(img, dtype=np.uint8)
rgb_img = np.float32(img) / 255
model = init_segmentor(args.config, args.checkpoint, device=args.device)
# test a single image

result = inference_segmentor(model, args.img)

result = torch.tensor(result)
print(result.shape)
result = result.long()
print(result)
# print(f"读取的数据={data_loaders}")

# input_tensor = preprocess_image(rgb_img,
#                                 mean=[0.485, 0.456, 0.406],
#                                 std=[0.229, 0.224, 0.225])

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

normalized_masks = torch.nn.functional.softmax(result).cpu()
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


target_layers = [model.decode_head.penultimate_conv]
targets = [SemanticSegmentationTarget(car_category, car_mask_float)]
with GradCAM(model=model,
             target_layers=target_layers,
             use_cuda=torch.cuda.is_available()) as cam:
    # grayscale_cam = cam(input_tensor=result, targets=targets)[0, :]
    cam_image = show_cam_on_image(img.astype(dtype=np.float32) / 255., result, use_rgb=True)

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
