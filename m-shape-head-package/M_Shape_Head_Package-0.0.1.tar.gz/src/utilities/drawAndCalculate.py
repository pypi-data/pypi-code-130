from collections import OrderedDict
from imutils import face_utils
import dlib
import cv2
import numpy as np
from utils.print_utils import show, write_on_image 


def draw_calc_brows(clone, shape, name, lst, iterList):
  step = 0.05 * clone.shape[0]
  i, j = lst
  write_on_image(clone, name,  (10, 30 + int(iterList["iter_brows"] * step)))

  # print('WHAT IS I, J: NAME', i, j, name)
  first_x, first_y = shape[i]
  last_x, last_y = shape[j-1]
  first_dim = np.array((first_x, first_y))
  last_dim = np.array((last_x, last_y))
  distance = np.linalg.norm(first_dim - last_dim)
  # print(first_dim, "\n", last_dim, '\n distance: ', distance)
  cv2.line(clone, first_dim, last_dim, (0,0,255), 1)
  write_on_image(clone, f'{distance:.2f}',  (clone.shape[1] // 3, 30 + int(iterList["iter_brows"] * step)))
  # show(clone)
  iterList["iter_brows"] += 1
  return distance
