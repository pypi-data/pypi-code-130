from typing import Dict
import numpy as np
import cv2
from .preprocess import gamma_correction
from .print_utils import print_training_stats, show, write_on_image

##################################################
############### REPEATED ALGORITHM  ###############
##################################################


def perform_bottom_operation(shape, lst, clone,  top_or_bottom: str, left_or_right: str, name: str, coordinates: Dict, distance: Dict, iterList: Dict):
    step = 0.05 * clone.shape[0]
    _, first_y = shape[lst]
    position = left_or_right
    next_name = "_".join(name.split("_")[1:])
    # print(top_or_bottom, left_or_right, next_name)
    # print("=" * 10, "here", "=" * 10,coordinates[top_or_bottom][left_or_right])
    # return
    coordinates[top_or_bottom][left_or_right][name] = np.array(
        (coordinates["top"][left_or_right][f"top_{next_name}"][0], first_y))

    cv2.rectangle(
        clone, coordinates["top"][left_or_right][f"top_{next_name}"], coordinates[top_or_bottom][left_or_right][f"{name}"], (0, 0, 255), -1)

    line_num = name.split("_")[2]
    distance[f"forehead"][left_or_right][line_num] = abs(np.linalg.norm(
        coordinates[top_or_bottom][left_or_right][f"{name}"] - coordinates["top"][left_or_right][f"top_{next_name}"]))
    # write_on_image(clone, f'forehead_{position}:{distance[f"forehead_{position}_distance"]:.1f}', (
    #     clone.shape[1] // 2, 30 + int(iterList["iter_forehead"] * step)))

    iterList["iter_forehead"] += 1


def perform_top_operation(shape, lst, image, top_or_bottom, left_or_right, name, coordinates):
    first_x, first_y = shape[lst]
    '''
    in this use case, we only care about the distance from the hair to the brow
    '''
    coordinates[top_or_bottom][left_or_right][name] = np.array(
        (first_x, first_y))

    return

    # return first_x, first_y

    average = get_average(first_x, first_y,  detect_and_correct(image))

    # print(f'WHAT IS AVERAGE: {average}')

    first_x, first_y = training(first_x, first_y, average, image)

    coordinates[f"{name}"] = np.array((first_x, first_y))
    # print(f"what is the coordinate for {name}: ", coordinates[f"{name}"])

def tophead_background(shape, lst, image, name, coordinates):
    first_x, first_y = shape[lst]
    '''
    in this use case, we only care about the distance from the hair to the brow
    '''
    coordinates[name] = np.array(
        (first_x, first_y))
    image  =   detect_and_correct(image)
    average = get_average(first_x, first_y, image)

    print(f'WHAT IS AVERAGE: {average}')

    first_x, first_y = training(first_x, first_y, average, image)

    coordinates[f"{name}"] = np.array((first_x, first_y))
    # print(f"what is the coordinate for {name}: ", coordinates[f"{name}"])


def training(first_x, first_y, average, image):
    iteratio = 1
    step = 0.025 * image.shape[0]
    if average > 168:
    # while average > 168 and iteratio < 6:
        first_y = int(first_y - step)
        cv2.circle(image, (first_x, first_y), 1, (0, 255, 0), -1)

        ROI = image[first_x, first_y]

        print_training_stats(iteratio, first_y, ROI)
        '''
    during training no need to perform another gammna correction
    '''
        average = get_average(first_x, first_y, image)

        print("WHAT IS AVERAGE; ", average)

        show(image)
    while average < 190 and iteratio < 6:
    # while average > 168 and iteratio < 6:
        first_y = int(first_y - step)
        iteratio += 1
        cv2.circle(image, (first_x, first_y), 1, (0, 255, 0), -1)

        ROI = image[first_x, first_y]

        print_training_stats(iteratio, first_y, ROI)
        '''
    during training no need to perform another gammna correction
    '''
        average = get_average(first_x, first_y, image)

        print("WHAT IS AVERAGE; ", average)

        show(image)


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
        image = gamma_correction(image, 0.5)
    return image


def get_average(first_x, first_y, image):
    ROI = image[first_x-20: first_x+20, first_y , :]
    kernel = np.ones((40, 1, 3))
    result = ROI * kernel
    average = np.average(result)
    # print("average: ", "=" * 10, average)
    return average
