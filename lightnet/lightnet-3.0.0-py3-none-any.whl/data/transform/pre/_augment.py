#
#   Lightnet data augmentation
#   Copyright EAVISE
#
import random
import math
import numpy as np
import torch
from lightnet._imports import cv2, Image
from ._base import ImageTransform, ImageAnnoTransform

__all__ = ['RandomFlip', 'RandomHSV', 'RandomJitter', 'RandomRotate']


class RandomFlip(ImageAnnoTransform):
    """ Randomly flip image.

    Args:
        horizontal (Number [0-1]): Chance of flipping the image horizontally
        vertical (Number [0-1], optional): Chance of flipping the image vertically; Default **0**
        kwargs: Passed on to :class:`~lightnet.data.transform.ImageTransform`
    """
    def __init__(self, horizontal, vertical=0, **kwargs):
        super().__init__(**kwargs)
        self.horizontal = horizontal
        self.vertical = vertical

        # parameters
        self._flip_h = False
        self._flip_v = False
        self._img_width = None
        self._img_height = None

    def get_parameters(self, img_width, img_height):
        self._img_width = img_width
        self._img_height = img_height
        self._flip_h = random.random() < self.horizontal
        self._flip_v = random.random() < self.vertical

    @torch.jit.unused
    def _tf_pil(self, img):
        if self._flip_h and self._flip_v:
            img = img.transpose(Image.ROTATE_180)
        elif self._flip_h:
            img = img.transpose(Image.FLIP_LEFT_RIGHT)
        elif self._flip_v:
            img = img.transpose(Image.FLIP_TOP_BOTTOM)

        return img

    @torch.jit.unused
    def _tf_cv(self, img):
        if self._flip_h and self._flip_v:
            img = cv2.flip(img, -1)
        elif self._flip_h:
            img = cv2.flip(img, 1)
        elif self._flip_v:
            img = cv2.flip(img, 0)

        return img

    def _tf_torch(self, img):
        if self._flip_h and self._flip_v:
            img = torch.flip(img, (1, 2))
        elif self._flip_h:
            img = torch.flip(img, (2,))
        elif self._flip_v:
            img = torch.flip(img, (1,))

        return img

    @torch.jit.unused
    def _tf_anno(self, anno):
        if self._flip_h:
            anno['x_top_left'] = self._img_width - anno['x_top_left'] - anno['width']
        if self._flip_v:
            anno['y_top_left'] = self._img_height - anno['y_top_left'] - anno['height']

        if 'segmentation' in anno.columns and (self._flip_h or self._flip_v):
            x, y, xoff, yoff = 1, 1, 0, 0

            if self._flip_h:
                x = -1
                xoff = self._img_width
            if self._flip_v:
                y = -1
                yoff = self._img_height

            anno['segmentation'] = anno['segmentation'].geos.affine((
                x, 0,
                0, y,
                xoff,
                yoff,
            ))

        return anno


