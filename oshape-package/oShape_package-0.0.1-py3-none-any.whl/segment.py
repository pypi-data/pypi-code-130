import cv2
from cv2 import contourArea
import numpy as np

def get_length():
  image = cv2.imread("./results.jpg")
  img = cv2.medianBlur(image.copy(), 3
  )

  cv2.imshow("img", img)
  cv2.waitKey(0)
  cv2.destroyAllWindows()

  imgray = cv2.cvtColor(img.copy(), cv2.COLOR_BGR2GRAY)
  ret, thresh = cv2.threshold(imgray, 127, 255, 0)
  contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

  print(len(contours))

  if len(contours) < 1: 
    return 
  # x,y,w,h = cv2.minAreaRect(contours[0])
  blank = np.zeros((img.shape[0],img.shape[1]), np.uint8)

  area = np.array([contourArea(x) for x in contours])

  print(area)

  rect =  cv2.minAreaRect(contours[np.argmax(area)])
  points = cv2.boxPoints(rect)    
  points = np.int0(points)
  img2 = np.zeros((img.shape[0],img.shape[1]), np.uint8)
  img5 = np.zeros((img.shape[0],img.shape[1]), np.uint8)
  img6 = np.zeros((img.shape[0],img.shape[1]), np.uint8)

  for i in range(len(points)):
    if i == 3:
      cv2.line(img6, points[i] , points[0], (255, 255, 255), 1) 
    else: 
      cv2.line(img6, points[i] , points[i+1], (255, 255, 255), 1) 

  for i in range(len(contours)):
    cv2.drawContours(img2, contours, i, (255, 255, 255), 1)

  '''
  create multiple line segments with the same slope of the shortest length
  '''

  '''
  find the longer side
  '''

  if np.linalg.norm(points[1] - points[2]) > np.linalg.norm(points[0] - points[1]):
    dx_top = np.linspace(points[1][0], points[2][0], 10).astype(int)
    dy_top = np.linspace(points[1][1], points[2][1], 10).astype(int)
    dx_bottom = np.linspace(points[0][0], points[3][0], 10).astype(int)
    dy_bottom = np.linspace(points[0][1], points[3][1], 10).astype(int)
  else: 
    dx_top = np.linspace(points[0][0], points[1][0], 10).astype(int)
    dy_top = np.linspace(points[0][1], points[1][1], 10).astype(int)
    dx_bottom = np.linspace(points[3][0], points[2][0], 10).astype(int)
    dy_bottom = np.linspace(points[3][1], points[2][1], 10).astype(int)

  img3 = np.zeros((img.shape[0],img.shape[1]), np.uint8)

  indices = np.where(img2 != [0])
  coordinates = zip(indices[0], indices[1])
  clst=list(coordinates)

  plst=[]

  for i in range(len(dx_top)):
    print("Line", i)
    cv2.line(img3, (dx_top[i], dy_top[i]) ,(dx_bottom[i], dy_bottom[i]),  (255, 255, 255), 1) 
    cv2.line(img5, (dx_top[i], dy_top[i]) ,(dx_bottom[i], dy_bottom[i]),  (255, 255, 255), 1) 
    result = np.where(img3 > 0)
              
    listOfIndices= list(zip(result[0], result[1]))
    temp=[]
    for indice in listOfIndices:
        if indice in clst:
            re = reversed(indice)
            re = list(re)
            print(re)
            temp.append(re)
    if len(temp)<2:
      continue
    else:
      sortedtemp = sorted(temp, key=lambda tup: tup[1])
      plst.append([sortedtemp[0], sortedtemp[-1]])
    
    img3.fill(0)
                
    
  img4 = np.zeros((img.shape[0],img.shape[1]), np.uint8)
  print(plst)

  max_length = 0

  # font
  font = cv2.FONT_HERSHEY_SIMPLEX
    
  # fontScale
  fontScale = 0.25
    
  # Blue color in BGR
  color = (0, 0, 255)
    
  # Line thickness of 2 px
  thickness = 1
    
  for i in plst:
    cv2.line(image, i[0], i[1],  (255, 255, 255), 1) 
    length = np.linalg.norm(np.array(i[0][0],i[0][1]) -np.array(i[1][0],i[1][1]))
    cv2.putText(image, f'{length}',(i[0]) , font, 
                    fontScale, color, thickness, cv2.LINE_AA)
    max_length = max(max_length, length)

  print(f'max length: ', max_length)

  cv2.imshow("image", image)
  cv2.imshow("img2", img2)
  cv2.imshow("img5", img5)
  cv2.imshow("img6", img6)
  cv2.waitKey(0)
  cv2.destroyAllWindows()

if __name__ == "__main__": 
  get_length()