#
#   Lightnet dataset that works with brambox annotations
#   Copyright EAVISE
#
import os
import logging
from PIL import Image
import numpy as np
import lightnet.data as lnd
from lightnet._imports import bb

__all__ = ['BramboxDataset']
log = logging.getLogger(__name__)


class BramboxDataset(lnd.Dataset):
    """ Dataset for any brambox annotations.

    Args:
        annotations (dataframe): Dataframe containing brambox annotations
        input_dimension (tuple, optional): (width,height) tuple with default dimensions of the network; Default **None**
        class_label_map (list): List of class_labels
        identify (function, optional): Lambda/function to get image based of annotation filename or image id; Default **replace/add .png extension to filename/id**
        transform (torchvision.transforms.Compose): Transformation pipeline

    Note:
        This dataset opens images with the Pillow library
    """
    def __init__(self, annotations, input_dimension=None, class_label_map=None, identify=None, transform=None):
        if bb is None:
            raise ImportError('Brambox needs to be installed to use this dataset')
        super().__init__(input_dimension)

        self.annos = annotations
        self.keys = self.annos.image.cat.categories
        self.transform = transform
        self.id = identify or (lambda name: os.path.splitext(name)[0] + '.png')

        # Add class_ids
        if class_label_map is None:
            log.warning(
                'No class_label_map given, generating it by sorting unique class labels from data alphabetically. '
                'This is not always deterministic!',
            )
            class_label_map = list(np.sort(self.annos.class_label.unique()))
        self.annos['class_id'] = self.annos.class_label.map({l: i for i, l in enumerate(class_label_map)})

    def __len__(self):
        return len(self.keys)

    @lnd.Dataset.resize_getitem
    def __getitem__(self, index):
        """ Get transformed image and annotations based of the index of ``self.keys``

        Args:
            index (int): index of the ``self.keys`` list containing all the image identifiers of the dataset.

        Returns:
            tuple: (transformed image, list of transformed brambox boxes)
        """
        if index >= len(self):
            raise IndexError(f'list index out of range [{index}/{len(self)-1}]')

        # Load
        img = Image.open(self.id(self.keys[index]))
        anno = bb.util.select_images(self.annos, [self.keys[index]])

        # Transform
        if self.transform is not None:
            img, anno = self.transform(img, anno)

        return img, anno
