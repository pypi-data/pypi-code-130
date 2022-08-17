import cv2
import videocv


def run():
    viewer = videocv.Viewer('./')
    while viewer():
        image = viewer.get_frame()
        cv2.imshow('image', image)
        pass


run()
