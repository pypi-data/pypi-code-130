#
#   Lightnet optional dependencies
#   Copyright EAVISE
#
import logging

__all__ = [
    'bb',
    'cv2',
    'Image',
    'ImageOps',
    'onnx',
    'onnx_numpy_helper',
    'pd',
    'pgpd',
    'pygeos',
    'tqdm',
]
log = logging.getLogger(__name__)

try:
    import pandas as pd
    import brambox as bb
except ModuleNotFoundError:
    log.warning('Brambox is not installed and thus all data functionality related to it cannot be used')
    pd = None
    bb = None

try:
    import cv2
except ModuleNotFoundError:
    log.warning('OpenCV is not installed and cannot be used')
    cv2 = None

try:
    from PIL import Image, ImageOps
except ModuleNotFoundError:
    log.warning('Pillow is not installed and cannot be used')
    Image, ImageOps = None, None

try:
    import onnx
    from onnx import numpy_helper as onnx_numpy_helper
except ModuleNotFoundError:
    log.warning('ONNX is not installed and thus no pruning functionality will work')
    onnx = None
    onnx_numpy_helper = None

try:
    import pygeos
    import pgpd
except ModuleNotFoundError:
    pygeos = None
    pgpd = None

try:
    from tqdm.auto import tqdm
    tqdm.pandas()
except ModuleNotFoundError:
    tqdm = None
