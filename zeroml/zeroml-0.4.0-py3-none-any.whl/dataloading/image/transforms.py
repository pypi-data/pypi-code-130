from typing import List, Union

import albumentations as A
from albumentations.pytorch.transforms import ToTensorV2
from timm.models.registry import _model_default_cfgs


def build_post_transform(model: str, mean=(0.485, 0.456, 0.406), std=(0.229, 0.224, 0.225)):
    if model:
        cfg = _model_default_cfgs[model.split("timm/")[-1] if "timm/" in model else model]
        mean = cfg["mean"]
        std = cfg["std"]
        print("Using data config", cfg)

    return [A.Normalize(mean=mean, std=std), ToTensorV2()]


def build_pre_transform(size):
    pre_transform = [A.LongestMaxSize(size), A.PadIfNeeded(size, size, border_mode=0)]
    return pre_transform


def timm_inference_transform(model_name, image_size=224):
    post_transform = build_post_transform(model_name)
    pre_transform = [
        A.LongestMaxSize(image_size),
        A.PadIfNeeded(image_size, image_size, border_mode=0),
    ]

    return A.Compose([*pre_transform, *post_transform])


def get_augment(augment_level: str) -> List[A.BasicTransform]:
    if augment_level not in AUGMENTATIONS:
        raise ValueError(f"Augmentation strategy has to be one of {AUGMENTATIONS.keys()}")
    return AUGMENTATIONS[augment_level]


def build_visualize_transform(size, augment_level: str):
    pre_transform = build_pre_transform(size)
    augment_transform = get_augment(augment_level)

    return A.Compose([*pre_transform, *augment_transform])


def build_training_transform(size, model, augment: Union[str, A.Compose]) -> A.Compose:

    pre_transform = build_pre_transform(size)
    post_transform = build_post_transform(model)
    if isinstance(augment, str):
        augment_transform = get_augment(augment)
    else:
        augment_transform = augment
    return A.Compose([*pre_transform, *augment_transform, *post_transform])


def build_inference_transform(model: str, size=224) -> A.Compose:
    pre_transform = build_pre_transform(size)
    post_transform = build_post_transform(model)
    return A.Compose([*pre_transform, *post_transform])


def build_eval_transform(model, size) -> A.Compose:
    pre_transform = build_pre_transform(size)
    post_transform = build_post_transform(model)

    return A.Compose([*pre_transform, *post_transform])


