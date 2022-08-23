from helloai import *
from haidetector import *

wnd = Window('wnd')

# 카메라 객체
camera = Camera()

detector = PoseDetector()

# 무한 반복 
def loop():
    # 카메라 영상 읽기
    img = camera.read()

    img, landmarks = detector.process(img, draw=True)
    print('LANDMARKS >>> ', len(landmarks))

    if len(landmarks) > 30:
        angle, img = detector.calc_angle(img, landmarks[12], landmarks[14], landmarks[16], draw=True)
        print('ANGLLE >>> ', angle)
        
    # 이미지 표시 
    wnd.show(img)

# ---------------------------------------
# HelloAI를 사용하기 위한 실행 방법 
# ---------------------------------------
if __name__ == '__main__':
    run()
    
