
from PyQt5.QtWidgets import QFileDialog, QMessageBox, QApplication
from simple_slice_viewer.model import CT, FULL, SUV
from simple_slice_viewer import Logger
from simple_slice_viewer.view import SliceViewerWidget, MainView

from simple_slice_viewer.model import SyncedImageSlicers, AXIAL

import os
import SimpleITK as sitk
import sitk_tools

import pyqtgraph as pg

LOG_LEVEL = Logger.LEVEL_INFO

SUPPORTED_FILES = ("Nifti Files (*.nii;*.nii.gz;*.nia;*.img;*.img.gz;*.hdr);;"
                   "Nrrd (*.nrrd;*.nhdr);;"
                   "Meta Image (*.mhd;*.mha);;"
                   "All Files (*)")
                   
class MainController():
    def __init__(self, view=None, model=None, slice_controller=None):
        if view is None:
            view = MainView()
        if model is None:
            model = SyncedImageSlicers()
        if slice_controller is None:
            slice_controller = SliceController(view=view.image_view,
                                               model=model)
        self.view = view
        self.model = model
        self.slice_controller = slice_controller
        self.set_menu_callbacks()
        
    def refresh(self, _):
        if self.model[0].get_image() is not None:
            self.view.set_image_enabled(True)
            self.view.set_fusion_enabled(False)
            
        if self.model[1].get_image() is None:
            self.view.set_fusion_enabled(True)
            
    def set_callbacks(self):
        self.model.subscribe(self, self.model.EVENT_IMAGE_CHANGED, 
                             self.refresh)
        
        
    def set_menu_callbacks(self):        
        callback = lambda _: self.slice_controller.load_image(0)
        self.view.subscribe(self, self.view.EVENT_OPEN_IMAGE, callback)
        
        callback = lambda _: self.slice_controller.load_image(1)
        self.view.subscribe(self, self.view.EVENT_OPEN_FUSION, callback)
        
        callback = lambda _: self.slice_controller.load_dicom(0)
        self.view.subscribe(self, self.view.EVENT_OPEN_IMAGE_DICOM, callback)
        
        callback = lambda _: self.slice_controller.load_dicom(1)
        self.view.subscribe(self, self.view.EVENT_OPEN_FUSION_DICOM, callback)
        
        callback = lambda _: self.view.clear_fusion()
        self.view.subscribe(self, self.view.EVENT_CLEAR_FUSION, callback)
        
    

        
