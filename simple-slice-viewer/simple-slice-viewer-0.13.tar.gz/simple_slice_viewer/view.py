import SimpleITK as sitk
import sitk_tools
import pyqtgraph as pg
import numpy as np
from functools import partial

from PyQt5.QtWidgets import (QWidget, QGridLayout, QLabel, 
                             QRadioButton,
                             QApplication, QPushButton, QScrollBar,
                             QMainWindow, QMenu, QAction, QVBoxLayout,
                             QHBoxLayout, QStatusBar, QSizePolicy)
                           

from PyQt5.QtGui import QCursor
from PyQt5.QtCore import Qt
from simple_slice_viewer import Observable, logger
from simple_slice_viewer import model
from simple_slice_viewer.styles import COLORMAPS, WINDOW_LEVELS, PRESETS, CUSTOM_COLORMAPS

import qtawesome as qta
from simple_slice_viewer import Logger

LOG_LEVEL = Logger.LEVEL_INFO
# callback = lambda _, cmap=cmap: self.set_cmap(cmap)
# action.triggered.connect(callback)
 
# callback = lambda _, wl=wl: self.set_window_level(wl)
# action.triggered.connect(callback)
   
class ColorMenu(QMenu):
    def __init__(self, parent=None, colorbar=None):
        self.colorbar = colorbar
        super().__init__(parent=parent)
        
        self.cmap_menu = QMenu("Colormap")        
        self.cmap_actions = []
        for cmap in COLORMAPS + list(CUSTOM_COLORMAPS.keys()):
            action = QAction(cmap)
            action.triggered.connect(lambda _, cmap=cmap: self.colorbar.setColorMap(cmap))
            self.cmap_actions += [action]
            self.cmap_menu.addAction(action)   
        
   
        self.wl_actions = []
        self.wl_menu = QMenu("Window Level")
        
        for wl in WINDOW_LEVELS.keys():
            action = QAction(wl)
            action.triggered.connect(lambda _: self.colorbar.setWindowLevel(wl))
            self.wl_menu.addAction(action)
            self.wl_actions += [action]
            

        
        self.addMenu(self.cmap_menu)
        self.addMenu(self.wl_menu)
    
    
    
    

class ColorBarItemMouse(pg.ColorBarItem, Observable):
    EVENT_RIGHT_CLICK = 'event_right_click'
    
    def __init__(self, *args, **kwargs):
        self.parent = kwargs.pop('parent')
        pg.ColorBarItem.__init__(self, *args, **kwargs)
        Observable.__init__(self, log_level=LOG_LEVEL)
        
    def mouseClickEvent(self, event):
        if event.button() == 2:
            # show context menu
            self.fire(self.EVENT_RIGHT_CLICK, self)


    def setColorMap(self, cmap):
        cmap = self.format_cmap(cmap)
        
        if sum(cmap[0].getRgb()) == 4:
            self.parent.plot_item.getViewBox().setBackgroundColor('w')
        else:
           self.parent.plot_item.getViewBox().setBackgroundColor('k')
           
        super().setColorMap(cmap)
        
    def setWindowLevel(self, window_level):
        if window_level is None:
            raise ValueError()
            
        if isinstance(window_level, str):
            window_level = WINDOW_LEVELS[window_level]


        wl = window_level
        low, high = (wl[1] - 0.5 * wl[0], wl[1] + 0.5 * wl[0])
            
        self.setLevels(low=low, high=high)
        
    def format_cmap(self, cmap):
        if cmap is None:
            cmap = 'gray'
        
        if cmap in CUSTOM_COLORMAPS.keys():
            cmap = CUSTOM_COLORMAPS[cmap]
            
        if isinstance(cmap, str):
            cmap = pg.colormap.getFromMatplotlib(cmap)
        
        return cmap
        
            
    
    
        

        