class RandomHSV(ImageTransform):
    """ Perform random HSV shift on the RGB data.

    Args:
        hue (Number): Random number between -hue,hue is used to shift the hue
        saturation (Number): Random number between 1,saturation is used to shift the saturation; 50% chance to get 1/dSaturation in stead of dSaturation
        value (Number): Random number between 1,value is used to shift the value; 50% chance to get 1/dValue in stead of dValue
        kwargs: Passed on to :class:`~lightnet.data.transform.ImageTransform`

    Warning:
        If you use OpenCV as your image processing library, make sure the image is RGB before using this transform.
        By default OpenCV uses BGR, so you must use `cvtColor`_ function to transform it to RGB.

    .. _cvtColor: https://docs.opencv.org/3.4/d8/d01/group__imgproc__color__conversions.html#ga397ae87e1288a81d2363b61574eb8cab
    """
    def __init__(self, hue, saturation, value, **kwargs):
        super().__init__(**kwargs)
        self.hue = hue
        self.saturation = saturation
        self.value = value

        # Parameters
        self._dh = None
        self._ds = None
        self._dv = None

    def get_parameters(self, img_width, img_height):
        self._dh = random.uniform(-self.hue, self.hue)

        self._ds = random.uniform(1, self.saturation)
        if random.random() < 0.5:
            self._ds = 1 / self._ds

        self._dv = random.uniform(1, self.value)
        if random.random() < 0.5:
            self._dv = 1 / self._dv

    @torch.jit.unused
    def _tf_pil(self, img):
        img = img.convert('HSV')
        channels = list(img.split())

        channels[0] = channels[0].point(self._wrap_hue_pil)
        channels[1] = channels[1].point(lambda i: min(255, max(0, int(i*self._ds))))
        channels[2] = channels[2].point(lambda i: min(255, max(0, int(i*self._dv))))

        img = Image.merge(img.mode, tuple(channels))
        img = img.convert('RGB')
        return img

    @torch.jit.unused
    def _tf_cv(self, img):
        imgtf = img[:, :, :3]

        imgtf = imgtf.astype(np.float32) / 255.0
        imgtf = cv2.cvtColor(imgtf, cv2.COLOR_RGB2HSV)

        imgtf[:, :, 0] = self._wrap_hue(imgtf[:, :, 0] + (360.0 * self._dh))
        imgtf[:, :, 1] = np.clip(self._ds * imgtf[:, :, 1], 0.0, 1.0)
        imgtf[:, :, 2] = np.clip(self._dv * imgtf[:, :, 2], 0.0, 1.0)

        imgtf = cv2.cvtColor(imgtf, cv2.COLOR_HSV2RGB)
        imgtf = (imgtf * 255).astype(np.uint8)

        img[:, :, :3] = imgtf
        return img

    def _tf_torch(self, img):
        imgtf = img[:3]

        maxval, _ = imgtf.max(0)
        minval, _ = imgtf.min(0)
        diff = maxval - minval

        h = torch.zeros_like(diff)
        mask = (diff != 0) & (maxval == imgtf[0])
        h[mask] = (60 * (imgtf[1, mask] - imgtf[2, mask]) / diff[mask] + 360)
        mask = (diff != 0) & (maxval == imgtf[1])
        h[mask] = (60 * (imgtf[2, mask] - imgtf[0, mask]) / diff[mask] + 120)
        mask = (diff != 0) & (maxval == imgtf[2])
        h[mask] = (60 * (imgtf[0, mask] - imgtf[1, mask]) / diff[mask] + 240)
        h %= 360

        s = torch.zeros_like(diff)
        mask = maxval != 0
        s[mask] = diff[mask] / maxval[mask]

        # Random Shift
        h = self._wrap_hue(h + (360 * self._dh))
        s = torch.clamp(self._ds * s, 0, 1)
        v = torch.clamp(self._dv * maxval, 0, 1)

        # Transform to RGB
        c = v * s
        m = v - c
        x = c * (1 - (((h / 60) % 2) - 1).abs())
        cm = c + m
        xm = x + m

        imgtf = torch.stack((m, m, m))
        mask = (h >= 0) & (h <= 60)
        imgtf[0, mask] = cm[mask]
        imgtf[1, mask] = xm[mask]
        mask = (h > 60) & (h <= 120)
        imgtf[0, mask] = xm[mask]
        imgtf[1, mask] = cm[mask]
        mask = (h > 120) & (h <= 180)
        imgtf[1, mask] = cm[mask]
        imgtf[2, mask] = xm[mask]
        mask = (h > 180) & (h <= 240)
        imgtf[1, mask] = xm[mask]
        imgtf[2, mask] = cm[mask]
        mask = (h > 240) & (h <= 300)
        imgtf[0, mask] = xm[mask]
        imgtf[2, mask] = cm[mask]
        mask = (h > 300) & (h <= 360)
        imgtf[0, mask] = cm[mask]
        imgtf[2, mask] = xm[mask]

        img[:3] = imgtf
        return img

    @torch.jit.unused
    def _wrap_hue_pil(self, x):
        x += int(self._dh * 255)
        if x > 255:
            x -= 255
        elif x < 0:
            x += 255
        return x

    def _wrap_hue(self, h):
        h[h >= 360.0] -= 360.0
        h[h < 0.0] += 360.0
        return h


