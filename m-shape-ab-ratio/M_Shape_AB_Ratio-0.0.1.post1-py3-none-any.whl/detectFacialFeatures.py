from collections import OrderedDict
from imutils import face_utils
import dlib
import cv2
import numpy as np
from .utils.drawAndCalculate import draw_calc_brows
from .utils.print_utils import show, return_stats
from .utils.algorithm_utils import perform_top_operation, perform_bottom_operation, tophead_background

"in order to be able to call other module (in this case top head) to get the highest point of the head"
import sys 
# ABOUT TO CHANGE FOR THE MODULE CALLING
# sys.path.append(r"C:\Users\ferdy\Documents\Project5")
sys.path.append(r"/Users/ferdy/Documents/HairCoSys")
print(sys.path)
from tophead.predict import get_coordinate, predict



# Create DataFrame from multiple lists



# PERSON = 1

def process(image_path, o_shape_image_path, p,  file_path, top_to_chin, top_to_hair, a_b_ratio, black_overall, result):
    # global PERSON
    detector = dlib.get_frontal_face_detector()
    predictor = dlib.shape_predictor(p)

    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    image = cv2.resize(image, (224,224), interpolation = cv2.INTER_AREA)
    gray = cv2.resize(gray, (224,224), interpolation = cv2.INTER_AREA)

    # Get faces into webcam's image
    rects = detector(gray, 0)

    coordinates = {
        "left_brow": 0,
        "right_brow": 0,
        "nose_central_coor": 0,
        "chin_central_coor": 0,
        "tophead": 0,
        "top": {
            "left": {
                "top_left_1_forehead_coor": 0,
                "top_left_2_forehead_coor": 0,
                "top_left_3_forehead_coor": 0,
                "top_left_4_forehead_coor": 0,
                "top_left_5_forehead_coor": 0,
            },
            "right": {
                "top_right_1_forehead_coor": 0,
                "top_right_2_forehead_coor": 0,
                "top_right_3_forehead_coor": 0,
                "top_right_4_forehead_coor": 0,
                "top_right_5_forehead_coor": 0,
            },
            "top_central_1_forehead_coor": 0,
        },
        "bottom": {
            "left": {
                "bottom_left_1_forehead_coor": 0,
                "bottom_left_2_forehead_coor": 0,
                "bottom_left_3_forehead_coor": 0,
                "bottom_left_4_forehead_coor": 0,
                "bottom_left_5_forehead_coor": 0,
            },
            "right": {
                "bottom_right_1_forehead_coor": 0,
                "bottom_right_2_forehead_coor": 0,
                "bottom_right_3_forehead_coor": 0,
                "bottom_right_4_forehead_coor": 0,
                "bottom_right_5_forehead_coor": 0,
            },
            "bottom_central_1_forehead_coor": 0
        }
    }

    FACIAL_LANDMARKS_IDXS = OrderedDict(
        [
            ("left_eyebrow", (17, 22)),
            ("right_eyebrow", (22, 27)),

            ("nose_central_coor", (33)),
            ("chin_central_coor", (8)),

            ("top_left_1_forehead_coor", (75)),
            ("top_left_2_forehead_coor", (76)),
            ("top_left_3_forehead_coor", (68)),
            ("top_left_4_forehead_coor", (69)),
            ("top_left_5_forehead_coor", (70)),

            ("top_right_1_forehead_coor", (71)),
            ("top_right_2_forehead_coor", (80)),
            ("top_right_3_forehead_coor", (72)),
            ("top_right_4_forehead_coor", (73)),
            ("top_right_5_forehead_coor", (79)),

            ("top_central_1_forehead_coor", (71)),
            ("tophead", (71)),

            ("bottom_left_1_forehead_coor", (17)),
            ("bottom_left_2_forehead_coor", (18)),
            ("bottom_left_3_forehead_coor", (19)),
            ("bottom_left_4_forehead_coor", (20)),
            ("bottom_left_5_forehead_coor", (21)),

            ("bottom_right_1_forehead_coor", (22)),
            ("bottom_right_2_forehead_coor", (23)),
            ("bottom_right_3_forehead_coor", (24)),
            ("bottom_right_4_forehead_coor", (25)),
            ("bottom_right_5_forehead_coor", (26)),

            ("bottom_central_1_forehead_coor", (21)),
        ]
    )

    iterList = {"iter_brows": 0, "iter_forehead": 0}
