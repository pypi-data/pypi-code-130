try:
    import mediapipe as mp

except ImportError:
    print("[!!] Package 'mediapipe' is not installed:")
    print("     1. Use python version 3.7 or below.")
    print("     2. Run this command in the terminal: pip install mediapipe")

try:
    import cv2

except ImportError:
    print("[!!] Package 'cv2' is not installed:")
    print("     Run this command in the terminal: pip install opencv-python")

class HandRecogniser:
    def __init__(self, static_image_mode=False, max_num_hands=2, model_complexity=1, min_detection_confidence=0.5, min_tracking_confidence=0.5):
        self.static_image_mode = static_image_mode
        self.max_num_hands = max_num_hands
        self.model_complexity = model_complexity
        self.min_detection_confidence = min_detection_confidence
        self.min_tracking_confidence = min_tracking_confidence

        self.hands = mp.solutions.hands.Hands(
            self.static_image_mode,
            self.max_num_hands,
            self.model_complexity,
            self.min_detection_confidence,
            self.min_tracking_confidence
        )
        self.numHands = 0

    def cvt_ratio2pixels(self, hand_landmark, image):
        cnv_landmark_coordinates = []
        for id, landmark in enumerate(hand_landmark):
            img_width, img_height, img_channels = image.shape
            x_axis = img_width * landmark.x
            y_axis = img_height * landmark.y

            cnv_landmark_coordinates.append((id, int(x_axis), int(y_axis))) # Change from float to int

        return cnv_landmark_coordinates

    def findHands(self, image_orginal, draw=True):
        try:
            # Create the hands object
            hands = self.hands

            # Read the image
            image = None
            if isinstance(image_orginal, str):
                image = cv2.imread(image_orginal)
            else:
                image = image_orginal

            # Convert image from BGR to RGB
            imageRGB = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

            # Process the image to get landmarks
            processed_image = hands.process(imageRGB)

            # Check if any hands are detected
            hands_in_image = processed_image.multi_hand_landmarks
            hands_landmarks_positions = []
            if hands_in_image:
                # Draw the landmarks on the image and get landmark positions for each hand
                for hand_landmarks in hands_in_image:
                    if draw:
                        mp.solutions.drawing_utils.draw_landmarks(image, hand_landmarks, mp.solutions.hands.HAND_CONNECTIONS)
                    hands_landmarks_positions.append(self.cvt_ratio2pixels(hand_landmarks.landmark, image))

            # [[(), (), ()], [(), (), ()]]
            # Get the number of hands
            self.numHands = len(hands_landmarks_positions)

            # Return image with hands recognised / Return the hands' landmarks coordinates
            return image, hands_landmarks_positions

        except cv2.error:
            return image_orginal, []

    def getFingerState(self, image_original, finger, hand_num = 1, hand_orientation = "right"):
        # Get Hands in "original_image" along with the hand landmarks' positions
        image_processed, hand_landmarks_pos = self.findHands(image_original, draw=False)

        # Check if finger is valid and if not, raise an error!
        fingers = ["thumb", "index", "middle", "ring", "pinky"]
        if finger not in fingers:
            raise NameError(f"'{finger}' is not a finger name! Chose from these: ['Thumb', 'Index', 'Middle', 'Ring', 'Pinky']")

        # Get the hand according to the hand num from the hand landmarks' positions
        try:
            hand_landmarks_pos = hand_landmarks_pos[hand_num-1]
        except IndexError:
            raise ValueError("Unable to find any fingers in the provided image")

        # Create an object of the Hand() class
        hand = Hand([hand_landmarks_pos]) # We specify the extra brackets for the right syntax

        # Check which finger was given and check it's state
        finger_state = None
        if finger == "index":
            if hand.index_finger_tip["y axis"] > hand.index_finger_pip["y axis"]:
                # Index is closed
                finger_state = False
            else:
                # Index is opened
                finger_state = True

        elif finger == "middle":
            if hand.middle_finger_tip["y axis"] > hand.middle_finger_pip["y axis"]:
                # Middle is closed
                finger_state = False
            else:
                # Middle is opened
                finger_state = True

        elif finger == "ring":
            if hand.ring_finger_tip["y axis"] > hand.ring_finger_pip["y axis"]:
                # Ring is closed
                finger_state = False
            else:
                # Ring is opened
                finger_state = True

        elif finger == "pinky":
            if hand.pinky_tip["y axis"] > hand.pinky_pip["y axis"]:
                # Pinky is closed
                finger_state = False
            else:
                # Pinky is opened
                finger_state = True

        elif finger == "thumb":
            if hand_orientation == "right":
                if hand.thumb_tip["x axis"] < hand.thumb_ip["x axis"]:
                    # Thumb is closed
                    finger_state = False
                else:
                    # Thumb is opened
                    finger_state = True

            else:
                if hand.thumb_tip["x axis"] > hand.thumb_ip["x axis"]:
                    # Thumb is closed
                    finger_state = False
                else:
                    # Thumb is opened
                    finger_state = True

        # Return the finger state ==> True for open / False for closed
        return finger_state

    def matchFingerState(self, image_original, stateList, hand_num = 1, hand_orientation="right"):
        # Get each state of finger and save it to a list ==> fingerStates
        thumbState = self.getFingerState(image_original, "thumb", hand_num=hand_num, hand_orientation=hand_orientation)
        indexState = self.getFingerState(image_original, "index", hand_num=hand_num, hand_orientation=hand_orientation)
        middleState = self.getFingerState(image_original, "middle", hand_num=hand_num, hand_orientation=hand_orientation)
        ringState = self.getFingerState(image_original, "ring", hand_num=hand_num, hand_orientation=hand_orientation)
        pinkyState = self.getFingerState(image_original, "pinky", hand_num=hand_num, hand_orientation=hand_orientation)

        fingerStates = [thumbState, indexState, middleState, ringState, pinkyState]

        # Compare it with the stateList
        result = fingerStates == stateList

        # Return True or False according to the match ==> result
        return result

    def getHandOrientation(self, image_original, hand_num = 1):
        # Get hands in the image
        image, hand_landmarks_pos = self.findHands(image_original, draw=False)

        # Extract the hand according to the hand number
        try:
            hand_landmarks_pos = hand_landmarks_pos[hand_num-1]
        except IndexError:
            raise ValueError("Unable to find any hands in the provided image")

        # Create hand object
        hand = Hand([hand_landmarks_pos])

        # Check thumb position and decide the hand orientation ==> left or right
        if hand.thumb_tip["x axis"] > hand.thumb_ip["x axis"]:
            orientation = "right"

        elif hand.thumb_tip["x axis"] < hand.thumb_ip["x axis"]:
            orientation = "left"

        # Return the hand orientation
        return orientation

