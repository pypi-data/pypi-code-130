from .basler import BaslerCamera
from .flir import FlirCamera
from .opencv import OpenCVCamera
CAMERAS={
    "BaslerCamera": BaslerCamera,
    "FlirCamera": FlirCamera,
    "OpenCVCamera": OpenCVCamera
}