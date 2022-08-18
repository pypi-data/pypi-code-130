import pandas as pd
from joblib import Parallel, delayed
from simba.read_config_unit_tests import read_config_entry, check_that_column_exist, read_config_file
import os, glob
from simba.features_scripts.unit_tests import read_video_info_csv, read_video_info
from _legacy.test import MovementProcessor
from simba.misc_tools import check_multi_animal_status, get_fn_ext
from simba.drop_bp_cords import createColorListofList
import numpy as np
import cv2

class DataPlotter(object):
    def __init__(self,
                 config_path: str=None,
                 body_part: str=None):

        self.config, self.config_path = read_config_file(config_path), config_path
        self.no_animals = read_config_entry(self.config, 'General settings', 'animal_no', 'int')
        self.project_path = read_config_entry(self.config, 'General settings', 'project_path', data_type='folder_path')
        self.file_type = read_config_entry(self.config, 'General settings', 'workflow_file_type', 'str', 'csv')
        self.save_dir = os.path.join(self.project_path, 'frames', 'output', 'live_data_table')
        if not os.path.exists(self.save_dir): os.makedirs(self.save_dir)
        self.vid_info_df = read_video_info_csv(os.path.join(self.project_path, 'logs', 'video_info.csv'))
        self.in_dir = os.path.join(self.project_path, 'csv', 'outlier_corrected_movement_location')
        self.files_found = glob.glob(self.in_dir + '/*.' + self.file_type)
        self.multi_animal_id_status, self.multi_animal_id_list = check_multi_animal_status(self.config, self.no_animals)
        self.color_lst_of_lst = createColorListofList(self.no_animals, 1)
        self.compute_spacings()
        print('Processing {} video(s)...'.format(str(len(self.files_found))))

    def compute_spacings(self):
        x_spacer, y_spacer = 2, 2
        self.loc_dict = {}
        self.loc_dict['Animal'] = (50, 15)
        self.loc_dict['total_movement_header'] = (250, 15)
        self.loc_dict['current_velocity_header'] = (475, 15)
        self.loc_dict['animals'] = {}
        x_cord, y_cord = 10, 10
        for animal_cnt, animal_name in enumerate(self.multi_animal_id_list):
            self.loc_dict['animals'][animal_name] = {}
            self.loc_dict['animals'][animal_name]['index_loc'] = (int(x_cord * x_spacer),y_cord)
            self.loc_dict['animals'][animal_name]['total_movement_loc'] = (int(x_cord * x_spacer), int((x_cord * y_spacer)))
            x_spacer += 1; y_spacer += 1
            self.loc_dict['animals'][animal_name]['current_velocity_loc'] = (int(x_cord * x_spacer), int((x_cord * y_spacer)))
            x_spacer += 1; y_spacer += 1

    def process_movement(self):
        movement_processor = MovementProcessor(config_path=self.config_path)
        movement_processor.process_movement()
        self.movement = movement_processor.movement_dict

    def create_data_plots(self):
        def multiprocess_img_creation(video_data_slice=None, location_dict=None, animal_ids=None, video_data=None):
            img = np.zeros((480, 640, 3))
            cv2.putText(img, 'Animal', self.loc_dict['Animal'], cv2.FONT_HERSHEY_TRIPLEX, 0.5, (255, 255, 255), 1)
            cv2.putText(img, 'Total movement (cm)', self.loc_dict['total_movement_header'], cv2.FONT_HERSHEY_TRIPLEX, 0.5, (255, 255, 255), 1)
            cv2.putText(img, 'Velocity (cm/s)', self.loc_dict['current_velocity_header'], cv2.FONT_HERSHEY_TRIPLEX, 0.5, (255, 255, 255), 1)
            for animal_cnt, animal_name in enumerate(animal_ids):
                clr = self.color_lst_of_lst[animal_cnt][0]
                total_movement = str(round(video_data[animal_name].iloc[0:video_data_slice.index.max()].sum(), 2))
                current_velocity = str(round(video_data_slice[animal_name].sum(), 2))
                print(self.loc_dict['animals'][animal_name]['index_loc'])
                cv2.putText(img, animal_name, self.loc_dict['animals'][animal_name]['index_loc'], cv2.FONT_HERSHEY_TRIPLEX, 1, clr, 5)
                cv2.putText(img, total_movement, self.loc_dict['animals'][animal_name]['total_movement_loc'], cv2.FONT_HERSHEY_TRIPLEX, 1, clr, 1)
                cv2.putText(img, current_velocity, self.loc_dict['animals'][animal_name]['current_velocity_loc'], cv2.FONT_HERSHEY_TRIPLEX, 1, clr, 1)
                print(np.unique(img))
                cv2.imshow('img', img)
                cv2.waitKey(20000)





        for file_path in self.files_found:
            _, video_name, _ = get_fn_ext(file_path)
            video_data = pd.DataFrame(self.movement[video_name])
            _, _, self.fps = read_video_info(vidinfDf=self.vid_info_df, currVidName=video_name)
            video_data_lst = np.array_split(pd.DataFrame(video_data), int(len(video_data) / self.fps))
            self.imgs = Parallel(n_jobs=1, verbose=2, backend="loky")(delayed(multiprocess_img_creation)(x, self.loc_dict, self.multi_animal_id_list, video_data) for x in video_data_lst)


test = DataPlotter(config_path='/Users/simon/Desktop/troubleshooting/train_model_project/project_folder/project_config.ini')
test.process_movement()
test.create_data_plots()