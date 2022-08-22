from .libs import *
from .other import *
def show(img):
    plt.imshow(img)
def save(name, img):
    cv2.imwrite(name, np.array(img))