# For each detected face, find the landmark.
    for (i, rect) in enumerate(rects):

        print("\n", 6 * "=", f"PATH: {image_path}", 6 * "=")
        # Make the prediction and transfom it to numpy array
        shape = predictor(gray, rect)
        shape = face_utils.shape_to_np(shape)

        clone = image.copy()

        
        distance = {
            "forehead": {
                "left": {
                    "1": 0,
                    "2": 0,
                    "3": 0,
                    "4": 0,
                    "5": 0,
                },
                "right": {
                    "1": 0,
                    "2": 0,
                    "3": 0,
                    "4": 0,
                    "5": 0,
                },
                "central": {
                    "1": 0
                }
            },
            "left_brow": 0,
            "right_brow": 0,
            "forehead2nose": 0,
            "nose2chin": 0,
            "tophead": 0
        }

    

        for (name, lst) in FACIAL_LANDMARKS_IDXS.items():
            if name == "left_eyebrow":
                distance["left_brow"] = draw_calc_brows(
                    clone, shape, name, lst, iterList
                )
            elif name == "tophead":
                x  = coordinates["top"]["top_central_1_forehead_coor"][0]
                y =  get_coordinate(image_path,x)
                if y == None: 
                    return
                print('WHAT IS X AND Y', x, y)
                coordinates["tophead"] = np.array((x,y))
            elif name == "right_eyebrow":
                distance["right_brow"] = draw_calc_brows(
                    clone, shape, name, lst, iterList
                )
            elif name == "nose_central_coor":
                coordinates["nose_central_coor"] = np.array(
                    (shape[lst][0], shape[lst][1])
                )
            elif name == "chin_central_coor":
                coordinates["chin_central_coor"] = np.array(
                    (shape[lst][0], shape[lst][1])
                )
            elif name.startswith("top"):
                top_or_bottom, left_or_right, _, _, _ = name.split(
                    "_")  # check if top  / bottom
                if left_or_right != "central":
                    perform_top_operation(
                        shape, lst, image, top_or_bottom, left_or_right, name, coordinates)
                else:
                    first_x, first_y = shape[lst]
                    coordinates[top_or_bottom][name] = np.array(
                        (first_x, first_y))
            elif name.startswith("bottom"):
                top_or_bottom, left_or_right, _, _, _ = name.split(
                    "_")  # check if top  / bottom
                if left_or_right != "central":
                    perform_bottom_operation(
                        shape, lst, clone,  top_or_bottom, left_or_right, name, coordinates, distance, iterList)
                else:
                    first_x, first_y = shape[lst]
                    coordinates[top_or_bottom][name] = np.array(
                        (first_x, first_y))
                    line_num = name.split("_")[2]
                    next_name = "_".join(name.split("_")[1:])
                    distance[f"forehead"][left_or_right][line_num] = abs(np.linalg.norm(
                         coordinates[top_or_bottom][f"{name}"] - coordinates["top"][f"top_{next_name}"]))

        distance["forehead2nose"] = np.linalg.norm(
            coordinates["bottom"]["bottom_central_1_forehead_coor"]
            - coordinates["nose_central_coor"]
        )
        distance["nose2chin"] = np.linalg.norm(
            coordinates["nose_central_coor"] - coordinates["chin_central_coor"]
        )

        # THE DISTANCE OF THE TOP HEAD TO THE FOREHEAD BOTTOM CENTRAL
        distance["tophead"] = abs(np.linalg.norm(
            coordinates["tophead"] - coordinates["bottom"]["bottom_central_1_forehead_coor"]
        ))
        avg_hair2brow = abs(np.array([list(distance["forehead"]["left"].values()) + 
                                list(distance["forehead"]["right"].values())
                                ]).mean())

        # TODO: from top head to chin
        b = distance["tophead"]+  distance["forehead2nose"] + distance["nose2chin"]

        a = abs(distance["tophead"] - avg_hair2brow)

        print("TOPHEAD TO HAIR: ", a)
        print(__name__, "FACE HEIGHT: ",b)

        black_ratio = predict(o_shape_image_path)

        file_path.append(image_path)
        top_to_hair.append(a)
        top_to_chin.append(b)
        a_b_ratio.append(round(a/b, 2))
        black_overall.append(round(black_ratio, 2))
        ratio = (a * black_ratio /b)
        result.append(round(ratio, 2))

        print(f"A/B: {a/b:.2f}")
        print(f'BLACK HAIR/ OVERALL RATIO: {black_ratio:.2f}')
        print(f'RESULT: {ratio:.2f}')
    # PERSON += 1
    # clean up iterator for next image
    for key in iterList.keys():
        iterList[key] = 0