class WidgetBase(QWidget, Observable):

    _layout = None
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        Observable.__init__(self, log_level=LOG_LEVEL)
        self.create_widgets()
        self.create_layout()
        self.set_callbacks()
        self.setLayout(self.layout)
        
    def create_widgets(self):
        pass
    
    def create_layout(self):
        pass
    
    def set_callbacks(self):
        pass

    @property
    def layout(self):
        if self._layout is None:
            self._layout = self._get_layout_object()
        return self._layout
    
    @layout.setter
    def layout(self, layout):
        self._layout = layout
        
    
    def _get_layout_object(self):
        return QGridLayout()
    
    @staticmethod
    def set_combo_to_text(combo, text):
        combo.setCurrentIndex(combo.findText(str(text)))
        
            


class ImageWidget(WidgetBase):
    EVENT_MOUSE_MOVE = 'event_mouse_move'
    EVENT_IMAGE_SPACE_CHANGED = 'event_image_space_changed'
    
    _image = None
    _fusion = None
    _alpha = 0.5
    _cmap_image = 'gray'
    _cmap_fusion = 'hot'
    _clim_image = (0, 1)
    _clim_fusion = (0, 1)
    def __init__(self, parent=None, image=None):
        self._image = image
            
        WidgetBase.__init__(self, parent=parent)
        
        self.refresh()
        
        self.set_cmap_fusion(self._cmap_fusion)

        
        #mainwidget.addPlot(self.plot_item, row=0, col=0)
    def create_widgets(self):

        self.plot_item = pg.PlotItem()
        self.plot_item.setMenuEnabled(False)
        
        vb = self.plot_item.getViewBox()
        vb.setBackgroundColor('k')
        
        
        self.image_item = pg.ImageItem(image=self.get_np_image(), 
                                       parent=self.plot_item)
        
        self.fusion_item = pg.ImageItem(image=self.get_np_fusion(), 
                                        parent=self.plot_item)
        
        self.fusion_item.setZValue(10)
        
        self.colorbar_image = ColorBarItemMouse(parent=self)
        self.colorbar_fusion = ColorBarItemMouse(parent=self)
        
        self.colorbar_image.setImageItem(self.image_item)
        self.colorbar_fusion.setImageItem(self.fusion_item)
        
        
        self.plot_item.hideAxis('bottom')
        self.plot_item.hideAxis('left')
        
       
        self.set_alpha(self._alpha)
        
   
    def create_layout(self):
        
        self.plot_item.addItem(self.image_item)
        self.plot_item.addItem(self.fusion_item)
        
        
        
        self.layout = QHBoxLayout()
        self.glayout = pg.GraphicsLayoutWidget()
        
        self.glayout.addItem(self.plot_item, row=0, col=0)
        self.glayout.addItem(self.colorbar_image, row=0, col=1)
        self.glayout.addItem(self.colorbar_fusion, row=0, col=2)
        
        
    
        self.layout.addWidget(self.glayout)
        
        self.setLayout(self.layout)
        
        #self.layout.addWidget(self.colorbar_image)
        #self.layout.addWidget(self.colorbar_fusion)

    def set_callbacks(self):
        self.mouse_poxy = pg.SignalProxy(self.plot_item.scene().sigMouseMoved, 
                                          rateLimit=60, slot=self.mouse_moved)
        
    def mouse_moved(self, event):
        self.fire(self.EVENT_MOUSE_MOVE, event_data=self.pos_index(event[0]))
    
    def pos_index(self, pos_view):
        pos_index = self.plot_item.getViewBox().mapSceneToView(pos_view)
        return (pos_index.x(), pos_index.y())
    


    def refresh(self):
        self.image_item.setImage(self.get_np_image())
        self.fusion_item.setImage(self.get_np_fusion())
        
        self.set_clim_image(self.get_image_min_max())
        self.set_clim_fusion(self.get_fusion_min_max())
        
        self.plot_item.setAspectLocked(True, ratio=self.get_ratio())
        
    def clear(self):
        self.set_image(self.get_empty_image())
        self.set_fusion(self.get_empty_fusion())
        self.refresh()
        
    def clear_fusion(self):
        image = self.get_image()
        fusion = self.get_empty_fusion()
    
        self.set_image_and_fusion(image, fusion)
        
        self.refresh()
        
    def set_alpha(self, alpha):   
        self.fusion_item.setOpacity(alpha)
    
    def get_ratio(self):
        spacing = self.get_image().GetSpacing()
        aspect = spacing[0] / spacing[1]
        return aspect
    
    def get_image_min_max(self):
        image = self.get_image()
        return [sitk_tools.min(image), sitk_tools.max(image)]
    
    def get_fusion_min_max(self):
        image = self.get_fusion()
        return [sitk_tools.min(image), sitk_tools.max(image)]
    
    def set_clim_image(self, clim):
        if clim is None:
            clim = self.get_image_min_max()
        #self._clim_image = clim
        self.colorbar_image.setLevels(clim) # colormap range
        
    def get_clim_image(self):
        return self.colorbar_image.levels()
        
    def set_clim_fusion(self, clim):
        if clim is None:
            clim = self.get_fusion_min_max()
        
        #self._clim_fusion = clim
        self.colorbar_fusion.setLevels(clim) # colormap range
        
    def get_clim_fusion(self):
        return self.colorbar_fusion.levels()
        
    def set_cmap_fusion(self, cmap):
       self.colorbar_fusion.setColorMap(cmap)
        
    def set_cmap_image(self, cmap):
        self.colorbar_image.setColorMap(cmap)
        
    def set_wl_fusion(self, wl):
        if wl is None:
            self.set_clim_fusion(None)
        else:
            self.colorbar_fusion.setWindowLevel(wl)
            
    def set_wl_image(self, wl):
        if wl is None:
            self.set_clim_image(None)
        else:
            self.colorbar_image.setWindowLevel(wl)
        
        
    def get_empty_image(self):
        return sitk.GetImageFromArray(np.zeros((10, 10)) )
    
    def get_empty_fusion(self):
        return sitk_tools.zeros_like_image(self.get_image())
   
    def get_image(self):
        if self._image is None:
            self._image = self.get_empty_image()
        return self._image
    
    def set_image_and_fusion(self, image=None, fusion=None):
        
        self._set_image(image)
        self._set_fusion(fusion)
        
        clim_image = self.get_clim_image()
        clim_fusion = self.get_clim_fusion()
        

        self.set_clim_image(clim_image)
        self.set_clim_fusion(clim_fusion)
        
        self.plot_item.setAspectLocked(True, ratio=self.get_ratio())
    
        
    def _set_image(self, image):
        self._image = image
        self.image_item.setImage(self.get_np_image())
        
        
        

    def get_fusion(self):
        if self._fusion is None:
            self._fusion = sitk_tools.random_like_image(self.get_image()) * 200
        
        image = self.get_image()
        
        if image is not None:
            if not sitk_tools.same_space(image, self._fusion):
                #print('Resample in view!')
                self._fusion = sitk_tools.resample_to_image(self._fusion, image)
            
        return self._fusion
        
    def _set_fusion(self, fusion):
      
        self._fusion = fusion
        self.fusion_item.setImage(self.get_np_fusion())
        
        
    def get_np_image(self):
        return sitk.GetArrayFromImage(self.get_image()).T
    
    def get_np_fusion(self):
        return sitk.GetArrayFromImage(self.get_fusion()).T
    


        
