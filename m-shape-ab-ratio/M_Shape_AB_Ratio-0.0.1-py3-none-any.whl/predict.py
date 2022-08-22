import os, argparse
from .detectFacialFeatures import process
import shutil
import pandas as pd
import numpy as np
import cv2

from pathlib import Path

SRC_DIR = Path(__file__).resolve().parent.parent

def main(args):
  file_path = []
  top_to_hair = []
  top_to_chin  = []
  a_b_ratio = []
  black_overall = []
  result = []
  columns=['file_path','top_to_hair','top_to_chin','a_b_ratio', 'black_overall', 'result']

  if os.path.exists('./results'):
    shutil.rmtree('./results')
    os.makedirs('results')
  else: 
    os.makedirs('results')
  if args.single: 
    process(args.single, args.config_dat_path)
  else: 
    # kl = 0
    for image in os.listdir(args.input):
      # if kl == 10: 
        # break
      if image.endswith('jpg') or image.endswith('png'):
        # kl += 1
        path = os.path.join(args.input, image)
        process(path, args.config_dat_path, file_path, top_to_chin, top_to_hair, a_b_ratio, black_overall, result)
  df = pd.DataFrame(list(zip(file_path,top_to_hair,top_to_chin,a_b_ratio, black_overall, result)), columns=columns)
  df.to_excel('./Results.xlsx')
  
def predict_ab(front, o_shape):
  from loguru import logger 
  logger.error("PREDICTING AB")
  '''
  
  NEED TO PASS THE IMAGE TO THE ALGORITHM OF AB RATIO 

  NEED TO COLLECT THE LOGIC FOR THE M_SHAPE AND AVOID VISUALIZATION            
  
  '''
  front_image = front.convert('RGB') 

  front_image = np.array(front_image) 
  # Convert RGB to BGR 
  front_image = front_image[:, :, ::-1].copy() 

  o_shape_image = o_shape.convert('RGB') 

  o_shape_image = np.array(o_shape_image) 
  # Convert RGB to BGR 
  o_shape_image = o_shape_image[:, :, ::-1].copy() 

  cv2.imwrite("o_shape_temp.jpg", o_shape_image)
  cv2.imwrite("front_shape_temp.jpg", front_image)

  file_path = []
  top_to_hair = []
  top_to_chin  = []
  a_b_ratio = []
  black_overall = []
  result = []

  # columns=['file_path','top_to_hair','top_to_chin','a_b_ratio', 'black_overall', 'result']
  config_dat_path = SRC_DIR / "ab_ratio/utils/shape_predictor_81_face_landmarks.dat"
  process("front_shape_temp.jpg", "o_shape_temp.jpg", config_dat_path, file_path, top_to_chin, top_to_hair, a_b_ratio, black_overall, result)
  os.remove("o_shape_temp.jpg")

  return result[0]
  
if __name__ == "__main__":
  parser = argparse.ArgumentParser(description='MSHAPE and RECEDING HAIRLINE project')
  parser.add_argument('--single', type=str, default=False)
  # parser.add_argument('--single', type=str, default=r'C:\Users\Public\ferdy\front_face\black\male_black_hair\male_black_hair10.jpg', type=str)
  parser.add_argument('--input', default=r'/Users/ferdy/Documents/HairCoSys/m_shape/sample_images', type=str)
  parser.add_argument('--verbose', default=False, type=str)
  # parser.add_argument('--config_dat_path', default=r'C:\Users\ferdy\Documents\Project5\m_shape\utils\shape_predictor_81_face_landmarks.dat', type=str)
  # TODO
  parser.add_argument('--config_dat_path', default=r'/Users/ferdy/Documents/HairCoSys/m_shape/utils/shape_predictor_81_face_landmarks.dat', type=str)
  args=parser.parse_args()
  main(args)
