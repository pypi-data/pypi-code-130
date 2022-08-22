import cv2

##################################################
############### PRINTING UTILITIES ###############
##################################################

# def format_string(text): 
#   print("=" * 10, f' {text} ', "=" * 10, "\n")

def format_string(text): 
  return "=" * 10 +  f' {text} ' +  "=" * 10 +  "\n"

# def print_stats(top_bottom_distance, left, right, m_shape=False):
#   measurement_type = 'mshape' if m_shape else 'forehead distance'

#   format_string(f'PRINT STATS FOR {measurement_type}')

#   print(f'forehead central distance: {top_bottom_distance}')

#   if m_shape:
#     print(f'left forehead distance: {left}')
#     print(f'right forehead distance: {right}')
#     total_dist = left + right + top_bottom_distance
#     left = left/ total_dist
#     top_bottom_distance = top_bottom_distance/ total_dist
#     right = right/ total_dist
#     print(f'RATIO: \n LEFT: {left} CENTRAL: {top_bottom_distance:.2f} : RIGHT: {right}')


#   if not m_shape:
#     print(f'left brow distance: {left}')
#     print(f'right brow distance: {right}')
#     print(f'ratio forehead line to left eyebrow: {(top_bottom_distance / left):.2f}')
#     print(f'ratio forehead line to right eyebrow: {(top_bottom_distance / right):.2f}')
#   print("\n")

def return_stats(top_bottom_distance, left, right, m_shape=False):
  text = ""
  measurement_type = 'M-SHAPE' if m_shape else 'FNC (FOREHEAD-NOSE-CHIN)'

  text += format_string(f'{measurement_type} PROJECT')

  text += (f'forehead central distance: {top_bottom_distance} \n')

  if m_shape:
    text += (f'left forehead distance: {left}\n')
    text += (f'right forehead distance: {right}\n')
    total_dist = left + right + top_bottom_distance
    left = left/ total_dist
    top_bottom_distance = top_bottom_distance/ total_dist
    right = right/ total_dist

    text += (f'{format_string("RATIO")}LEFT: {left}\nCENTRAL: {top_bottom_distance:.2f}\nRIGHT: {right}')

    print(left)
    diag = 0
    if left> 0.39:
      diag += 1
    if right> 0.39:
      diag += 1
    if top_bottom_distance < left and top_bottom_distance < right:
      diag += 1
    if diag == 3: 
      diag = 'yes'
    else: 
      diag = 'no' 

    return [left, top_bottom_distance, right, diag]


  if not m_shape:
    # text += (f'left brow distance: {left}\n')
    # text += (f'right brow distance: {right}\n')
    # text += (f'ratio forehead line to left eyebrow: {(top_bottom_distance / left):.2f}')
    # text += (f'ratio forehead line to right eyebrow: {(top_bottom_distance / right):.2f}')
    text += (f'forehead2nose distance: {left}\n')
    text += (f'nose2chin: {right}\n')
    total_dist = left + right + top_bottom_distance
    left = left/ total_dist
    top_bottom_distance = top_bottom_distance/ total_dist
    right = right/ total_dist
    text += (f'RATIO: \nFOREHEAD2NOSE: {left} FOREHEAD: {top_bottom_distance:.2f} : NOSE2CHIN: {right}')
  return text

def print_training_stats(iteratio, first_y, ROI):
  print(3 * "*", f'iter: {iteratio}', 3 * "*")
  print("WHAT IS FIRST Y: ", "=" * 20, first_y)

  print('extending forehead line')

  print('WHAT IS ROI: ',ROI)

##################################################
############### OPEN CV DRAW AND SHOW UTILITIES ###############
##################################################

def write_on_image(clone, text, position): 
  cv2.putText(clone, f'{text}', position, cv2.FONT_HERSHEY_SIMPLEX, 0.5 * clone.shape[1] / clone.shape[0], (0, 0, 255), 2)

def show(image):
  cv2.imshow("image",image)
  cv2.waitKey(0)
  cv2.destroyAllWindows()

