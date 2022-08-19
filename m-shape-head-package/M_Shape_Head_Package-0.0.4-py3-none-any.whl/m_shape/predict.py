import argparse
import sys 
from src.m_shape.detectFacialFeatures import process_mshape
import cv2
import numpy as np

from pathlib import Path

SRC_DIR = Path(__file__).resolve().parent.parent

def main(args):
  process_mshape(args.input, args.m_shape, args.config_dat_path)

def predict_m_shape(front_face_img):
  from loguru import logger 
  logger.error("PREDICTING M SHAPE")
  # TODO
  front_face_img = front_face_img.convert('RGB') 

  front_face_img = np.array(front_face_img) 
  # Convert RGB to BGR 
  front_face_img = front_face_img[:, :, ::-1].copy() 

  cv2.imwrite("front_face_img.jpg", front_face_img)
  return process_mshape("front_face_img.jpg", True, SRC_DIR / 'utilities/shape_predictor_81_face_landmarks.dat')

if __name__ == "__main__":
  parser = argparse.ArgumentParser(description='MSHAPE and RECEDING HAIRLINE project')
  parser.add_argument('--single', type=str, default=False)
  # parser.add_argument('--single', type=str, default=r'C:\Users\Public\ferdy\front_face\black\male_black_hair\male_black_hair10.jpg', type=str)
  # TODO
  parser.add_argument('--input', default=r'/Users/ferdy/Documents/HairCoSys/m_shape_standalone/sample_images/male_black_hair0.jpg', type=str)
  parser.add_argument('--m_shape', default=True, type=str)
  parser.add_argument('--verbose', default=False, type=str)
  # TODO
  parser.add_argument('--config_dat_path', default=r'/Users/ferdy/Documents/HairCoSys/m_shape_standalone/utilities/shape_predictor_81_face_landmarks.dat', type=str)
  args=parser.parse_args()
  main(args)
