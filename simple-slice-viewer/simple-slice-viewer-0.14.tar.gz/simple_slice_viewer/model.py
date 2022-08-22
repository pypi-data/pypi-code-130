from simple_slice_viewer import Observable
from simple_slice_viewer.logger import Logger
from matplotlib.colors import LinearSegmentedColormap
import numpy as np
import SimpleITK as sitk
import yaml
import os
from collections.abc import Sequence
import sitk_tools


SUV = 'SUV'
CT = 'CT'
FULL = 'Full'
MASK = 'Mask'

AXIAL = 'Axial'
CORONAL = 'Coronal'
SAGGITAL = 'Saggital'

ORIENTATIONS = (SAGGITAL, CORONAL, AXIAL)

LOG_LEVEL = Logger.LEVEL_INFO


def load_image(image):
    if isinstance(image, str) and os.path.exists(image):
        image = sitk.ReadImage(image)
    elif isinstance(image, np.ndarray):
        image = sitk.GetImageFromArray(image)
    elif isinstance(image, sitk.Image) or image is None:
        pass
    else:
        raise TypeError(f'Cannot load image of type {type(image)}')
    return image

class ImageSlicer(Observable):
    _index = None
    _image = None
    _array = None
    _view_direction = None
    _guessed = None
    
  
    
    def __init__(self, image=None, view_direction=AXIAL, index=None):
        
        
        Observable.__init__(self, log_level=LOG_LEVEL)
        
        self.set_image(image)
        self.set_view_direction(view_direction)
        self.set_index(index)
        
    def transform_index_to_physical_point(self, index):
        image = self.get_image()
        if self.get_ndim() == 2:
            phys = image.TransformContinuousIndexToPhysicalPoint(index)
        elif self.get_ndim() == 3:
            phys = (0, 0, 0)
            if len(index) == 3:
                phys = image.TransformContinuousIndexToPhysicalPoint(index)
            elif len(index) == 2:
                direction = self.get_view_direction()
                if direction == SAGGITAL:
                    index = [self.get_index(), *index]
                elif direction == CORONAL:
                    index = [index[0], self.get_index(), index[1]]
                elif direction == AXIAL:
                    index = [*index, self.get_index()]
                else:
                    raise RuntimeError()
            else:
                raise IndexError(f'Wrong number of values passed {len(index)}')
           
            phys = image.TransformContinuousIndexToPhysicalPoint(index)
            
            return np.round(np.asarray(phys), decimals=1).tolist()
            

                
        
    def __len__(self):
        return self.get_slice_count()
    
    def guess_scale(self):
        if self._guessed is None:
            image = self.get_image()
            if image is not None:
                median = sitk_tools.median(image)
                if median < -500:   
                    scale = CT
                elif median > 0 and median < 10:
                    scale = SUV
                else:
                    scale = FULL
            else:
                scale = None
                
            #print(f'Guessing image type {scale}')
            self._guessed = scale
            
        return self._guessed
          
    def get_ndim(self):
        if self.get_image() is None:
            ndim = 0
        else:
            ndim = self.get_image().GetDimension()
        return ndim
        
    
    def get_index(self):
        
        if self._index is None  and len(self) > 0:
            self._index = -1 
            
        if self._index is None:
            pass
          
        elif self._index < 0 or self._index > (len(self)-1):
            self._index = int(round(len(self)/2))
        
        return self._index
    
        
    def set_index(self, index):
        self.logger.debug(f'New Index {index}')
        if index is None:
            self._index = index
            return
        
        index = int(round(float(index)))
        if index == self._index:
            return
        self.logger.debug('start slice scroll to index: %s', str(index))
        self._index = index
        
    def get_np_slice(self):
        direction = self.get_view_direction()
        
        array = self.get_array()
        index = self.get_index()
        
        if array is None: return None
        
        if direction is None:
            direction = self.get_view_direction()
            
        if direction == AXIAL:
            np_slice = np.flipud(array[index, :, :])
        elif direction == CORONAL:
            np_slice = array[:, index, :]
        elif direction == SAGGITAL:
            np_slice = array[:, :, index]
            
        return np_slice
        
        
    
    def get_sitk_slice(self):
        direction = self.get_view_direction()
        image = self.get_image()
        index = self.get_index()
        
        if image is None: return None
        
        if index is None: return None
        try:
            if direction == SAGGITAL:
                image = image[index, :, : ]
            elif direction == CORONAL:
                image = image[:, index, : ]
            elif direction == AXIAL:
                image = image[:, :, index]
                image = sitk.Flip(image, [False, True])

        except IndexError:
            msg = 'Index {0} out of bound for image size {1} and direction {2}'
            raise IndexError(msg.format(str(index), str(image.GetSize()),
                                                        str(direction)))

        if image.GetDimension() == 3:
            raise IndexError('Slice getter failed for image of size %s, direction %s and index %s', str(image.GetSize()), direction, str(index))
        return image
    
        
    
    def get_image(self):
        return self._image
    
   
    def set_image(self, image):
        if image is self._image:
            return
        
        self._image = load_image(image)
        self._array = None
        self.index = None
        self._guessed = None
 
    def get_view_direction(self):
        if self._view_direction is None:
            self._view_direction = AXIAL
        return self._view_direction
    
    
    def set_view_direction(self, view_direction):
        self._view_direction = view_direction
        self.set_index(None)
        

    def get_slice_count(self):
        if self.get_image() is None:
            return 0
        
        imsize = self.get_image().GetSize()
        view_direction = self.get_view_direction()
        if view_direction == AXIAL:
            return imsize[2]
        elif view_direction == CORONAL:
            return imsize[1]
        elif view_direction == SAGGITAL:
            return imsize[0]
        else:
            raise ValueError
            
    
    
    def get_array(self):
        if self._array is None:
            if self.get_image() is not None:
                self._array = sitk.GetArrayFromImage(self.get_image())
        return self._array

