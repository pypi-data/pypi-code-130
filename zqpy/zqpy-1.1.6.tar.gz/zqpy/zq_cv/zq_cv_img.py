import aircv
import qrcode
import PIL
import numpy
import os
import cv2

import zq_log, zq_file, zq_const

def cv_img_contain_img_points_by_cv2(bg,tp,out=None):
    '''
    滑动模块验证(抖音已验证) 适用于滑动模块
    bg: 背景图片
    tp: 缺口图片
    out:输出图片
    '''
    # 读取背景图片和缺口图片
    bg_img = cv2.imread(bg) # 背景图片
    tp_img = cv2.imread(tp) # 缺口图片
    
    # 识别图片边缘
    bg_edge = cv2.Canny(bg_img, 100, 200)
    tp_edge = cv2.Canny(tp_img, 100, 200)
    
    # 转换图片格式
    bg_pic = cv2.cvtColor(bg_edge, cv2.COLOR_GRAY2RGB)
    tp_pic = cv2.cvtColor(tp_edge, cv2.COLOR_GRAY2RGB)
    
    # 缺口匹配
    res = cv2.matchTemplate(bg_pic, tp_pic, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res) # 寻找最优匹配
    
    tl = max_loc # 左上角点的坐标
    # 绘制方框
    if out:
        th, tw = tp_pic.shape[:2] 
        br = (tl[0]+tw,tl[1]+th) # 右下角点的坐标
        cv2.rectangle(bg_img, tl, br, (0, 0, 255), 2) # 绘制矩形
        cv2.imwrite(out, bg_img) # 保存在本地
    
    # 返回缺口的X坐标
    return tl[0]

def cv_img_contain_img_points_by_aircv(img1, img2): 
    ''' 
    查找img2在img1的位置（坐标从左上角开始）适用于完全一致
    :param img1 图1
    :param img2 图2
    :return 匹配到的所有的列表(第一个列表相识度最高)
    '''
    imsrc = aircv.imread(img1) # 原始图像
    imsch = aircv.imread(img2) # 带查找的部分
    match_result=aircv.find_all_template(imsrc, imsch,0.80)
    #提取出中心点的横纵坐标
    points=[]
    for i in match_result:
        # [result点坐标，rectangle四个角坐标=>左上坐下右上右下，confidence匹配度=>0.8以上基本就是了]
        points.append((i['result']))
    return points

def cv_img_qr_code_create(codeContent, codeCoreImgPath=None, savePath=None, box_size = 8):
    '''
    生成二维码
    :param codeContent: 内容
    :param codeCoreImgPath: 中心图
    :param savePath: 保存路径
    '''
    qr = qrcode.QRCode(
        version=2,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=box_size,
        border=1
    )#各参数具体用法请参考底下链接
    qr.add_data(codeContent)#要显示的内容
    qr.make(fit=True)

    img = qr.make_image()
    img = img.convert('RGBA')
    if codeCoreImgPath:
        icon = PIL.Image.open(codeCoreImgPath)#打开一张图片作为二维码中心图标

        img_w, img_h = img.size
        factor = 4
        size_w = int(img_w / factor)
        size_h = int(img_h / factor)

        icon_w, icon_h = icon.size
        if icon_w > size_w:
            icon_w = size_w
        if icon_h > size_h:
            icon_h = size_h
        icon = icon.resize((icon_w, icon_h), PIL.Image.ANTIALIAS)

        w = int((img_w - icon_w) / 2)
        h = int((img_h - icon_h) / 2)

        img.paste(icon, (w, h))#将图标粘贴到二维码上
    if not savePath:
        savePath = zq_file.dir_auto_path_merage(const.const_caches_dir(), 'qr', 'qrcode.png')
    zq_log.log_debug('二维码保存地址: %s'%savePath)
    img.save(savePath)#保存图片

def cv_img_draw_text(text, sourceImg, targetImg, fontSize=28, fontPath=None, color='#000000', textPosTuple=None, textPosAnchor=None, textPosAnchorOff=None, sizeTuple=None):
    '''
    在图片上绘制文字
    :param text: 内容
    :param sourceImg: 原图
    :param targetImg: 保存图
    :param fontSize: 字体大小
    :param fontPath: 字体路径
    :param color: 字体颜色
    :param textPosTuple 坐标在左上角开始,不填默认最中间
    :param textPosAnchor 坐标锚点，默认最中间 0/默认 中，1 左，2 上，3 右， 4 下
    :param textPosAnchorOff 偏移
    位置：textPosAnchor + textPosAnchorOff适用于添加封面文字, textPosTuple适用于普通文字
    '''
    # 设置字体样式
    font = PIL.ImageFont.truetype(font=fontPath or 'C:/Windows/Fonts/simsun.ttc', size=fontSize)

    # 打开图片
    image = PIL.Image.open(sourceImg)
    draw = PIL.ImageDraw.Draw(image)
    width, height = image.size

    pos = (0,0)
    if textPosTuple:
        pos = textPosTuple
    else:
        if not textPosAnchor or textPosAnchor == 0:
            pos = ((width-fontSize*len(text))/2, (height-fontSize)/2)
        elif not textPosAnchor or textPosAnchor == 1:
            pos = (0, (height-fontSize)/2)
        elif not textPosAnchor or textPosAnchor == 2:
            pos = ((width-fontSize*len(text))/2, 0)
        elif not textPosAnchor or textPosAnchor == 3:
            pos = (width-fontSize*len(text), (height-fontSize)/2)
        elif not textPosAnchor or textPosAnchor == 4:
            pos = ((width-fontSize*len(text))/2, height-fontSize)
        if textPosAnchorOff:
            pos = (pos[0]+textPosAnchorOff[0], pos[1]+textPosAnchorOff[1])

    draw.text(pos, '%s' % text, color, font)
    # 生成图片
    # image.save(targetImg, 'png')
    image.save(targetImg)

    # 压缩图片
    if sizeTuple:
        sImg = PIL.Image.open(targetImg)
        # resize 是裁剪， thumbnail 不会裁剪，是等比缩放
        if sImg.size[0] < sizeTuple[0] and sImg.size[1] < sizeTuple[1]:
            dImg = sImg.resize(sizeTuple, PIL.Image.ANTIALIAS)
            dImg.save(targetImg)
        else:
            sImg.thumbnail(sizeTuple, PIL.Image.ANTIALIAS)
            sImg.save(targetImg)

