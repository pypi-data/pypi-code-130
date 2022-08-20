import cv2
from sklearn.metrics import RocCurveDisplay
import numpy as np
from cv2cuda.decorator import timeit
import functools

def make_square(easy_roi_circle):

    x = easy_roi_circle["center"][0] - easy_roi_circle["radius"]
    y = easy_roi_circle["center"][1] - easy_roi_circle["radius"]
    h = w = easy_roi_circle["radius"] * 2
    return [x, y, w, h]

    
class ROISPlugin:
    _ROIbackend = "EasyROI"

    """
    
    Needed signatures

    status, image = self._next_image_square()
    width, height = self.resolution   
    """

    ROI_SEGMENTATION_PREVIEW_WIDTH = 1280
    ROI_SEGMENTATION_PREVIEW_HEIGHT = 960

    def __init__(self,  *args, roi_helper=None, **kwargs):
        self._roi_helper = roi_helper
        super(ROISPlugin, self).__init__(*args, **kwargs)


    @staticmethod
    def _crop_roi(image, roi):
        return image[
            int(roi[1]) : int(roi[1] + roi[3]),
            int(roi[0]) : int(roi[0] + roi[2]),
        ]


    @staticmethod
    def _process_roi(r, fx, fy):
        r[0] = int(r[0] * fx)
        r[1] = int(r[1] * fy)
        r[2] = int(r[2] * fx)
        r[3] = int(r[3] * fy)
        roi = tuple(r)
        return roi

    def _select_rois(self, image):

        if self._roi_helper and self._ROIbackend == "EasyROI":
            print(image.shape)
            while True:
                roi = self._roi_helper.draw_circle(image, quantity=1)["roi"][0]
                roi = make_square(roi)

                mask = np.zeros_like(image)
                mask[
                    roi[1]:(roi[1] + roi[3]),
                    roi[0]:(roi[0] + roi[2]),
                ] = 255
                applied = cv2.bitwise_and(image, mask)
                cv2.imshow("Selected", applied)
                if cv2.waitKey(0) == 32: #spacebar
                    break


            roi = [roi]
        
        elif self._ROIbackend == "cv2":
            roi = cv2.selectROIs("select the area", image)
                
        while any([v < 0 for v in roi[0]]):
            roi = self._select_rois(image)
        
        print(roi)
        return roi


    def select_ROIs(self):
        """
        Select 1 or more ROIs
        """
        status, image = self._next_image_square()

        if (
            image.shape[1] > self.ROI_SEGMENTATION_PREVIEW_WIDTH or 
            image.shape[0] > self.ROI_SEGMENTATION_PREVIEW_HEIGHT
        ):
            fx = self.ROI_SEGMENTATION_PREVIEW_WIDTH / image.shape[1] 
            fy = self.ROI_SEGMENTATION_PREVIEW_HEIGHT / image.shape[0]

            fx = min(fx, fy)
            fy = fx

            image = cv2.resize(
                image, dsize=None, fx=fx, fy=fy, interpolation=cv2.INTER_AREA
            )

        rois = self._select_rois(image)

        rois = [self._process_roi(list(roi), 1/fx, 1/fy) for roi in rois]
        self._rois = rois
        print("Selected ROIs")
        for roi in self._rois:
            print(roi)
        cv2.destroyAllWindows()
        return rois



    def _next_image_rois(self):

        status, image = self._next_image_square()
        if not status:
            return status, (None)

        data = []
        for r in self.rois:
            data.append(self._crop_roi(image, r))
        return status, data


    @property
    def rois(self):
        if self._rois is None:
            try:
                return [(0, 0, *self.resolution)]
            except:
                raise Exception(
                    "Please open the camera before asking for its resolution"
                )
        else:
            return self._rois



class CameraUtils:

    def _count_frames_in_second(self):
        offset = self._time_s % 1000
        if offset < self._last_offset:
            self._last_offset = offset
            self._frames_this_second = 0
        else:
            self._frames_this_second += 1

class SquareCamera:

    VALUE_OF_BACKGROUND=255

    @staticmethod
    @functools.lru_cache
    def _compute_pad(shape):

        if shape[1] > shape[0]:
            left = right = 0
            bottom = top = (shape[1] - shape[0]) / 2
            diff = shape[1] - shape[0] - bottom - top
            if diff > 0:
                bottom += diff
        
        elif shape[0] > shape[1]:
            top, bottom = 0
            left = right = (shape[0] - shape[1]) / 2
            diff = shape[0] - shape[1] - left - right
            if diff > 0:
                right += diff
        
        else:
            top = bottom = left = right = 0

        
        return int(top), int(bottom), int(left), int(right)

    @timeit
    def apply_pad(self, image):
        top, bottom, left, right = self._compute_pad(image.shape)
        image = cv2.copyMakeBorder(image,
            top, bottom, left, right,
            borderType=cv2.BORDER_CONSTANT, value=self.VALUE_OF_BACKGROUND
        )
        return image

    def _next_image_square(self):
        code, image = self._next_image_default()
        if image is not None:
            if image.shape[0] != image.shape[1]:
                image, msec = self.apply_pad(image)
                assert image.shape[0] == image.shape[1]


        return code, image
