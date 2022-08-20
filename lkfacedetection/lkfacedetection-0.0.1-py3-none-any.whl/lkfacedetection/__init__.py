import cv2
import mediapipe as mp

mp_face_detection = mp.solutions.face_detection
mp_face_detection = mp.solutions.face_detection
mp_drawing = mp.solutions.drawing_utils
face_detection = mp_face_detection.FaceDetection(model_selection=0, min_detection_confidence=0.5)
mpDraw = mp.solutions.drawing_utils

def faceDetector(image, draw=False):
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    height, width, fc = image.shape
    results = face_detection.process(image)

    image.flags.writeable = True
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    if results.detections:
        detection_results = []
        for detection in results.detections:
            bbox = detection.location_data.relative_bounding_box
            bbox_points = {
                "xmin": int(bbox.xmin * width),
                "ymin": int(bbox.ymin * height),
                "width": int(bbox.width * width),
                "height": int(bbox.height * height)
            }

            detection_results.append(bbox_points)
        x = detection_results[0]['xmin']
        y = detection_results[0]['ymin']
        w = detection_results[0]['width']
        h = detection_results[0]['height']
        if draw:
            cv2.rectangle(image, (x, y), (x + w, y + h), (255, 0, 0), 2)
        return [image, [x, y, w, h]]

    return [image, [0, 0, 0, 0]]