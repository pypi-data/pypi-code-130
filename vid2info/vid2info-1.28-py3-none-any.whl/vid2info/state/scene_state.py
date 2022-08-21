"""
This class implements the state of a concrete frame.

Author: Eric Canas.
Github: https://github.com/Eric-Canas
Email: eric@ericcanas.com
Date: 17-07-2022
"""
from collections import deque
from time import time
import numpy as np

from state.config import ELEMENT_BUFFER_SIZE
from utils.general import crop_segmentation_mask
from vid2info.inference.utils import crop_bbox_from_image
from vid2info.inference.config import BBOX_XYXY
from vid2info.state.element_state import ElementState

crop_img_if_given = lambda img, bbox, copy = True: crop_bbox_from_image(image=img, bbox_xyxy=bbox, is_normalized=True, copy=copy) \
                                        if img is not None else None

class SceneState:
    def __init__(self, tracker_out : dict, buffer: deque, get_first_element_time_stamp: callable = lambda track_id : None,
                 element_buffer_size : int = ELEMENT_BUFFER_SIZE,
                 frame: np.ndarray | None = None, segmentation_mask : dict | None = None,
                 save_full_segmentation_mask : bool = False, element_state_class : type = ElementState):
        """
        Initialize the SceneState. It is used for defining the current scene, and will contain the
        state of each individual element in the scene.

        :param tracker_out: dictionary. The output of the tracker. It is the dictionary outputted by
                get_track_ids when return_as_dict is True. It's keys are the track_ids and the values are
                dictionaries with, at least, the following keys: ('bbox_xyxy', 'confidence', 'class_id', 'track_length')
        :param buffer: deque. The buffer containing the N previous SceneStates.
        :param get_first_element_time_stamp: callable. A function that returns the first_timestamp of the first
                detection of the element with the given track_id in the buffer or the current timestamp if the
                element is not in the buffer.
        :param element_buffer_size: int. The size of the buffer for each element. That buffer will only contain the last
                element_buffer_size element ElementStates for each element.
        :param frame: np.ndarray or None. The frame of the scene. If given, it will save a cropped subimage for
                each detected element.
        :param segmentation_mask: dict or None. The segmentation mask of the scene, embedded within a dictionary
                with the following keys: ('segmentation_mask', 'background_class_idx', 'class_names_list'). If given,
                it will save a cropped subimage for each detected element.

        :param save_full_segmentation_mask: bool. If True, it will save the full segmentation mask of the scene.
        """

        self.elements = {track_id :
                         element_state_class(element_tracker_info=element,
                                             first_detection_timestamp=get_first_element_time_stamp(track_id=track_id),
                                             element_buffer=_get_element_buffer(scene_buffer=buffer, track_id=track_id,
                                                                                   buffer_size=element_buffer_size),
                                             element_img=crop_img_if_given(img=frame, bbox=element[BBOX_XYXY], copy=True),
                                             element_segmentation_mask=crop_segmentation_mask(segmentation_mask=segmentation_mask,
                                                                                              bbox=element[BBOX_XYXY],
                                                                                              copy=not save_full_segmentation_mask)
                                                                    if segmentation_mask is not None else None)
                         for track_id, element in tracker_out.items()}
        self.timestamp = time()
        self.segmentation_mask = segmentation_mask if save_full_segmentation_mask else None

    def __len__(self):
        return len(self.elements)

    def get_elements_age_in_seconds(self) -> dict:
        """
        Returns the age of each element in the scene in seconds.

        :return dict. The age of each element in the scene. The keys are the track_ids and
                        the values are the age in seconds.
        """
        return {track_id : self.elements[track_id].age_in_seconds for track_id in self.elements}

    def get_element_counts(self) -> dict:
        """
        Returns the number of elements in the scene for each class.

            Returns:
                dict. The number of elements in the scene for each class. The keys are the class names and
                the values are the number of elements in the scene for that class.
            """
        classes_list = [element.class_name for element in self.elements.values()]
        return {class_name : classes_list.count(class_name) for class_name in set(classes_list)}

def _get_element_buffer(scene_buffer : deque, track_id : int, buffer_size : int = ELEMENT_BUFFER_SIZE) -> deque:
    """
    Returns a buffer with the last buffer_size elements with the given track_id in the scene_buffer. If the track_id
    disappears in the scene_buffer for some in between frames, these frames will be ignored. So the buffer will be
    not representative of the distance between frames.

    :param scene_buffer: deque. The buffer containing the last SceneStates.
    :param track_id: int. The track_id of the element we want to get the buffer for.
    :param buffer_size: int. The maximum size of the expected buffer.

    :return deque. A buffer containing the last buffer_size elements with the given track_id in the scene_buffer.
    """
    element_buffer = deque(maxlen=buffer_size)
    # Read the scene_buffer backwards
    for scene_state in reversed(scene_buffer):
        if track_id in scene_state.elements:
            element_buffer.append(scene_state.elements[track_id])
        if len(element_buffer) == buffer_size:
            break
    element_buffer = deque(reversed(element_buffer))
    return element_buffer