import numpy as np  
import cv2
from utils.preprocess import gamma_correction
from utils.print_utils import print_training_stats, show, write_on_image

##################################################
############### REPEATED ALGORITHM  ###############
##################################################
def perform_bottom_operations(shape, lst, clone, name, coordinates, distance, iterList):
  step = 0.05 * clone.shape[0]
  _, first_y = shape[lst]
  position = name.split("_")[1]
  coordinates[f"{name}"]  = np.array((coordinates[f"top_{position}_forehead_coor"][0], first_y))
  cv2.rectangle(clone, coordinates[f"top_{position}_forehead_coor"], coordinates[f"{name}"], (0,0,255), -1)
  distance[f"forehead_{position}_distance"] = np.linalg.norm(coordinates[f"{name}"] - coordinates[f"top_{position}_forehead_coor"])
  write_on_image(clone, f'forehead_{position}:{distance[f"forehead_{position}_distance"]:.1f}', (clone.shape[1] // 2, 30 + int(iterList["iter_forehead"] * step)))
  iterList["iter_forehead"] += 1 

def perform_top_operations(shape, lst, image, name, coordinates):
  first_x, first_y = shape[lst]
  
  average = get_average(first_x, first_y,  detect_and_correct(image))

  # print(f'WHAT IS AVERAGE: {average}')

  first_x, first_y = training(first_x, first_y, average, image)

  coordinates[f"{name}"] = np.array((first_x, first_y))
  # print(f"what is the coordinate for {name}: ", coordinates[f"{name}"])

def training(first_x, first_y, average, image):
  iteratio = 1
  step = 0.01 * image.shape[0]
  while  average > 168 and iteratio < 6:
    first_y =int(first_y - step)
    iteratio +=1 
    cv2.circle(image, (first_x, first_y), 1, (0, 255, 0), -1)

    ROI = image[first_x, first_y]
    
    # print_training_stats(iteratio, first_y, ROI)
    '''
    during training no need to perform another gammna correction
    '''
    get_average(first_x, first_y, image)

    # show(image)
  
  return first_x, first_y
  

'''
@output: return image after performing gamma correciton
'''
def detect_and_correct(image):
  average = np.average(image)
  # print("average: ", "=" * 10, average)
  if average < 120: 
    # print("*" * 10, " increasing light")
    image = gamma_correction(image, 2.5)
  elif average > 200: 
    # print("*" * 10, " decreasing light")
    image =  gamma_correction(image, 0.5)
  return image


def get_average(first_x, first_y, image):        
  ROI = image[first_x-20: first_x+20, first_y, :]
  kernel = np.ones((40, 1,3))
  result = ROI * kernel
  average = np.average(result)
  # print("average: ", "=" * 10, average)
  return average