class RandomJitter(ImageAnnoTransform):
    """ Add random jitter to an image, by randomly cropping (or adding borders) to each side.

    Args:
        jitter (Number [0-1]): Indicates how much of the image we can crop
        fill_color (int or float, optional): Fill color to be used for padding (if int, will be divided by 255); Default **0.5**
        kwargs: Passed on to :class:`~lightnet.data.transform.ImageTransform`

    Warning:
        This transformation only modifies the annotations to fit the new origin point of the image.
        It does not crop the annotations to fit inside the new boundaries, nor does it filter annotations that fall outside of these new boundaries.
        Check out :class:`~lightnet.data.transform.FitAnno` for a transformation that does this.
    """
    def __init__(self, jitter, fill_color=0.5, **kwargs):
        super().__init__(**kwargs)
        self.jitter = jitter
        self.fill_color = fill_color if isinstance(fill_color, float) else fill_color / 255

        # Parameters
        self._img_width = None
        self._img_height = None
        self._crop = None

    def get_parameters(self, img_width, img_height):
        dw, dh = int(img_width * self.jitter), int(img_height * self.jitter)
        crop_left = random.randint(-dw, dw)
        crop_right = random.randint(-dw, dw)
        crop_top = random.randint(-dh, dh)
        crop_bottom = random.randint(-dh, dh)

        self._img_width = img_width
        self._img_height = img_height
        self._crop = (crop_left, crop_top, img_width-crop_right, img_height-crop_bottom)

    @torch.jit.unused
    def _tf_pil(self, img):
        crop_w = self._crop[2] - self._crop[0]
        crop_h = self._crop[3] - self._crop[1]
        shape = np.array(img).shape
        channels = shape[2] if len(shape) > 2 else 1

        img = img.crop((
            max(0, self._crop[0]),
            max(0, self._crop[1]),
            min(self._img_width, self._crop[2]),
            min(self._img_height, self._crop[3]),
        ))
        img_crop = Image.new(img.mode, (crop_w, crop_h), color=(int(self.fill_color*255),)*channels)
        img_crop.paste(img, (max(0, -self._crop[0]), max(0, -self._crop[1])))

        return img_crop

    @torch.jit.unused
    def _tf_cv(self, img):
        crop_w = self._crop[2] - self._crop[0]
        crop_h = self._crop[3] - self._crop[1]
        img_crop = np.ones((crop_h, crop_w) + img.shape[2:], dtype=img.dtype) * int(self.fill_color*255)

        src_x1 = max(0, self._crop[0])
        src_x2 = min(self._crop[2], self._img_width)
        src_y1 = max(0, self._crop[1])
        src_y2 = min(self._crop[3], self._img_height)
        dst_x1 = max(0, -self._crop[0])
        dst_x2 = crop_w - max(0, self._crop[2]-self._img_width)
        dst_y1 = max(0, -self._crop[1])
        dst_y2 = crop_h - max(0, self._crop[3]-self._img_height)
        img_crop[dst_y1:dst_y2, dst_x1:dst_x2] = img[src_y1:src_y2, src_x1:src_x2]

        return img_crop

    def _tf_torch(self, img):
        crop_w = self._crop[2] - self._crop[0]
        crop_h = self._crop[3] - self._crop[1]
        img_crop = torch.full((img.shape[0], crop_h, crop_w), self.fill_color, dtype=img.dtype)

        src_x1 = max(0, self._crop[0])
        src_x2 = min(self._crop[2], self._img_width)
        src_y1 = max(0, self._crop[1])
        src_y2 = min(self._crop[3], self._img_height)
        dst_x1 = max(0, -self._crop[0])
        dst_x2 = crop_w - max(0, self._crop[2]-self._img_width)
        dst_y1 = max(0, -self._crop[1])
        dst_y2 = crop_h - max(0, self._crop[3]-self._img_height)
        img_crop[:, dst_y1:dst_y2, dst_x1:dst_x2] = img[:, src_y1:src_y2, src_x1:src_x2]

        return img_crop

    @torch.jit.unused
    def _tf_anno(self, anno):
        anno.x_top_left -= self._crop[0]
        anno.y_top_left -= self._crop[1]
        if 'segmentation' in anno.columns:
            anno['segmentation'] = anno['segmentation'].geos.translate(-self._crop[0], -self._crop[1])

        return anno