class SyncedImageSlicers(Sequence, Observable):
    EVENT_VIEW_DIRECTION_CHANGED    = 'event_view_direction_changed'
    EVENT_IMAGE_CHANGED             = 'event_image_changed'
    EVENT_INDEX_CHANGED             = 'event_slice_changed'
    
    def __init__(self, images=None, view_direction=AXIAL, index=None):
        Sequence.__init__(self)
        Observable.__init__(self, log_level=LOG_LEVEL)
        
        if isinstance(images, sitk.Image):
            images = [images]
        
        if images is None:
            images = [None] * 2
        
        self._image_slicers = [ImageSlicer() for i in range(len(images))]
        
        self.set_images(images)
        self.set_view_direction(view_direction)
        self.set_index(index)
    
    
    def __getitem__(self, index):
        return self._image_slicers[index]
    
    
    def set_view_direction(self, view_direction):
        if view_direction == self[0].get_view_direction():
            return
        
        for i in range(0, len(self)):
            self[i].set_view_direction(view_direction)
        event_data = (0, self.get_image(0))
        self.fire(self.EVENT_VIEW_DIRECTION_CHANGED, event_data)
        #print(view_direction)
        
    def get_view_direction(self):
        return self[0].get_view_direction()
    
  
    def set_index(self, index):
        if index == self[0].get_index():
            return
            
        for slicer in self:
            slicer.set_index(index)
            
        self.fire(self.EVENT_INDEX_CHANGED, index)
            
        
    def get_index(self):
        return self[0].get_index()
    
    def fire_image_change(self, index):
        event_data = (index, self[index].get_image())
        self.fire(self.EVENT_IMAGE_CHANGED, event_data=event_data)
    
    def get_image(self, index=None):
        return self[index].get_image()
    
    def set_images(self, images):
        if len(images) != len(self):
            raise ValueError('Expected {len(self)} images got {len(images)}')
        
        if None not in images:
            images = self.resample_to_first(images)
        
        for item, image in zip(self, images):  
            item.set_image(image)
             
        
        for index in range(0, len(self)):
            self.fire_image_change(index)
            
            
       
    def get_images(self):
        return [self[i].get_image() for i in range(len(self))]
    
    
    def set_image(self, image, index=None):
        images = self.get_images()
        images[index] = image
        self.set_images(images)
            
    def resample_to_first(self, images):
        if images[0] is None:
            return
        
        for i in range(1, len(images)):
            if images[i] is None:
                continue
            
            if not sitk_tools.same_space(images[0], images[i]):
                images[i] = sitk_tools.resample_to_image(images[i], images[0])
        return images
            
            
    
    
                    
    def __len__(self):
        return len(self._image_slicers)
    
    