def cv_img_cut(imgPath, saveDir, saveName, hCutNum, vCutNum=1):
    '''
    图片切图
    :param imgPath:图片地址
    :param saveDir:保存文件夹
    :param saveName:保存名字
    :param hCutNum:横向数量
    :param vCutNum:纵向数量
    '''
    image = PIL.Image.open(imgPath)
    width, height = image.size
    item_width = int(width / hCutNum)
    item_height = int(height / vCutNum)
    box_list = []    
    # (left, upper, right, lower)
    if vCutNum and vCutNum != 1 :
        for j in range(vCutNum):
            for i in range(hCutNum):
                box = (item_width * i, item_height * j, item_width * (i + 1), item_height * (j + 1))
                box_list.append(box)
    else:
        for i in range(hCutNum):
            box = (i*item_width,0,(i+1)*item_width,height)
            box_list.append(box)

    image_list = [image.crop(box) for box in box_list]    
    #保存
    index = 1
    suffixName = '.png'
    for image in image_list:
        image.save('%s%s'%(saveDir, saveName)+str(index) + suffixName)
        index += 1

def cv_img_su_miao(sourceImg, targetImg):
    '''
    将原图转化为 灰度图，并将其像素值放入
    :param sourceImg: 来源图
    :return targetImg: 保存图
    '''
    L = numpy.asarray(sourceImg.convert('L')).astype('float')

    depth = 10.  # (0-100)
    grad = numpy.gradient(L)  # 取图像灰度的梯度值
    grad_x, grad_y = grad  # 分别取横纵图像梯度值
    grad_x = grad_x * depth / 100.
    grad_y = grad_y * depth / 100.
    A = numpy.sqrt(grad_x ** 2 + grad_y ** 2 + 1.)
    uni_x = grad_x / A
    uni_y = grad_y / A
    uni_z = 1. / A

    el = numpy.pi / 2.2  # 光源的俯视角度，弧度值
    az = numpy.pi / 4  # 光源的方位角度，弧度值
    dx = numpy.cos(el) * numpy.cos(az)  # 光源对x轴的影响
    dy = numpy.cos(el) * numpy.sin(az)  # 光源对y轴的影响
    dz = numpy.sin(el)  # 光源对z轴的影响

    gd = 255 * (dx * uni_x + dy * uni_y + dz * uni_z)  # 光源归一化
    gd = gd.clip(0, 255)  # 避免数据越界，将生成的灰度值裁剪至0-255之间

    # gd = numpy.expand_dims(gd,axis =2)
    # gd = numpy.concatenate((gd,gd,gd),axis = -1)
    #
    # gd = numpy.hstack((arr,gd))
    im = PIL.Image.fromarray(gd.astype('uint8'))  # 重构图像
    im.save(targetImg)  # 保存图像
    return im

def cv_img_resize_by_dir(dir_path, save_dir_path, width, height, suffixs_name=['png']):
    '''
    改变某个文件夹下所有指定后缀文件的大小，并保存到指定文件夹下
    :return bool: 是否成功
    '''
    source_list = zq_file.dir_get_files(dir_path, True, suffix_names=suffixs_name)
    for img_path in source_list:
        img_dir = os.path.dirname(img_path)
        if not os.path.exists(img_dir):
            os.makedirs(img_dir)
        img = PIL.Image.open(img_path)
        try:
            new_img = img.resize((width, height), PIL.Image.BILINEAR)
            new_img.save(os.path.join(save_dir_path, os.path.basename(img_path)))
        except Exception as e:
            print(e)
            return False
    return True

def cv_img_add_text(img:str, outImg:str, text, font_size, text_pos:tuple=(0,0), color='black'):
    '''
    图片添加文字
    '''
    bk_img = cv2.imread(img)
    #设置需要显示的字体
    fontpath = 'font/simsun.ttc'
    font = PIL.ImageFont.truetype(fontpath, font_size)
    img_pil = PIL.Image.fromarray(bk_img)
    draw = PIL.ImageDraw.Draw(img_pil)
    #绘制文字信息
    draw.text(text_pos, text, font = font, fill = color)
    bk_img = np.array(img_pil)

    # cv2.imshow('add_text',bk_img)
    # cv2.waitKey()
    cv2.imwrite(outImg,bk_img)