AUGMENTATIONS = {
    "hard_1": [
        A.RandomRotate90(),
        A.Flip(),
        A.Transpose(),
        A.OneOf(
            [
                A.IAAAdditiveGaussianNoise(),
                A.GaussNoise(),
            ],
            p=0.2,
        ),
        A.OneOf(
            [
                A.MotionBlur(p=0.2),
                A.MedianBlur(blur_limit=3, p=0.1),
                A.Blur(blur_limit=3, p=0.1),
            ],
            p=0.2,
        ),
        A.ShiftScaleRotate(shift_limit=0.0625, scale_limit=0.2, rotate_limit=45, p=0.2),
        A.OneOf(
            [
                A.OpticalDistortion(p=0.3),
                A.GridDistortion(p=0.1),
                A.IAAPiecewiseAffine(p=0.3),
            ],
            p=0.2,
        ),
        A.OneOf(
            [
                A.CLAHE(clip_limit=2),
                A.IAASharpen(),
                A.IAAEmboss(),
                A.RandomBrightnessContrast(),
            ],
            p=0.3,
        ),
        A.HueSaturationValue(p=0.3),
    ],
    "medium": [
        A.OneOf(
            [
                A.IAAAdditiveGaussianNoise(),
                A.GaussNoise(),
            ],
            p=0.2,
        ),
        A.OneOf(
            [
                A.MotionBlur(p=0.2),
                A.MedianBlur(blur_limit=3, p=0.1),
                A.Blur(blur_limit=3, p=0.1),
            ],
            p=0.2,
        ),
        A.ShiftScaleRotate(shift_limit=0.0625, scale_limit=0.2, rotate_limit=45, p=0.2),
        A.OneOf(
            [
                A.OpticalDistortion(p=0.3),
                A.GridDistortion(p=0.1),
                A.IAAPiecewiseAffine(p=0.3),
            ],
            p=0.2,
        ),
        A.OneOf(
            [
                A.CLAHE(clip_limit=2),
                A.IAASharpen(),
                A.IAAEmboss(),
                A.RandomBrightnessContrast(),
            ],
            p=0.3,
        ),
        A.HueSaturationValue(p=0.3),
        A.CoarseDropout(
            max_holes=1,
            max_height=100,
            max_width=50,
            p=0.66,
            min_holes=1,
            min_height=50,
            min_width=20,
        ),
        A.JpegCompression(),
    ],
    "medium3": [
        A.OneOf(
            [
                A.IAAAdditiveGaussianNoise(),
                A.GaussNoise(),
            ],
            p=0.5,
        ),
        A.OneOf(
            [
                A.MotionBlur(blur_limit=15, p=1),
                A.MedianBlur(blur_limit=15, p=1),
                A.Blur(blur_limit=15, p=1),
            ],
            p=1,
        ),
        A.ShiftScaleRotate(shift_limit=0.0625, scale_limit=0.1, rotate_limit=15, p=0.2),
        A.OneOf(
            [
                A.CLAHE(clip_limit=2),
                A.IAASharpen(),
                A.IAAEmboss(),
                A.RandomBrightnessContrast(),
            ],
            p=0.3,
        ),
        A.HueSaturationValue(p=0.3),
        A.CoarseDropout(
            max_holes=1,
            max_height=100,
            max_width=50,
            p=0.66,
            min_holes=1,
            min_height=50,
            min_width=20,
        ),
        A.JpegCompression(),
    ],
    "medium2": [
        A.OneOf(
            [
                A.IAAAdditiveGaussianNoise(),
                A.GaussNoise(),
            ],
            p=0.5,
        ),
        A.OneOf(
            [
                A.MotionBlur(p=0.2),
                A.MedianBlur(blur_limit=3, p=0.1),
                A.Blur(blur_limit=3, p=0.1),
            ],
            p=0.5,
        ),
        A.ShiftScaleRotate(shift_limit=0.0625, scale_limit=0.2, rotate_limit=15, p=0.2),
        A.OneOf(
            [
                A.OpticalDistortion(p=0.3),
                A.GridDistortion(p=0.1),
                A.IAAPiecewiseAffine(p=0.3),
            ],
            p=0.5,
        ),
        A.OneOf(
            [
                A.CLAHE(clip_limit=2),
                A.IAASharpen(),
                A.IAAEmboss(),
                A.RandomBrightnessContrast(),
            ],
            p=0.3,
        ),
        A.HueSaturationValue(p=0.3),
        A.CoarseDropout(
            max_holes=1,
            max_height=100,
            max_width=50,
            p=0.66,
            min_holes=1,
            min_height=50,
            min_width=20,
        ),
        A.JpegCompression(),
        A.HorizontalFlip(p=0.33),
    ],
    "medium2_strong_blur": [
        A.OneOf(
            [
                A.IAAAdditiveGaussianNoise(),
                A.GaussNoise(),
            ],
            p=0.5,
        ),
        A.OneOf(
            [
                # A.MotionBlur(p=0.2),
                # A.MedianBlur(blur_limit=3, p=0.1),
                A.Blur(blur_limit=(9, 11), p=1),
            ],
            p=1,
        ),
        A.ShiftScaleRotate(shift_limit=0.0625, scale_limit=0.2, rotate_limit=15, p=0.2),
        A.OneOf(
            [
                A.OpticalDistortion(p=0.3),
                A.GridDistortion(p=0.1),
                A.IAAPiecewiseAffine(p=0.3),
            ],
            p=0.5,
        ),
        A.OneOf(
            [
                A.CLAHE(clip_limit=2),
                A.IAASharpen(),
                A.IAAEmboss(),
                A.RandomBrightnessContrast(),
            ],
            p=0.3,
        ),
        A.HueSaturationValue(p=0.3),
        A.CoarseDropout(
            max_holes=1,
            max_height=100,
            max_width=50,
            p=0.66,
            min_holes=1,
            min_height=50,
            min_width=20,
        ),
        A.JpegCompression(),
        A.HorizontalFlip(p=0.33),
    ],
    "medium4": [
        A.OneOf(
            [
                A.IAAAdditiveGaussianNoise(),
                A.GaussNoise(),
            ],
            p=0.5,
        ),
        A.OneOf(
            [
                A.MotionBlur(p=0.2),
                A.MedianBlur(blur_limit=7, p=0.1),
                A.Blur(blur_limit=7, p=0.1),
            ],
            p=0.5,
        ),
        A.ShiftScaleRotate(shift_limit=0.0625, scale_limit=0.2, rotate_limit=15, p=0.2, border_mode=0),
        A.OneOf(
            [
                A.CLAHE(clip_limit=2),
                A.IAASharpen(),
                A.IAAEmboss(),
                A.RandomBrightnessContrast(),
                A.ColorJitter(),
                A.ToGray(),
            ],
            p=0.3,
        ),
        A.HueSaturationValue(p=0.3),
        A.CoarseDropout(
            max_holes=2,
            max_height=100,
            max_width=50,
            p=0.66,
            min_holes=1,
            min_height=50,
            min_width=20,
        ),
        A.JpegCompression(),
        A.HorizontalFlip(p=0.33),
    ],
    "easy_2": [A.RandomBrightnessContrast()],
    "noaug": [],
    "new": [
        A.IAAAdditiveGaussianNoise(p=0.5),
        A.IAASuperpixels(p=1),
        A.ImageCompression(p=1),
        A.IAAPerspective(p=1),
        A.RGBShift(r_shift_limit=50, b_shift_limit=50, g_shift_limit=50, p=1),
        A.Posterize(p=1, num_bits=3),
        A.IAAAdditiveGaussianNoise(p=1, loc=0, scale=(30, 50)),
    ],
    "kaggle": [
        # A.HorizontalFlip(p=0.5),
        A.OneOf(
            [
                A.CLAHE(clip_limit=2),
                A.IAASharpen(),
                A.IAAEmboss(),
                A.RandomBrightnessContrast(),
            ],
            p=0.3,
        ),
        A.OneOf(
            [
                A.IAAAdditiveGaussianNoise(),
                A.GaussNoise(),
            ],
            p=0.5,
        ),
        A.OneOf(
            [
                A.MotionBlur(p=0.2),
                A.MedianBlur(blur_limit=7, p=0.1),
                A.Blur(blur_limit=7, p=0.1),
            ],
            p=0.5,
        ),
        A.HueSaturationValue(p=0.3),
        A.RGBShift(r_shift_limit=10, b_shift_limit=10, g_shift_limit=10, p=0.1),
        A.ImageCompression(quality_lower=50, quality_upper=100),
        A.ShiftScaleRotate(shift_limit=0.1, scale_limit=0.1, rotate_limit=10, border_mode=0, p=0.5),
    ],
}