class ButtonView(WidgetBase):
    EVENT = 'button_click'
    button_texts = ['Button1', 'Button2']
    label_text = 'Button Group Name'
    orientation = Qt.Horizontal

    def __init__(self, parent=None, button_texts=None, label_text=None):

        
        if button_texts is not None:
            self.button_texts = button_texts
            
        if label_text is not None:
            self.label_text = label_text
            
        WidgetBase.__init__(self, parent=parent)

    def create_widgets(self):
        if self.label_text:
            self.label = QLabel(self.label_text, self)
        else:
            self.label = None
            
        self._buttons = []
        for text in self.button_texts:
            button = self.create_button(text)
            self._buttons += [button]
            
    def create_button(self, text):
        button = QPushButton(text, self)
        button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        return button
    
    def create_vertical_layout(self):
        row = 0
        if self.label is not None:
            self.layout.addWidget(self.label, row, 0)
            row += 1
        
        for button in self._buttons:
            self.layout.addWidget(button, row, 0)
            row += 1
            
    def create_horizontal_layout(self):
        column = 0
        if self.label is not None:
            self.layout.addWidget(self.label, 0, column)#, alignment=Qt.AlignCenter)
            column += 1
        
        for button in self._buttons:
            self.layout.addWidget(button, 0, column)#, alignment=Qt.AlignCenter)
            column += 1
            
    def create_layout(self):
        if self.orientation == Qt.Horizontal:
            self.create_horizontal_layout()
        elif self.orientation == Qt.Vertical:
            self.create_vertical_layout()
        else:
            raise ValueError(f'Unknown orientation {self.orientation}')
        
    
    def set_callbacks(self):
        for i, button in enumerate(self._buttons):
            text = self.button_texts[i]
            cmd = partial(self.fire, self.EVENT, text)
            button.clicked.connect(cmd)
            
    def disable(self, text=None):
        self._set_state(text=text, enabled=False)

    def enable(self, text=None):
        self._set_state(text=text, enabled=True)

    def _set_state(self, text=None, enabled=True):
        if text is None:
            for text in self.button_texts:
                self._set_state(text=text, enabled=enabled)
            return
        index = self.button_texts.index(text)
        self._buttons[index].setEnabled(enabled)

   