class RandomRotate(ImageAnnoTransform):
    """ Randomly rotate the image/annotations.
    For the annotations we take the smallest possible rectangle that fits the rotated rectangle.

    Args:
        jitter (Number [0-180]): Random number between -jitter,jitter degrees is used to rotate the image
        kwargs: Passed on to :class:`~lightnet.data.transform.ImageTransform`
    """
    def __init__(self, jitter, **kwargs):
        super().__init__(**kwargs)
        self.jitter = jitter

        # Parameters
        self._angle = None
        self._img_width = None
        self._img_height = None

    def get_parameters(self, img_width, img_height):
        self._img_width = img_width
        self._img_height = img_height
        self._angle = random.randint(-self.jitter, self.jitter)

    @torch.jit.unused
    def _tf_pil(self, img):
        return img.rotate(self._angle)

    @torch.jit.unused
    def _tf_cv(self, img):
        M = cv2.getRotationMatrix2D(
            (self._img_width / 2, self._img_height / 2),
            self._angle,
            1,
        )
        return cv2.warpAffine(img, M, (self._img_width, self._img_height))

    @torch.jit.ignore
    def _tf_torch(self, img):
        raise NotImplementedError('Random Rotate is not implemented for torch Tensors, you can use Kornia [https://github.com/kornia/kornia]')

    @torch.jit.unused
    def _tf_anno(self, anno):
        cx, cy = self._img_width/2, self._img_height/2
        rad = math.radians(self.angle)

        if 'segmentation' in anno.columns:
            anno['segmentation'] = anno['segmentation'].geos.rotate(rad, origin=(cx, cy))
            bounds = anno['segmentation'].geos.bounds()
            anno['x_top_left'] = bounds['xmin']
            anno['y_top_left'] = bounds['ymin']
            anno['width'] = bounds['xmax'] - bounds['xmin']
            anno['height'] = bounds['ymax'] - bounds['ymin']
        else:
            cos_a = math.cos(rad)
            sin_a = math.sin(-rad)

            # Rotate anno
            x1_c = anno.x_top_left - cx
            y1_c = anno.y_top_left - cy
            x2_c = x1_c + anno.width
            y2_c = y1_c + anno.height

            x1_r = (x1_c * cos_a - y1_c * sin_a) + cx
            y1_r = (x1_c * sin_a + y1_c * cos_a) + cy
            x2_r = (x2_c * cos_a - y1_c * sin_a) + cx
            y2_r = (x2_c * sin_a + y1_c * cos_a) + cy
            x3_r = (x2_c * cos_a - y2_c * sin_a) + cx
            y3_r = (x2_c * sin_a + y2_c * cos_a) + cy
            x4_r = (x1_c * cos_a - y2_c * sin_a) + cx
            y4_r = (x1_c * sin_a + y2_c * cos_a) + cy
            rot_x = np.stack([x1_r, x2_r, x3_r, x4_r])
            rot_y = np.stack([y1_r, y2_r, y3_r, y4_r])

            # Max rect box
            anno.x_top_left = rot_x.min(axis=0)
            anno.y_top_left = rot_y.min(axis=0)
            anno.width = rot_x.max(axis=0) - anno.x_top_left
            anno.height = rot_y.max(axis=0) - anno.y_top_left

        return anno
