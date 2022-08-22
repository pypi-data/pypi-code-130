import sys
sys.path.append("D:\Programs\Python\Python39\Lib\site-packages\mpqcv")
from My_CV import *
# -*- coding utf-8 -*-
"""
Created on Sept 2th 09:41 2020

@auther: Peiqi Miao

"""
def cutPic(pic,gre_thre,kernel,thre1,thre2):
    #gre_thre[0,255],kernel卷积核大小，thre1缩小程度，扩大程度
    new_pic = cut_pic(pic,gre_thre,kernel,thre1,thre2)
    return new_pic

def readPic(name):
    img = read_pic(name)
    return img

def showName(name,dely):
    img = cv2.imread(name)
    cv2.namedWindow('show',0)
    cv2.imshow('show', img)
    cv2.waitKey(dely)

def show_img(img,dely):
    cv2.namedWindow('show',0)
    cv2.imshow('show', img)
    cv2.waitKey(dely)

def mkDir(path):
    mkdir(path)

def rot90(img):
    img90 = rot_90(img)
    return img90

def warpMinirect(rect,img):
    warped = warp_minirect(rect,img)
    return warped

def xintaiArg(c):
    a1_w, a1_h, area, baohedu1, match_k = xintai_arg(c)
    return a1_w, a1_h, area, baohedu1, match_k

def give_day_name():
    name = datetime.datetime.now().strftime('%Y%m%d')
    print(name)
    return name

def give_name():
    name = datetime.datetime.now().strftime('%Y%m%d_%H%M%S_%f')
    return name

def preProcessing(frame,gray_thre = 100,kernel = 10,iter1=1,iter2 = 1):
    dst = pre_processing(frame,gray_thre,kernel,iter1,iter2)
    return dst

def find_cMax(cnts):
    c = find_c_max(cnts)
    return c

def findCnts(bin_img):
    cnts = find_cnts(bin_img)
    return cnts

def drawCnts(src,cnts):
    src = draw_cnts(src,cnts)
    return src

def minRect(c):
    rect = min_rect(c)
    return rect

def drawRect(frame,rect):
    frame = draw_rect(frame,rect)
    return frame
def drawCircle(img,center,r,index):
    img =draw_circle(img,center,r,index)
    return  img
def matchC(c1,c2):
    retval = match_c(c1,c2)
    return retval
def concatPic1(img):
    img_01 = concat_pic1(img)
    return img_01

def concatPic2(img, axis):
    img_02 = concat_pic2(img, axis)
    return img_02

def concatPic3(img):
    img_03 = concat_pic3(img)
    return img_03

def tiaoZheng(img_list):
    out = tiaozheng(img_list)
    return out

def tiaoZheng234(img_list):
    out = tiaozheng234(img_list)
    return out

def getGray(img1,channal):
    get_Gray(img1, channal)

if __name__ == '__main__':
    show_name('./test1.jpg',0)
    img = read_pic('./test1.jpg')
    new_pic = cut_pic(img,100,10,1,1)
    show_img(new_pic,0)

