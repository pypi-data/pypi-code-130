from helloai import *
from haidetector import *

wnd = Window('wnd')

# 카메라 객체
camera = Camera()

# 손을 인식하기 위한 객체 
detector = HandsDetector()

# 무한 반복 
def loop():
    # 카메라 영상 읽기
    img = camera.read()

    # 손 인식하기 
    img, landmarks = detector.process(img, draw=True)
    # 인식된 손의 정보 표시
    print(landmarks)
    
    # 이미지 표시 
    wnd.show(img)

# ---------------------------------------
# HelloAI를 사용하기 위한 실행 방법 
# ---------------------------------------
if __name__ == '__main__':
    run()
    