class RadioButtonView(ButtonView):
    EVENT = 'selection_change'
    label_text = 'Radiobutton Group Name'
    button_texts = ['RadioButton1', 'RadioButton2']
    
    def __init__(self, parent=None, button_texts=None, label_text=None,
                 selected_button=None):
        ButtonView.__init__(self, parent=parent, button_texts=button_texts, 
                            label_text=label_text)
        
        self.set_selected_button(selected_button)
        
    
    def get_selected_button(self):
        for text, button in zip(self.button_texts, self._buttons):
            if button.isChecked():
                return text

    def set_selected_button(self, button_name):
        if button_name is None:
            button_name = self.button_texts[0]
            
        self._selected_button = button_name
        
        for text, button in zip(self.button_texts, self._buttons):
            if text == button_name:
                button.setChecked(True)
            else:
                button.setChecked(False)
    
    def fire(self, event_name, event_data=None):
        if event_name == self.EVENT:
            button_index = self.button_texts.index(event_data)
            button = self._buttons[button_index]
            if button.isChecked():
                super().fire(event_name, event_data=event_data)
        else:
            super().fire(event_name, event_data=event_data)
            
    
    def create_button(self, text):
        button = QRadioButton(text, self)
        button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        return button
        
    
    def set_callbacks(self):
        for text, button in zip(self.button_texts, self._buttons):
            
            cmd = partial(self.fire, self.EVENT, text)
            button.toggled.connect(cmd)
            


class ViewDirectionRadioButtons(RadioButtonView):
    button_texts = model.ORIENTATIONS 
    orientation = Qt.Horizontal
    label_text = None

    

class IOFusionButtons(ButtonView):
    LOAD_FUSION     = 'Load Fusion'
    LOAD_IMAGE      = 'Load_image'
    CLEAR_FUSION    = 'Clear Fusion'
    
    
    button_texts = (LOAD_IMAGE, LOAD_FUSION, CLEAR_FUSION)
    label_text = None
    
class OperatorButtons(ButtonView):
    SUBTRACT     = 'Subtract'
    ADD          = 'Add'
    SAVE         = 'Save'
    
    button_texts = (ADD, SUBTRACT, SAVE)
    label_text = 'Image <operator> Fusion'
    
    
    
