from helloai import *
from haidetector import *

wnd = Window('wnd')

# 카메라 객체
camera = Camera()

detector = TMImageModel()
detector.load_model('C:\\Users\\user\\Downloads\\converted_keras')

# 무한 반복 
def loop():
    # 카메라 영상 읽기
    img = camera.read()

    label = detector.process(img)
    img = img.text((5,5), text=label, size=40, color=(255, 0, 0))
    print('LABEL >>> ', label)
        
    # 이미지 표시 
    wnd.show(img)

# ---------------------------------------
# HelloAI를 사용하기 위한 실행 방법 
# ---------------------------------------
if __name__ == '__main__':
    run()
    
