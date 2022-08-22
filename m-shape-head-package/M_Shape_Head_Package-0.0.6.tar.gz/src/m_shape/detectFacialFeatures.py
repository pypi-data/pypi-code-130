from collections import OrderedDict
from imutils import face_utils
import dlib
import cv2
import numpy as np 
from utilities.drawAndCalculate import draw_calc_brows
from utilities.print_utils import show, return_stats
from utilities.algorithm_utils import perform_top_operations, perform_bottom_operations

person = 1
def process_mshape(image_path, m_shape, predictor):
  global person
  detector = dlib.get_frontal_face_detector()
  predictor = dlib.shape_predictor(predictor)

  image = cv2.imread(image_path)
  gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
      
  # Get faces into webcam's image
  rects = detector(gray, 0)
  
  coordinates = {
    "left_brow" : 0,
    "right_brow" : 0,
    "top_central_forehead_coor" : 0,
    "bottom_central_forehead_coor" : 0,
    "top_right_forehead_coor" : 0,
    "bottom_right_forehead_coor" : 0,
    "top_left_forehead_coor" : 0,
    "bottom_left_forehead_coor" : 0,
    "nose_central_coor" : 0,
    "chin_central_coor" : 0,
  }
  FACIAL_LANDMARKS_IDXS = OrderedDict([
      ("left_eyebrow", (17, 22)),
      ("right_eyebrow", (22, 27)),
      ("top_right_forehead_coor", (72)), 
      ("bottom_right_forehead_coor", (24)), 
      ("top_left_forehead_coor", (69)), 
      ("bottom_left_forehead_coor", (18)), 
      ("top_central_forehead_coor", (71)), 
      ("bottom_central_forehead_coor", (21)), 
      ("nose_central_coor", (33)), 
      ("chin_central_coor", (8)), 
    ])
  
  iterList = {
    "iter_brows": 0, 
    "iter_forehead": 0
  }

  # For each detected face, find the landmark.
  for (i, rect) in enumerate(rects):
      print("\n",6* "=", f"PERSON: {person} PATH: {image_path}",6 * "=")
      # Make the prediction and transfom it to numpy array
      shape = predictor(gray, rect)
      shape = face_utils.shape_to_np(shape)

      '''
      OUTPUT FOR EVERY FACE IS IN CLONE
      '''      
      clone = image.copy() 

      distance = {
        "forehead_central_distance":0,
        "forehead_left_distance":0,
        "forehead_right_distance":0,
        "left_brow":0,
        "right_brow":0,
        "forehead2nose": 0, 
        "nose2chin": 0
      }
      
      '''
      NOTES FOR PERFORM_operation: 
      we pass coordinates are part of mutable object, so when our algorithm runs, the changes of value in coordinates can be reflected. 
      since we already initialize the keys for the dictionary, updating or reassigning the value will return as pass by reference.
      '''

      for (name, lst) in FACIAL_LANDMARKS_IDXS.items():
        if name == 'left_eyebrow': 
          distance["left_brow"] = draw_calc_brows(clone, shape, name, lst, iterList)
        elif name == 'right_eyebrow': 
          distance["right_brow"] = draw_calc_brows(clone, shape, name, lst, iterList)
        elif name == 'nose_central_coor': 
          coordinates["nose_central_coor"] = np.array((shape[lst][0], shape[lst][1]))
        elif name == 'chin_central_coor': 
          coordinates["chin_central_coor"] = np.array((shape[lst][0], shape[lst][1]))
        elif name.startswith("top"):
          perform_top_operations(shape, lst, image, name, coordinates)
        elif name.startswith("bottom"):
          perform_bottom_operations(shape, lst, clone, name, coordinates, distance, iterList)
  '''
  detect m shape
  '''
  if m_shape == True:
    print(f'WHAT IS MSHAPE: {m_shape}')
    results = return_stats(distance["forehead_central_distance"],distance["forehead_left_distance"], distance["forehead_right_distance"], m_shape=True)
    print(results)
    return results
    # with open(f'./results/{person}.txt', 'w') as f: 
    #   f.write(results)
  # else:
  #   distance["forehead2nose"] =  np.linalg.norm(coordinates["bottom_central_forehead_coor"] - coordinates["nose_central_coor"])
  #   # cv2.line(clone, coordinates["bottom_central_forehead_coor"], coordinates["nose_central_coor"], (0,255,0), 2)
  #   distance["nose2chin"] = np.linalg.norm(coordinates["nose_central_coor"] - coordinates["chin_central_coor"])
    # cv2.line(clone, coordinates["nose_central_coor"], coordinates["chin_central_coor"], (255,0,), 2)

    # results = return_stats(distance["forehead_central_distance"],distance["forehead2nose"], distance["nose2chin"], m_shape=False)
    # print(results)
    # with open(f'./results/{person}.txt', 'w') as f: 
    #   f.write(results)

  # show(clone)
  # cv2.imwrite(f'./results/{person}.jpg', clone)

  # person += 1

  # clean up iterator for next image
  for key in iterList.keys(): 
    iterList[key] = 0
 




        