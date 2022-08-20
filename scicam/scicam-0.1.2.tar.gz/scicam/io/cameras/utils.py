import cv2
import time
import warnings

def mark_image(camera, img):    
    # signal it's the first frame afer a pause
    try:
        print(img.shape)
        # img[0, [0, 2, 4, 6]] = 255 
        # img[0, [1, 3, 5, 7]] = 0 
        # img[1, [0, 2, 4, 8]] = 0
        # img[1, [1, 3, 5, 7]] = 255
        # img[2, [0, 2, 4, 6]] = 255 
        # img[2, [1, 3, 5, 7]] = 0 
        # img[3, [0, 2, 4, 8]] = 0
        # img[3, [1, 3, 5, 7]] = 255
        img = cv2.putText(img, "error", (10, 10), cv2.FONT_HERSHEY_SIMPLEX, 5, 127, 5)


    except Exception as error:
        print(error)
        print(f"{camera} cannot mark frame")

    return img


def validate_img(img):
    fail = img is None or img.shape[0] is None
    return not fail

def ensure_img(camera, waiting_time=None):
    print("Alert: img is None")
    before = time.time()
    print(f"Closing {camera}")
    camera.close()
    if waiting_time is not None:
        time.sleep(waiting_time)
    print(f"Opening {camera}")
    camera.open(idx=camera._idx)
    warnings.warn("Recursive call to next_image_default_timeit")
    (code, img), msec =camera._next_image_default_timeit()
    if img.shape[0] is None:

        print("img is still None, look below")
        print(img.shape)
        print(img)
        print("----- ------")

    after = time.time()
    lost_time = after - before
    print(f"Done in {lost_time} seconds")
    # img = mark_image(camera, img.copy())
    # cv2.imwrite(f"/home/vibflysleep/{camera.friendly_name}.png", img)
    return (code, img)


