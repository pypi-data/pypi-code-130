from asyncio.windows_utils import pipe
import reactivex as rx
import reactivex.operators as ops



# cp  = rx.pipe()(ops.map(sum),ops.map(lambda x:x+1))
# cp = rx.compose(print,lambda x:x+1)


def run(source):
    return source.pipe(ops.map(sum))
p = rx.pipe(ops.map(sum))
rx.of([1,2,3,4,5],[1,2]).pipe(
    ops.map(rx.of),
    ops.map(p),
    
    ops.merge_all()
    ).subscribe(print,on_error=print)

import cv2
import cv2

img = cv2.imread("data/Lenna.png")
gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# -------------------Sobel边缘检测------------------------
x = cv2.Sobel(gray_img, -1, 1, 1, 3, 1,1,borderType=cv2.BORDER_DEFAULT)
print(x)
# y = cv2.Sobel(gray_img, -1, 0, 1)
# cv2.convertScaleAbs(src[, dst[, alpha[, beta]]])
# 可选参数alpha是伸缩系数，beta是加到结果上的一个值，结果返回uint类型的图像
Scale_absX = cv2.convertScaleAbs(x)  # convert 转换  scale 缩放
print(Scale_absX)
# Scale_absY = cv2.convertScaleAbs(y)
# result = cv2.addWeighted(Scale_absX, 0.5, Scale_absY, 0.5, 0)
# ----------------------显示结果----------------------------
cv2.imshow('img', gray_img)
cv2.imshow('Scale_absX', Scale_absX)
# cv2.imshow('Scale_absY', Scale_absY)
# cv2.imshow('result', result)
cv2.waitKey(0)
cv2.destroyAllWindows()