class VerticalSLider(WidgetBase):
    def __init__(self, parent=None, label='Alpha', unit='%', value=50):
        self.label = label
        self.unit = unit
        self._value = value
        super().__init__(parent=parent)
        

    @property
    def value(self):
        return str(self._value)
    
    @value.setter
    def value(self, value):
        value = str(value)
        self._value = value
        self.top_label.setText(value + self.unit)

        
    def create_widgets(self):
        self.label = QLabel(self.label)
        self.top_label = QLabel(self.value)
        self.scrollbar = QScrollBar(orientation = Qt.Vertical)
        
        
    def create_layout(self):
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.label, 0, alignment=Qt.AlignHCenter)
        self.layout.addWidget(self.top_label, 0, alignment=Qt.AlignCenter)
        self.layout.addWidget(self.scrollbar, 1,  alignment=Qt.AlignHCenter)
        
    def set_callbacks(self):
        self.scrollbar.valueChanged.connect(self.scroll_event)
        
    def scroll_event(self, event_data=None):
        self.value = self.scrollbar.value()
        
        
    
    
        
class SliceViewerWidget(WidgetBase):
    _menu = None
    def __init__(self, *args, **kwargs):        
        WidgetBase.__init__(self, *args, **kwargs)
        self.image_menu = self._get_image_color_menu()
        self.fusion_menu = self._get_fusion_color_menu()
        
    def _get_image_color_menu(self):        
        menu = ColorMenu(colorbar=self.image_view.colorbar_image, parent=self)
        return menu
    

    def _get_fusion_color_menu(self):
        menu = ColorMenu(colorbar=self.image_view.colorbar_fusion, parent=self)
        return menu
    
    
    def create_widgets(self):
        
        self.image_view = ImageWidget()
        
        self.slicescroller = VerticalSLider(parent=self, label='Slice', unit='')
        
        self.orientation_buttons = ViewDirectionRadioButtons(parent=self)
        
        self.alpha_slider = VerticalSLider(parent=self, label='Alpha',
                                           unit='%')
       
        self.set_alpha(self.image_view._alpha)
        
        self.status_label = QLabel('Start')
        
        # if self.show_buttons:
        #     self.io_buttons = IOFusionButtons()
        # else:
        #     self.io_buttons = None
            
    def create_layout(self):
       
       row = 0   
       
       self.layout.addWidget(self.orientation_buttons, row, 0, 1, 3)
       
       row += 1
      
       self.layout.addWidget(self.slicescroller, row, 0)
       self.layout.addWidget(self.image_view, row, 1)
       self.layout.addWidget(self.alpha_slider, row, 2) 
       
       row += 1
       
       
       
       # if self.show_buttons:
       #     row += 1
           
       #     self.layout.addWidget(self.io_buttons, row, 0, 1, 3)
           
       
       # row += 1
       
       self.layout.addWidget(self.status_label, row, 0, 1, 3)
       
  
    def set_callbacks(self):
        event =  self.image_view.colorbar_fusion.EVENT_RIGHT_CLICK        
        callback = lambda _: self.show_fusion_colorbar_context_menu()
        self.image_view.colorbar_fusion.subscribe(self, event, callback)
        
     
        callback = lambda _: self.show_image_colorbar_context_menu()
        self.image_view.colorbar_image.subscribe(self, event, callback)
        
        self.alpha_slider.scrollbar.valueChanged.connect(self.alpha_changed)
        
    
    def show_image_colorbar_context_menu(self):
        self.image_menu.exec_(QCursor().pos())
    
    def show_fusion_colorbar_context_menu(self):
        self.fusion_menu.exec_(QCursor().pos())
        
    def set_enabled_image(self, enabled):
        self.orientation_buttons.setVisible(enabled)
        self.slicescroller.setVisible(enabled)
        self.fusion_menu.cmap_menu.setEnabled(enabled)
        self.fusion_menu.wl_menu.setEnabled(enabled)

       
    def set_enabled_fusion(self, enabled):
        self.image_view.colorbar_fusion.setVisible(enabled)
        self.image_view.fusion_item.setVisible(enabled)
        self.alpha_slider.setVisible(enabled)
        self.fusion_menu.cmap_menu.setEnabled(enabled)
        self.fusion_menu.wl_menu.setEnabled(enabled)

    
        
    def alpha_changed(self):
        self.image_view.set_alpha(self.alpha_slider.scrollbar.value() / 100)
        
    def set_alpha(self, alpha):
        self.alpha_slider.scrollbar.setValue(int(round(alpha*100)))
        
        
    def show_image(self, scroll=True):
        self.set_enabled_image(True)
        
        if scroll:
            self.slicescroller.setVisible(True)
            self.orientation_buttons.setVisible(True)
        else:
            self.scrollbar.setVisible(False)
            self.orientation_buttons.setVisible(False)
    
    def clear_image(self):
        self.image_view.clear()
        self.set_enabled_image(False)
        self.set_enabled_fusion(False)
        self.scrollbar.setVisible(False)
        self.orientation_buttons.setVisible(False)
    
     
    def show_fusion(self):
        self.set_enabled_fusion(True)
        
    def hide_fusion(self):
        self.set_enabled_fusion(False)
   
    def clear_fusion(self):
        self.image_view.clear_fusion()
        self.set_enabled_fusion(False)
    
       

    def set_preset(self, preset):
        if isinstance(preset, str):
            return self.set_preset(PRESETS[preset])
            
            
        image_preset = preset.get('image', {})
        fusion_preset = preset.get('fusion', {})
        imview = self.image_view
        
        if 'cmap' in image_preset.keys():
            imview.set_cmap_image(image_preset['cmap'])
        if 'window_level' in image_preset.keys():
            imview.set_wl_image(image_preset['window_level'])
        
        if 'cmap' in fusion_preset.keys():
            imview.set_cmap_fusion(fusion_preset['cmap'])
        if 'window_level' in fusion_preset.keys():
            imview.set_wl_fusion(fusion_preset['window_level'])
        if 'alpha' in fusion_preset.keys():
            self.set_alpha(fusion_preset['alpha'])

