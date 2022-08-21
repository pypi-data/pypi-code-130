# 好强大的 pyautogui， 能根据图识别图,然后循环操作
# 可以参考： https://blog.csdn.net/yzy_1996/article/details/85244714
# 可以考虑 算手机分辨率，然后实现手机点击
# import pyautogui
import os, time
# import jieba
from PIL import Image
# from appium import webadb


#region AI自动化相关
# def cv_img_contain_click_pos(img1, img2, isWin, isMultiTouch, click_num=1):
#     ''' 
#     点击img2在img1的位置
#     :param isWin: 电脑是分辨率，手机需要换算分辨率和屏幕大小
#     :param isMultiTouch: 是否是多点触控（所以满足的点，都点击）
#     :param click_num: 点击次数
#     :return {state:是否点击成功,msg:消息提示}
#     '''
#     resultData = {'state': False, 'msg':''}
#     pos_list = cv_img_contain_img_points(img1, img2)
#     if not pos_list or len(pos_list)==0:
#         resultData['msg'] = '没有匹配到对应图'
#     else:
#         for item in pos_list[:]:
#             if isWin:
#                 pyautogui.moveTo(item[0],item[1])
#                 pyautogui.click(clicks=click_num, interval=0.2)
#             else:
#                 for clickIndex in range(0, click_num):
#                     self.adbService.Click(item[0],item[1])
#                     time.sleep(0.2)
#             if not isMultiTouch:
#                 break
#         resultData['state'] = True
#     return resultData

#endregion
