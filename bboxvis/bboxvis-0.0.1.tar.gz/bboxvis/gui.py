import numpy as np
import vispy
import vispy.io
vispy.use("PyQt5")
import vispy.scene as scene
from vispy import app
import threading
from queue import Queue
import os.path as osp
import zmq
import sys
sys.path.append('..')
sys.path.append('.')
from bboxvis.tools import get_corners
import threading
from loguru import logger
from queue import Queue


import matplotlib.pyplot as plt

COLORS = plt.get_cmap('Paired').colors

def get_color(i):
    return COLORS[i % len(COLORS)] + (1,)


def threaded(fn):
    def wrapper(*args, **kwargs):
        thread = threading.Thread(target=fn, args=args, kwargs=kwargs)
        thread.daemon=True
        # logger.debug(f'{fn} start a thread')
        thread.start()
    return wrapper

class VisMessenger:
    def __init__(self, port='19999'):
        self.socket = zmq.Context().socket(zmq.PUB)
        self.socket.bind(f"tcp://*:{port}")

    def array_to_msg(self, array):
        _shape = np.array(array.shape, dtype=np.int32)
        return [array.dtype.name.encode(),
                _shape.tostring(),
                array.tostring()]
    
    def send_numpy(self, array, nptype='pc', name=''):
        '''
        type: "pc" or "bbox"
        '''
        assert isinstance(array, np.ndarray)
        # _msg = self.array_to_msg(array)
        head_msg = str(nptype) + '/' + str(name)
        self.socket.send_string(head_msg, zmq.SNDMORE)
        self.socket.send_pyobj(array)