class Hand:
    def __init__(self, hand_pos_landm):
        if len(hand_pos_landm) > 1:
            raise ValueError(f"{len(hand_pos_landm)} is too many hands. Please specify only 1 hand in the right syntax")

        else:
            if len(hand_pos_landm) < 1:
                raise ValueError(f"{len(hand_pos_landm)} is less than required amounts of hands. Please only specify 1 hand in the right syntax")
            else:
                self.hand_pos_lanm = hand_pos_landm[0]

        self.wrist = {}
        self.thumb_cmc = {}
        self.thumb_mcp = {}
        self.thumb_ip = {}
        self.thumb_tip = {}
        self.index_finger_mcp = {}
        self.index_finger_pip = {}
        self.index_finger_dip = {}
        self.index_finger_tip = {}
        self.middle_finger_mcp = {}
        self.middle_finger_pip = {}
        self.middle_finger_dip = {}
        self.middle_finger_tip = {}
        self.ring_finger_mcp = {}
        self.ring_finger_pip = {}
        self.ring_finger_dip = {}
        self.ring_finger_tip = {}
        self.pinky_mcp = {}
        self.pinky_pip = {}
        self.pinky_dip = {}
        self.pinky_tip = {}

        self.__populate_variables__()

    def __populate_variables__(self):
        for landmark in self.hand_pos_lanm:
            id = landmark[0] # First value corresponds to the landmark of hand
            x_axis = landmark[1] # x value
            y_axis = landmark[2] # y value

            if id == 0:
                self.wrist["id"] = id
                self.wrist["x axis"] = x_axis
                self.wrist["y axis"] = y_axis

            elif id == 2:
                self.thumb_mcp["id"] = id
                self.thumb_mcp["x axis"] = x_axis
                self.thumb_mcp["y axis"] = y_axis

            elif id == 1:
                self.thumb_cmc["id"] = id
                self.thumb_cmc["x axis"] = x_axis
                self.thumb_cmc["y axis"] = y_axis

            elif id == 3:
                self.thumb_ip["id"] = id
                self.thumb_ip["x axis"] = x_axis
                self.thumb_ip["y axis"] = y_axis

            elif id == 4:
                self.thumb_tip["id"] = id
                self.thumb_tip["x axis"] = x_axis
                self.thumb_tip["y axis"] = y_axis

            elif id == 5:
                self.index_finger_mcp["id"] = id
                self.index_finger_mcp["x axis"] = x_axis
                self.index_finger_mcp["y axis"] = y_axis

            elif id == 6:
                self.index_finger_pip["id"] = id
                self.index_finger_pip["x axis"] = x_axis
                self.index_finger_pip["y axis"] = y_axis

            elif id == 7:
                self.index_finger_dip["id"] = id
                self.index_finger_dip["x axis"] = x_axis
                self.index_finger_dip["y axis"] = y_axis

            elif id == 8:
                self.index_finger_tip["id"] = id
                self.index_finger_tip["x axis"] = x_axis
                self.index_finger_tip["y axis"] = y_axis

            elif id == 9:
                self.middle_finger_mcp["id"] = id
                self.middle_finger_mcp["x axis"] = x_axis
                self.middle_finger_mcp["y axis"] = y_axis

            elif id == 10:
                self.middle_finger_pip["id"] = id
                self.middle_finger_pip["x axis"] = x_axis
                self.middle_finger_pip["y axis"] = y_axis

            elif id == 11:
                self.middle_finger_dip["id"] = id
                self.middle_finger_dip["x axis"] = x_axis
                self.middle_finger_dip["y axis"] = y_axis

            elif id == 12:
                self.middle_finger_tip["id"] = id
                self.middle_finger_tip["x axis"] = x_axis
                self.middle_finger_tip["y axis"] = y_axis

            elif id == 13:
                self.ring_finger_mcp["id"] = id
                self.ring_finger_mcp["x axis"] = x_axis
                self.ring_finger_mcp["y axis"] = y_axis

            elif id == 14:
                self.ring_finger_pip["id"] = id
                self.ring_finger_pip["x axis"] = x_axis
                self.ring_finger_pip["y axis"] = y_axis

            elif id == 15:
                self.ring_finger_dip["id"] = id
                self.ring_finger_dip["x axis"] = x_axis
                self.ring_finger_dip["y axis"] = y_axis

            elif id == 16:
                self.ring_finger_tip["id"] = id
                self.ring_finger_tip["x axis"] = x_axis
                self.ring_finger_tip["y axis"] = y_axis

            elif id == 17:
                self.pinky_mcp["id"] = id
                self.pinky_mcp["x axis"] = x_axis
                self.pinky_mcp["y axis"] = y_axis

            elif id == 18:
                self.pinky_pip["id"] = id
                self.pinky_pip["x axis"] = x_axis
                self.pinky_pip["y axis"] = y_axis

            elif id == 19:
                self.pinky_dip["id"] = id
                self.pinky_dip["x axis"] = x_axis
                self.pinky_dip["y axis"] = y_axis

            elif id == 20:
                self.pinky_tip["id"] = id
                self.pinky_tip["x axis"] = x_axis
                self.pinky_tip["y axis"] = y_axis
