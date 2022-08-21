import pytesseract, os, jieba, PIL

def cv_img_contain_text_points(text, img, isRemoveOutBox=True, isShowLog=False):
    '''
    instruction:
    基于tesseract识别出文字(不同语言有不同的文字识别库，此处用的是中文库 chi_sim，主要用于识别中文 )，
    返回文字在屏幕上的坐标点列表。

    usage:
    text = '带查找文字'
    img = '图片地址.png'
    isRemoveOutBox = '结束是否移除数据文件'

    return 匹配到的所有的列表(第一个列表相识度最高)
    '''
    outSuffix = '.box'
    outName='out'
    outFullName='%s%s'%(outName, outSuffix)

    if os.path.exists(img):
        strValue = pytesseract.image_to_string(img, lang='chi_sim')
        if isShowLog:
            print(strValue)
        os.system('tesseract %s %s -l chi_sim makebox'%(img, outName))
        print('输出坐标文件 : %s'%outFullName)
    else:
        print('%s is not exists'%img)

    pos_list = []
    if os.path.exists(outFullName):
        with open(outFullName,'r', encoding='UTF-8') as f:
            for line in f:
                if line.split()[0] in text:
                    pos_list.append(line.split())

    if os.path.exists(outFullName) and isRemoveOutBox:
        os.remove(outFullName)

    return pos_list

def img_contain_text_click_pos(text, img, isWin, isHorizontal=True, isRemoveImg=True, isRemoveOutBox=True, isShowLog=False):
    '''
    点击文字在图片中的位置
    基于tesseract识别出文字(不同语言有不同的文字识别库，此处用的是中文库 chi_sim，主要用于识别中文 )，
    return {state:是否点击成功,msg:消息提示}

    usage:
    text = '带查找文字'
    img = '图片地址.png'
    isWin: 电脑是分辨率，手机需要换算分辨率和屏幕大小
    isRemoveImg = '结束是否移除Img'
    isRemoveOutBox = '结束是否移除数据文件'
    '''

    resultData = {'state': False, 'msg':''}
    pos_list = cv_img_contain_text_points(text, img, isRemoveOutBox)

    if not pos_list or len(pos_list) == 0:
        resultData['msg'] = '没有匹配到对应字'
    else:
        if isShowLog:
            print(pos_list)
        xCenterPointList, yCenterPointList, xCenterPointSum, yCenterPointSum, x, y = [], [], 0, 0, 0, 0
        for item in pos_list[:]:
            tempXCenterPoint = (int(item[1]) + int(item[3]))/2
            xCenterPointList.append(tempXCenterPoint)
            xCenterPointSum = xCenterPointSum + tempXCenterPoint

            tempYCenterPoint = (int(item[2]) + int(item[4]))/2
            yCenterPointList.append(tempYCenterPoint)
            yCenterPointSum = yCenterPointSum + tempYCenterPoint

        x = int(xCenterPointSum/2)
        imgInstance = PIL.Image.open(img)
        height = imgInstance.size[1]    # 获取屏幕高度

        if isHorizontal:
            # 水平，一般认为三个字的中间点Y轴是一样的，所以取一个字的Y轴就可以了
            y = int((height - int(pos_list[0][2])) + (height - int(pos_list[0][4])))/2
        else:
            print('纵向文字的高计算有问题，记录记录，后面修')
            y = int(yCenterPointSum/2)

        if isShowLog:
            print('X--> %s   Y--> %s'%(x, y))
        resultData['state'] = True
    if  os.path.exists(img) and isRemoveImg:
        os.remove(img)
    return resultData

def img_contain_text(img, text, lang='chi_sim', isShowContent=False):
    '''
    图片是否包含文字
    return bool
    '''
    resultStr = pytesseract.image_to_string(img, lang=lang)
    resultStr = resultStr.replace('\n', '').replace(' ', '')
    if isShowContent:
        print(resultStr)
    if type(text) == type([]):
        for item in text[:]:
            if item in resultStr:
                return True
    else:
        if text in resultStr:
            return True
    return False

def img_contain_text_jieba(self, img, text, lang='chi_sim', confidence=None, cut_all=False, isShowContent=False):
    '''
    图片是否包含某一句话（结巴）
    confidence 匹配度
    return 【传入匹配度，返回bool】【不传入匹配度，返回匹配度（0-1）】
    '''
    seg_list = jieba.cut(text)
    if not seg_list:
        return 0
    resultStr = pytesseract.image_to_string(img, lang=lang)
    resultStr = resultStr.replace('\n', '').replace(' ', '')
    if isShowContent:
        print(resultStr)
    used, sum = 1, 1
    for item in seg_list:
        if item[0] in resultStr:
            used += 1
        sum += 1
    confidenceT = used/sum
    if confidence:
        return confidenceT >= confidence
    else:
        return confidenceT