class VisCanvas(scene.SceneCanvas):

    PTS_OPT = dict(alpha=0.8, spherical=True)



    def __init__(self, pc_size=5.0, pc_font_size=10.0, label_font_size=5, server=False):
        super().__init__(keys=None, size=(1000, 800), title='PointCloud Canvas', show=True)
        self.unfreeze()

        self.view = self.central_widget.add_view()
        self.axis = scene.visuals.XYZAxis(parent=self.view.scene)

        self.view.camera = 'turntable'
        self.view.camera.center = [0, 0, 0]
        self.view.camera.distance = 10
        self.view.camera.elevation = 30
        self.view.camera.azimuth = -90
        # Press Shift to translate camera view
        self.view.camera.translate_speed = 25
        # GUI
        self.pc_points_size = pc_size
        self.pc_font_size = pc_font_size
        self.label_text_size = label_font_size * 100
        # Visual Elements
        self._pc = dict()
        self._bbox = dict()
        self._bbox_color = list()
        self.numpy_queue = Queue()
        if server == True:
            self._init_server_mode()


    def _init_server_mode(self):
        self.data_thread = threading.Thread(target=self.recv_data, daemon=True)
        self.data_thread.start()
        pass

    def recv_data(self):
        print('thread start')
        socket = zmq.Context().socket(zmq.SUB)  
        socket.setsockopt_string(zmq.SUBSCRIBE, '')  
        port = '19999'
        socket.connect("tcp://localhost:%s" % port)
        while True:
            topic = socket.recv_string()
            msg = socket.recv_pyobj()
            print(topic)
            self.numpy_queue.put([topic, msg])
            event = app.KeyEvent(type='key_press', text='*')
            self.events.key_press(event)

    def _init_bbox(self):
        self.bbox_all_points = np.empty((0,3))
        self.bbox_all_connect = np.empty((0,2))
        self.bbox_all_colors = np.empty((0,4))
        self.connect_template = np.array([
            [0, 1], [1, 2], [2, 3], [3, 0],  # front
            [4, 5], [5, 6], [6, 7], [7, 4],  # back
            [0, 4], [1, 5], [2, 6], [3, 7],  # side
            [0, 2], [1, 3], # front cross
        ])
        self.all_labels_text = []
        self.all_labels_pos = []
    
    @threaded
    def add_pc(self, pc, color=None, name='pointcloud', size=None):
        '''
        Add Point Cloud to canvas
        Args:
        ------
            pc : numpy.ndarray
            color: numpy.ndarray
        '''
        if color is None:
            color = 'w'
        if size is None:
            size = self.pc_points_size
        if name == '':
            name = 'pointcloud'
        if hasattr(self, name):
            self.__dict__[name].set_data(pos=pc, face_color=color, edge_color=None, size=self.pc_points_size)
        else:
            setattr(self, name , scene.visuals.Markers(pos=pc, face_color=color, edge_color=None, size=self.pc_points_size, parent=self.view.scene, **self.PTS_OPT ))

        # Add visual element to dict for further modification
        self._pc[name] = self.__dict__[name]
        return self.__dict__[name]

    @threaded
    def add_bbox(self, bbox, color=(1,1,1,1), name='bbox', width=None):
        '''
        Add Bbox to canvas
        -------
        bbox: (n, 9) numpy ndarray
        color: (n, 4) numpy ndarray
        name: bbox name in canvas
        width: bounding box line width
        '''
        self._init_bbox()
        self._bbox_color.append(color)
        if width is None:
            width = 4
        if name == '':
            name = 'bbox'
        assert len(color) == 4 
        pts, center = get_corners(bbox, ret_center=True)
        self._bbox[name] = [pts, center]

        curr_idx = 0
        for bbox_name in self._bbox:
            self.bbox_all_points = np.append(self.bbox_all_points, self._bbox[bbox_name][0], axis=0)
            self.bbox_all_connect = np.append(self.bbox_all_connect, self.connect_template + curr_idx * 8, axis=0)
            color = np.asanyarray(self._bbox_color[curr_idx]).reshape(1, 4)
            curr_color = np.repeat(color, 8, axis=0)
            self.bbox_all_colors = np.append(self.bbox_all_colors, curr_color, axis=0)
            self.all_labels_text.append(bbox_name)
            self.all_labels_pos.append(self._bbox[bbox_name][1].tolist())
            curr_idx += 1


        if hasattr(self, 'bbox'):
            self.bbox.set_data(pos=self.bbox_all_points, color=self.bbox_all_colors, connect=self.bbox_all_connect, width=width)
        else:
            self.bbox = scene.visuals.Line(pos=self.bbox_all_points, connect=self.bbox_all_connect,
                                           color=self.bbox_all_colors, width=width, parent=self.view.scene)




    def run(self):
        vispy.app.run()

    def render_img(self, dir='/home/nio/workspace/sot_new/bboxvis/example.png',
                   cam_center=(0,0,0), cam_distance=10):
        self.view.camera.center = cam_center
        self.view.camera.distance = cam_distance
        img = self.render()
        vispy.io.write_png(dir, img)
    
    def on_key_press(self, event):
        self.view_center = list(self.view.camera.center)
        if (event.text == '*'):
            this_data = self.numpy_queue.get()
            head_msg = this_data[0]
            nptype, name = head_msg.split('/')
            if nptype == 'pc':
                self.add_pc(this_data[1], name=name)
                logger.info('Received a Point Cloud')
            elif nptype == 'bbox':
                self.add_bbox(this_data[1])
                logger.info('Received a Bbox')
        if(event.text == 'w' or event.text == 'W'):
            dx, dy = self.get_cam_delta()
            self.view_center[0] += dx
            self.view_center[1] += dy
            self.view.camera.center = self.view_center

        if(event.text == 's' or event.text == 'S'):
            dx, dy = self.get_cam_delta()
            self.view_center[0] -= dx
            self.view_center[1] -= dy
            self.view.camera.center = self.view_center

        if(event.text == 'a' or event.text == 'A'):
            dx, dy = self.get_cam_delta()
            self.view_center[0] -= dy
            self.view_center[1] += dx
            self.view.camera.center = self.view_center

        if(event.text == 'd' or event.text == 'D'):
            dx, dy = self.get_cam_delta()
            self.view_center[0] += dy
            self.view_center[1] -= dx
            self.view.camera.center = self.view_center

        if(event.key == 'up'):
            self.view_center[2] += 1
            self.view.camera.center = self.view_center

        if(event.key == 'down'):
            self.view_center[2] -= 1
            self.view.camera.center = self.view_center

        if(event.text == 'c' or event.text == 'C'):
            # Centered
            self.view_center[0] = 0
            self.view_center[1] = 0
            self.view_center[2] = 0
            self.view.camera.center = self.view_center
    
    def get_cam_delta(self):
        theta = self.view.camera.azimuth
        dx = -np.sin(theta * np.pi / 180)
        dy = np.cos(theta * np.pi / 180)
        return dx, dy
      
            