class SliceController(Logger):
    _image_style = None
    _index = None
    _image = None

    _mpl = None
    _view = None
    _view_direction = AXIAL

    def __init__(self, view=None, model=None, view_direction=AXIAL,
                 image_style=None, show_cropper=True):
        
        Logger.__init__(self, log_level=LOG_LEVEL)

        if model is None:
            model = SyncedImageSlicers(view_direction=view_direction)
        
        if view is None:
            view = SliceViewerWidget()

        
        self.view = view
    
        
        self.model = model
        self.set_callbacks()
        self.full_update_image()
        
    def set_model(self, model):
        self.model.unsubscribe(self)
        
        self.model = model
        self.set_model_callbacks()
        self.full_update_image()
        
    def full_update_image(self, event_data=None):
        self.refresh()
        
        image_scale = self.model[0].guess_scale()
        fusion_scale = self.model[1].guess_scale()
        
        if image_scale == SUV:
            self.view.set_preset('PET')
        elif image_scale == CT and fusion_scale == SUV:
            self.view.set_preset('PET-CT SUV')
        elif image_scale == CT and fusion_scale == FULL:
            self.view.set_preset('PET-CT')
        elif image_scale == CT and fusion_scale == CT:
            self.view.set_preset('Overlay')
        elif image_scale == CT and fusion_scale is None:
            self.view.set_preset('PET-CT')
       
        self.view.image_view.plot_item.enableAutoRange()
        
    def refresh(self, event_data=None):
        image_slice = self.model[0].get_sitk_slice()
        fusion_slice = self.model[1].get_sitk_slice()
        
        if image_slice is not None:
            if self.model[0].get_ndim() == 3\
                and len(self.model[0]) > 1:
                    self.view.show_image(scroll=True)
            else:
                self.view.clear_image()
                
        else:
            self.view.set_enabled_image(False)
        
            #self.view.clear_image()
        
        if fusion_slice is not None:
            self.view.show_fusion()
        else:
            self.view.clear_fusion()
        
        self.view.image_view.set_image_and_fusion(image_slice, fusion_slice)
        
        if len(self.model[0]) > 1:
            self.view.slicescroller.scrollbar.setMinimum(0)
            self.view.slicescroller.scrollbar.setMaximum(len(self.model[0])-1)
            self.view.slicescroller.scrollbar.setValue(self.model.get_index())
        
        vdir = self.model.get_view_direction()
        self.view.orientation_buttons.set_selected_button(vdir)

    
    def scroll(self):
        self.logger.debug('Scroll!')
        self.model.set_index(self.view.slicescroller.scrollbar.value())
        
    def update_slice(self, event_data=None):
        self.logger.debug('Update Slcie!')
        image = self.model[0].get_sitk_slice()
        fusion = self.model[1].get_sitk_slice()
        self.view.image_view.set_image_and_fusion(image, fusion)
       
      
    def set_callbacks(self):
        self.logger.debug('Setting callbacks....')
        
        self.view.slicescroller.scrollbar.valueChanged.connect(self.scroll)

        event = self.view.image_view.EVENT_MOUSE_MOVE
        self.view.image_view.subscribe(self, event, self.mouse_move)
        
        # if self.view.io_buttons:
        #     event = self.view.io_buttons.EVENT
        #     self.view.io_buttons.subscribe(self, event, self.button_click)
        
        self.set_model_callbacks()
        
        
    # def button_click(self, button):
    #     if button == self.view.io_buttons.LOAD_IMAGE:
    #         self.load_image(0)
    #     elif button == self.view.io_buttons.LOAD_FUSION:
    #         self.load_image(1)

            
        
    
    
    def set_model_callbacks(self):
        self.model.subscribe(self, self.model.EVENT_INDEX_CHANGED, 
                             self.update_slice)
        
        self.model.subscribe(self, self.model.EVENT_VIEW_DIRECTION_CHANGED,
                                 self.refresh)
        
        
        self.model.subscribe(self, self.model.EVENT_IMAGE_CHANGED, 
                             self.full_update_image)
        
        event = self.view.orientation_buttons.EVENT
        
        self.view.orientation_buttons.subscribe(
            self, event, self.model.set_view_direction)

    def mouse_move(self, position):
     
        position = self.model[0].transform_index_to_physical_point(position)
        position_text = f'Mouse Position: {position} [mm]'
        self.view.status_label.setText(position_text)
        
    def load_dicom(self, index):
        image = self.read_dicom()
        if image:
            self.model.set_image(image, index=index)
 
    def read_dicom(self):
        folder = self.get_open_folder()
        image = None
        if folder:
            try:
                image = sitk_tools.read_folder(folder, recursive=True, 
                                              frame_tag=None)
            except:
                self.show_warning(f'Failed to load Dicom folder {folder}')

        return image
        
    def get_open_file(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self.view, "Select Image File", "", SUPPORTED_FILES)
            
        return file_name
    
    def get_open_folder(self, msg="Select Folder"):
        folder_name = QFileDialog.getExistingDirectory(self.view, msg)
        return folder_name
            
    def load_image(self, index):
        image = self.read_image()
        
        if not image:
            self.logger.debug('No Image Selected!')
            return
        
        clear_fusion = False
        
        
        if index == 0:
            fusion =  self.model.get_image(1)
            if fusion is None or not sitk_tools.same_space(image, fusion):
                clear_fusion = True
        
        if image:
           self.model.set_image(image, index=index)
            
        if clear_fusion:
            self.logger.debug('Clearing Fusion!')
            self.model.set_image(None, index=1)
                
    def read_image(self):
        file_name = self.get_open_file()
        image = None
        if file_name:
            try:
                image = sitk.ReadImage(file_name)
            except:
                self.show_warning(f'Could not open file {file_name}')
        
       
            
            
        return image

                    
    def load_fusion(self):
        self.show_warning('Test!')
    
    def show_warning(self, msg):
        QMessageBox.warning(self.view, 'Simple Slice Browser', 
                             msg, QMessageBox.Ok)
  
        
   
        

def safe_load_image(image):
    if isinstance(image, sitk.Image) or image is None:
        return image
    elif isinstance(image, str) and not os.path.exists(image):
        raise IOError(f'File not found: {image}')
    elif os.path.isfile(image):
        try:
            image = sitk.ReadImage(image)
        except:
            try:
                image = sitk_tools.read_file(image)
            except:
                raise IOError(f'Could not read {image}!')
    elif os.path.isdir(image):
        try:
            image = sitk_tools.read_folder(image)
        except:
            raise IOError(f'Could not read folder as DICOM: {image}')
    return image
        
    
def display(image=None, 
            fusion=None, 
            view_direction=None, 
            preset=None,
            new_qapp=True):
    
    image = safe_load_image(image)
    fusion = safe_load_image(fusion)
    
    if new_qapp:
        app = QApplication([])
    #_app.setStyleSheet(qdarkstyle.load_stylesheet(qt_api='pyqt5'))
    
    
        color = app.palette().color(app.palette().Background)
        pg.setConfigOption('background', color)
        pg.setConfigOption('foreground', 'k')
    
    
    model = SyncedImageSlicers(images=[image, fusion],
                               view_direction=view_direction)
    
    controller = MainController(model=model)
                         
    if preset is None:
        preset = {}
        
    controller.view.image_view.set_preset(preset)
    
    controller.view.show()
    
    if new_qapp:
        app.exec()
    
    return controller
    
 

if __name__ == "__main__":
    app = QApplication([])
    
    color = app.palette().color(app.palette().Background)
    pg.setConfigOption('background', color)
    pg.setConfigOption('foreground', 'k')
     
    window = MainView()
    controller = MainController(view=window) 
    
    #window.subscribe(window, window.SLICE_SCROLL_EVENT, callback)  
    
    
    window.show()    
    app.exec_()
    
    
    
    # import sys
    # image = None
    # fusion = None
    # if len(sys.argv) > 1:
    #     image = sys.argv[1]
    # if len(sys.argv) > 2:
    #     fusion = sys.argv[2]
    # display(image=image, fusion=fusion)
    