class MainView(QMainWindow, Observable):    
    OPEN_FILE = 'Open file'
    OPEN_DICOM = 'Open Dicom Folder'
    
    EVENT_OPEN_IMAGE = 'open_image'
    EVENT_OPEN_IMAGE_DICOM = 'open_image_dicom'
    
    EVENT_OPEN_FUSION = 'open_fusion'
    EVENT_OPEN_FUSION_DICOM = 'open_fusion_dicom'
    
    CLEAR_FUSION = 'Clear Fusion'
    EVENT_CLEAR_FUSION = 'event_clear_fusion'
    
    def __init__(self):
        QMainWindow.__init__(self)
        Observable.__init__(self, log_level=LOG_LEVEL)
        
        self.create_widgets()
        #self.set_callbacks()
        self.set_menus()
        self.setWindowTitle('Simple Slice Viewer')
        
        icon = qta.icon('fa5s.pizza-slice', color='#ff4000')
        self.setWindowIcon(icon)
    

    def set_enabled_image(self, enabled):
        self.image_view.set_enabled_image(enabled)
        self.fusion_menu_actions[self.OPEN_FILE].setEnabled(enabled)
        self.fusion_menu_actions[self.OPEN_DICOM].setEnabled(enabled)
        
    def set_enabled_fusion(self, enabled):
        self.image_view.set_enabled_fusion(enabled)
        self.fusion_menu_actions[self.CLEAR_FUSION].setEnabled(enabled)
    
    def clear_fusion(self):
        self.image_view.clear_fusion()
        self.set_enabled_fusion(False)

        
    def create_widgets(self):
        self.image_view = SliceViewerWidget(parent=self)
        self.setCentralWidget(self.image_view)
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        
        #self.statusBar.addWidget(self.status_label)
  
  
    def set_menus(self):
        self.menubar = self.menuBar()
        
        self.image_menu = self.menubar.addMenu('Image')
        self.fusion_menu = self.menubar.addMenu('Fusion')
        
        self.fusion_menu_actions = {}
        self.image_menu_actions = {}
        
        action = self.image_menu.addAction(self.OPEN_FILE)
        callback = lambda: self.fire(self.EVENT_OPEN_IMAGE)
        action.triggered.connect(callback)            
        self.image_menu_actions[self.EVENT_OPEN_IMAGE] = action
        
        action = self.image_menu.addAction(self.OPEN_DICOM)
        callback = lambda: self.fire(self.EVENT_OPEN_IMAGE_DICOM)
        action.triggered.connect(callback)            
        self.image_menu_actions[self.EVENT_OPEN_IMAGE_DICOM] = action
        
        action = self.fusion_menu.addAction(self.OPEN_FILE)
        callback = lambda: self.fire(self.EVENT_OPEN_FUSION)
        action.triggered.connect(callback)            
        self.fusion_menu_actions[self.EVENT_OPEN_FUSION] = action
        
        action = self.fusion_menu.addAction(self.OPEN_DICOM)
        callback = lambda: self.fire(self.EVENT_OPEN_FUSION_DICOM)
        action.triggered.connect(callback)            
        self.fusion_menu_actions[self.EVENT_OPEN_FUSION_DICOM] = action
           
        action = self.fusion_menu.addAction(self.CLEAR_FUSION)
        callback = lambda: self.fire(self.EVENT_CLEAR_FUSION)
        action.triggered.connect(callback)
        self.fusion_menu_actions[self.CLEAR_FUSION] = action
          
            
        self.image_menu.addMenu(self.image_view.image_menu.cmap_menu)
        self.image_menu.addMenu(self.image_view.image_menu.wl_menu)
        
        self.fusion_menu.addMenu(self.image_view.fusion_menu.cmap_menu)
        self.fusion_menu.addMenu(self.image_view.fusion_menu.wl_menu)
        
        self.preset_menu = self.menubar.addMenu('Presets')
        
        self.preset_actions = {}
        for name in PRESETS.keys():
            self.preset_actions[name] = QAction(name)
            self.preset_menu.addAction(self.preset_actions[name])
            callback = lambda _, name=name: self.image_view.set_preset(name)
            
            self.preset_actions[name].triggered.connect(callback)
            
              
        # cbar = self.widgets.image_view.colorbar_image
        
        # self.cmap_image_menu = cbar.cmap_menu
        # self.image_menu.addMenu(self.cmap_image_menu)
        
        # self.wl_image_menu = cbar.wl_menu
        # self.image_menu.addMenu(self.wl_image_menu)
        
        
        
        # self.fusion_menu = self.menubar.addMenu('Fusion')
        # self.fusion_menu_actions = {}
        
        # for name in (self.OPEN_FILE, self.OPEN_DICOM):
        #     action = self.fusion_menu.addAction(name)
        #     self.fusion_menu_actions[name] = action

        # cbar = self.widgets.image_view.colorbar_fusion
        
        # self.cmap_fusion_menu = cbar.get_cmap_menu()
        # self.fusion_menu.addMenu(self.cmap_fusion_menu)
        
        # self.wl_fusion_menu = cbar.get_wl_menu()
        # self.fusion_menu.addMenu(self.wl_fusion_menu)
        
        
             
if __name__ == "__main__":
    #import qdarkstyle

    app = QApplication([])
    
    color = app.palette().color(app.palette().Background)
    pg.setConfigOption('background', color)
    pg.setConfigOption('foreground', 'k')
    #app.setStyleSheet(qdarkstyle.load_stylesheet(qt_api='pyqt5'))
    # widget = pg.GraphicsLayoutWidget()
    # widget.addItem(ImageItem())
    # window = widget
    window = MainView()
    #window = SliceViewerWidget()
    #window.set_enabled_image(False)
    #window.set_enabled_fusion(False)
    #window.set_enabled_fusion(True)
    #window.show_image()
    
    
    #window.subscribe(window, window.SLICE_SCROLL_EVENT, callback)
   
    
    
    window.show()    
    app.exec_()
    
    
 