import cv2
import numpy
from moviepy.editor import *
from natsort import natsorted
from PIL import Image
import os, glob, hashlib, shutil
# import zq_cv_img
from moviepy.editor import CompositeAudioClip, VideoFileClip, AudioFileClip, CompositeVideoClip

def _result_param(status, path, video, obj, msg):
    '''
    常规返回数据类型
    :param status: 状态
    :param path: 路径
    :param video: 视频
    :param obj: 对象
    :param msg: 消息
    :return 
    '''
    return {'status':status, 'path': path, 'video': video, 'obj': obj, 'msg': msg}

def _video_path_handle(video_path, save_path):
    '''
    视频路径处理，重名那种
    :param video_path: 视频地址
    :param save_path: 保存地址
    :return 类型: 描述
    '''
    tempPath = video_path
    if video_path == save_path:
        tempFileName = "tempVideo"
        [dirName,fileName]=os.path.split(video_path)
        fileName = "-y.mp4"
        if dirName == "":
            tempPath = "{}_{}".format(tempFileName,fileName)
        else:
            tempPath = "{}/{}_{}".format(dirName,tempFileName,fileName)
        shutil.copyfile(video_path,tempPath)
    return tempPath, save_path

def cv_video_su_miao(video_path):
    '''
    视频转素描
    :param video_path: 视频路径
    '''
    vc = cv2.VideoCapture(video_path)
    c = 0
    if vc.isOpened():
        rval,frame = vc.read()
        height,width = frame.shape[0],frame.shape[1]
        print(height, width)
    else:
        rval = False
        height,width = 960,1200

    # jpg_list = [os.path.join('Pic_Directory/',i) for i in os.listdir('Pic_Directory') if i.endswith('.jpg')]

    fps = 24 # 视频帧率
    video_path1 = './text.mp4'
    video_writer = cv2.VideoWriter(video_path1,cv2.VideoWriter_fourcc(*'mp4v'),fps,(width*2,height))

    while rval:
        rval,frame = vc.read()# 读取视频帧
        img = convert_jpg(Image.fromarray(frame))
        frame_converted = numpy.array(img)

        # 转化为三通道
        image = numpy.expand_dims(frame_converted,axis = 2)
        result_arr = numpy.concatenate((image,image,image),axis = -1)
        result_arr = numpy.hstack((frame,result_arr))

        video_writer.write(result_arr)
        print('Sucessfully Conveted---------{}'.format(c))
        c = c + 1
        if c >= 60:
            break
    video_writer.release()

def cv_video_subclip(video_path, save_path, start_pos, end_pos, is_relative_end_pos = False):
    '''
    视频截取
    :param video_path: 视频地址
    :return list: 视频列表
    '''
    tempPath, save_path = _video_path_handle(video_path, save_path)
    video = VideoFileClip(video_path)
    if is_relative_end_pos:
        # 剪辑视频，从x秒开始到视频结尾前x秒
        video = video.subclip(start_pos, video.duration-end_pos)
    else:
        # 剪辑视频，截取视频前x秒
        video = video.subclip(start_pos, end_pos)
    video.to_videofile(save_path, fps=25, remove_temp=True)
    return _result_param(True, save_path, video, None, '')

def cv_video_merge_all_video_by_list(video_list, save_path, suffix_name='.mp4'):
    '''
    合成列表所有的视频
    :param video_list: 视频列表
    :param save_path: 保存路径
    '''
    # 定义一个数组
    target_list= []
    # 遍历所有文件
    for file_path in video_list:
        # 如果后缀名为 .mp4
        if os.path.splitext(file_path)[1] == suffix_name:
            # 载入视频
            video = VideoFileClip(file_path)
            # 添加到数组
            target_list.append(video)
    if len(target_list) == 0:
        return _result_param(False, save_path, None, None, '文件列表是空的')
    try:
        # 拼接视频
        final_clip = concatenate_videoclips(target_list)
        # 生成目标视频文件
        final_clip.to_videofile(save_path, fps=25, remove_temp=True)
        return _result_param(True, save_path, final_clip, None, '')
    except BaseException as e:
        return _result_param(False, save_path, None, None, str(e))

def cv_video_merge_all_video_by_dir(dir_path, save_path, suffix_name='.mp4'):
    '''
    合成文件夹下所有的视频
    :param dir_path: 视频文件夹路径
    :param save_path: 保存路径
    :return
    '''
    video_list = []
    # 访问 video 文件夹 (假设视频都放在这里面)
    for root, dirs, files in os.walk(dir_path):
        # 按文件名排序
        # files.sort() # 原 1.mp4, 2.mp4, 10.mp4.  排序后  1.mp4, 10.mp4, 2.mp4.
        files = natsorted(files) # 原 1.mp4, 2.mp4, 10.mp4. 排序后  1.mp4, 2.mp4, 10.mp4.
        # 遍历所有文件
        for file in files:
            # 如果后缀名为 .mp4
            if os.path.splitext(file)[1] == suffix_name:
                # 拼接成完整路径
                filePath = os.path.join(root, file)
                video_list.append(filePath)
    if len(video_list) == 0:
        return _result_param(False, save_path, None, None, '列表为空')
    return cv_video_merge_all_video_by_list(video_list, save_path, suffix_name)

def cv_video_crop(video_path, save_path, x_center, y_center, width, height):
    '''
    视频播放区域裁剪
    :param video_path: 视频路径
    :param save_path: 保存地址
    :param x_center: x中心
    :param y_center: y中心
    :param width: 宽度
    :param height: 高度
    :return 
    '''
    video = VideoFileClip(video_path)
    final_clip = video.crop(x_center=x_center, y_center=y_center, width=width, height=height)
    final_clip.to_videofile(save_path, fps=25, remove_temp=True)
    return _result_param(True, save_path, final_clip, None, '')

def cv_video_resize(video_path, save_path, width, height):
    '''
    改变视频分辨率,可能花屏(视频画质不变)
    :param video_path: 视频路径
    :param save_path: 保存地址
    :param width: 宽度
    :param height: 高度
    :return 
    '''
    video = VideoFileClip(video_path)
    final_clip = video.resize(newsize=(width, height))
    final_clip.to_videofile(save_path, fps=25, remove_temp=True)
    return _result_param(True, save_path, final_clip, None, '')


def cv_video_resize_crop(video_path, save_path, x1=0,x2=0,y1=0,y2=0,width=0,height=0,x_center=0,y_center=0):
    '''
    改变视频分辨率,可能花屏(部分画质)
    https://www.sohu.com/a/383491741_797291
    :param video_path: 视频路径
    :param save_path: 保存地址
    :param x1: 左上角
    :param x2: 左上角
    :param y1: 右下角
    :param y2: 右下角
    :param width: 宽度
    :param height: 高度
    :param x_center: x中心点
    :param y_center: y中心点
    :return 
    '''
    video = VideoFileClip(video_path)
    final_clip = video.crop(x1=x1,x2=x2,y1=y1,y2=y2,width=width,height=height,x_center=x_center,y_center=y_center)
    final_clip.to_videofile(save_path, fps=25, remove_temp=True)
    return _result_param(True, save_path, final_clip, None, '')

def cv_video_rotate(video_path, save_path, ang=0):
    '''
    视频旋转
    :param video_path: 视频路径
    :param save_path: 保存地址
    :param ang: 角度
    :return 
    '''
    video = VideoFileClip(video_path)
    final_clip = video.rotate(ang)
    final_clip.to_videofile(save_path, fps=25, remove_temp=True)
    return _result_param(True, save_path, final_clip, None, '')

def cv_video_images_clip_by_list(pic_list, save_path, fps=25, suffix_name='.jpg'):
    '''
    把图片列表合成视频
    :param pic_list: 图片列表
    :param save_path: 保存路径
    '''
    target_list= []
    for pic_path in pic_list:
        if os.path.splitext(pic_path)[1] == suffix_name:
            # 添加到数组
            target_list.append(pic_path)
    if len(target_list)==0:
        return _result_param(False, save_path, None, None, '列表为空')
    try:
        final_clip = ImageSequenceClip(pic_list, fps=fps)
        final_clip.to_videofile(save_path, fps=fps, remove_temp=True)
    except BaseException as e:
        print("很大可能是图片不一样大，可以调用zq_cv_img.cv_img_resize_by_dir 或者 images_resize_by_list 统一设置图片大小")
        return _result_param(False, save_path, None, None, str(e))
    return _result_param(True, save_path, final_clip, None, '')

def cv_video_images_clip_by_dir(dir_path, save_path, fps=25, suffix_name='.jpg'):
    '''
    把文件夹下所有图片合成视频
    :param dir_path: 文件夹路径
    :param save_path: 保存地址
    :return 
    '''
    pic_list = []
    for root, dirs, files in os.walk(dir_path):
        # 按文件名排序
        # files.sort() # 原 1.mp4, 2.mp4, 10.mp4.  排序后  1.mp4, 10.mp4, 2.mp4.
        files = natsorted(files) # 原 1.mp4, 2.mp4, 10.mp4. 排序后  1.mp4, 2.mp4, 10.mp4.
        # 遍历所有文件
        for file in files:
            # 如果后缀名为 .mp4
            if os.path.splitext(file)[1] == suffix_name:
                # 拼接成完整路径
                filePath = os.path.join(root, file)
                pic_list.append(filePath)
    if len(pic_list) == 0:
        return _result_param(False, save_path, None, None, '列表为空')
    return cv_video_images_clip_by_list(pic_list, save_path, fps, suffix_name)

def cv_video_merge_video_to_one_canvas(video_list, save_path):
    '''
    把两个视频放在一个画面上同时播放(左右)
    :param video_list: 视频列表
    :param save_path: 保存路径
    '''
    video1 = VideoFileClip(video_list[0])
    video2 = VideoFileClip(video_list[1])
    # 注意：.set_position([x1, y1])中的x1，y1为视频左上角的坐标
    target1 = video1.set_position([0, 0])
    target2 = video2.set_position([video1.w, 0])
    final_clip = CompositeVideoClip([target1, target2], size=(video1.w+video2.w, video1.h))
    final_clip.to_videofile(save_path, fps=25, remove_temp=True)
    return _result_param(True, save_path, final_clip, None, '')

def video_merge_video_to_one_canvas_by_pos(video_list, save_path, position):
    '''
    把两个视频放在一个画面上同时播放(自定义位置)
    :param video_list: 视频列表
    :param save_path: 保存路径
    :param position: 位置
    '''
    video1 = VideoFileClip(video_list[0])
    video2 = VideoFileClip(video_list[1])
    # 注意：.set_position([x1, y1])中的x1，y1为视频左上角的坐标
    target1 = video1.set_position([0, 0])
    target2 = video2.set_position(position)
    final_clip = CompositeVideoClip([target1, target2], size=(video1.w+video2.w, video1.h))
    final_clip.to_videofile(save_path, fps=25, remove_temp=True)
    return _result_param(True, save_path, final_clip, None, '')

def cv_video_merge_list_all_video(video_path_list, save_path):
    '''
    视频列表合并为一个视频
    :param video_path_list: 视频路径列表
    :param save_path: 保存地址
    '''
    clips = []
    clip = None
    for video_path in video_path_list:
        try:
            clip = VideoFileClip(video_path)
        except BaseException as e:
            print("cv_video_merge_list_all_video Error " + str(e))
            clip = None
        finally:
            if clip != None:
                clips.append(clip)
    if len(clips) == 0 :
        return _result_param(False, save_path, None, None, '列表为空')
    
    final_clip = concatenate_videoclips(clips)
    # mp4文件默认用libx264编码， 比特率单位bps
    # final_clip.write_videofile(save_path, codec="libx264", bitrate="10000000") 
    final_clip.to_videofile(save_path, fps=25, remove_temp=True)
    return _result_param(True, save_path, final_clip, None, '')

def cv_video_change_md5(video_path, save_path):
    '''
    改变视频MD5，路径需要带后缀 VideoFileClipPath
    :param video_path: 视频地址
    :param save_path: 保存地址
    '''
    tempPath, save_path = _video_path_handle(video_path, save_path)
    return cv_video_merge_list_all_video([tempPath], save_path)

def cv_video_add_log(video_path, save_path, logoPngPath = None, logoTextStr = None, color='white', align='center', fontsize = 25, left=0, top=0, right=0, bottom=0, opacity=0, pos=('center','center'), fontPath=None):
    '''
    视频添加LOG  VideoClipAddLogoPath
    '''
    tempPath, save_path = _video_path_handle(video_path, save_path)
    if logoPngPath == None and logoTextStr == None:
        return _result_param(False, save_path, None, None, '没有设置水印')

    clipList = []        
    video = VideoFileClip(tempPath)
    clipList.append(video)
    logoPngClip = None
    logoTextClip = None
    if logoPngPath != None:
        logoPngClip = (ImageClip(logoPngPath)
                .set_duration(video.duration)  # 水印持续时间
                .resize(height=50)  # 水印的高度，会等比缩放
                .margin(left=left, top=top, right=right, bottom=bottom, opacity = opacity)# 水印边距和透明度
                .set_pos(pos))  # 水印的位置
        clipList.append(logoPngClip)

    if logoTextStr != None:
        FONT_URL = fontPath or r'C:/Windows/Fonts/simsun.ttc'  #r'C:\Windows\Fonts\simhei.ttf'    #C:\Windows\Fonts\STXINGKA.TTF'
        if not os.path.exists(FONT_URL):
            print("字体文件不存在 %s"%FONT_URL)
            return False
        logoTextClip = (TextClip(txt=logoTextStr, color=color, size=(640, 480), method='caption',
                align=align, fontsize=fontsize, font=FONT_URL)
                .set_duration(video.duration)
                .margin(left=left, top=top, right=right, bottom=bottom, opacity = opacity)
                .set_pos(pos))  # 水印的位置
        clipList.append(logoTextClip)

    if len(clipList) == 0:
        return _result_param(False, save_path, None, None, '列表为空')
    final_clip = CompositeVideoClip(clipList)
    # mp4文件默认用libx264编码， 比特率单位bps
    # final_clip.write_videofile(save_path, codec="libx264", bitrate="10000000") 
    final_clip.to_videofile(save_path, fps=25, remove_temp=True)
    return _result_param(True, save_path, final_clip, None, '')

def cv_video_add_cover(pic_list, video_path, save_path, cover_video_path=None, fps=25, suffix_name='.jpg'):
    '''
    视频添加封面
    '''
    video = VideoFileClip(video_path)
    if not cover_video_path:
        cover_video_path = save_path
    for item in pic_list:
        img = Image.open(item)
        if video.size != list(img.size):
            try:
                new_img = img.resize((video.w, video.h), Image.BILINEAR)
                new_img.save(item)
            except Exception as e:
                print(e)
        
    result = cv_video_images_clip_by_list(pic_list, cover_video_path, fps, suffix_name)
    if result and result['status']:
        return cv_video_merge_all_video_by_list([cover_video_path, video_path], save_path)
    return _result_param(False, save_path, None, result, result['msg'])

def cv_video_add_cover_by_num(pic, video_path, save_path, cover_video_path=None, picNum=25, fps=25, suffix_name='.jpg'):
    '''
    视频添加封面
    '''
    picList = []
    for item in range(0, picNum):
        picList.append(pic)
    else:
        picList.append(pic)
    return cv_video_add_cover(picList, video_path, save_path, cover_video_path, fps, suffix_name)

def cv_video_get_audio(video_path, save_audio_path):
    '''
    提取视频中的音频
    '''
    video = VideoFileClip(video_path)
    audio = video.audio
    audio.write_audiofile(save_audio_path)
    return _result_param(True, save_audio_path, video, audio, '')

def cv_video_add_audio_by_video(video_path_source, video_path_target, out_video_path):
    '''
    为视频添加另一个视频的音频  source 声音添加到 target
    '''
    video_source = VideoFileClip(video_path_source)
    video_target = VideoFileClip(video_path_target)
    audio = video_source.audio
    videoclip = video_target.set_audio(audio)
    videoclip.write_videofile(out_video_path, audio_codec="aac")
    return _result_param(True, out_video_path, videoclip, None, '')

def cv_video_add_audio_by_audio(video_path, audio_path, out_video_path):
    '''
    为视频添加的音频
    '''
    video = VideoFileClip(video_path)
    audio = AudioFileClip(audio_path).subclip(0, video.duration)
    videoclip = video.set_audio(audio)
    videoclip.write_videofile(out_video_path, audio_codec="aac")
    return _result_param(True, out_video_path, videoclip, None, '')

def cv_video_imgs_to_video(img_list, output_video_file, frame_rate):
    '''
    将图片列表组合成视频
    '''
    # 拿一张图片确认宽高
    img0 = cv2.imread(img_list[0])
    # print(img0)
    height, width, layers = img0.shape
    # 视频保存初始化 VideoWriter
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    videowriter = cv2.VideoWriter(output_video_file, fourcc, frame_rate, (width, height))
    # 核心，保存的东西
    for img_path in img_list:
        img = cv2.imread(img_path)
        videowriter.write(img)
    videowriter.release()
    cv2.destroyAllWindows()
    print('Success save %s!' % output_video_file)

def cv_video_add_audio(video_path, audio_path, out_video_path):
    '''
    为视频添加音频
    '''
    video = VideoFileClip(video_path)
    audio = AudioFileClip(audio_path)
    videos = video.set_audio(audio) #音频文件
    videos.write_videofile(out_video_path,  audio_codec='aac') #保存合成视频，注意加上参数audio_codec='aac'，否则音频无声音
    videos.close()

def cv_video_split_clip(video_path, out_video_path, sub:list):
    '''
    视频分割片段
    '''
    video = VideoFileClip(video_path).subclip(sub[0], sub[1])
    video.write_videofile(out_video_path,  audio_codec='aac') #保存合成视频，注意加上参数audio_codec='aac'，否则音频无声音
    video.close()

def cv_video_to_image(video_path, out_dir, num = -1):
    '''
    将视频分割为图片
    '''
    vid_cap = cv2.VideoCapture(video_path)    #传入视频的路径
    success, image = vid_cap.read()
    count = 0
    while success:
        vid_cap.set(cv2.CAP_PROP_POS_MSEC, 0.5 * 1000 * count)   #截取图片的方法  此处是0.5秒截取一个  可以改变参数设置截取间隔的时间
        if not os.path.exists(out_dir):   #创建每一个视频存储图片对应的文件夹
            os.makedirs(out_dir)
        cv2.imwrite(out_dir+'/' + str(count) + '.jpg', image)       #存储图片的地址 以及对图片的命名
        success, image = vid_cap.read()
        count += 1
        if num != -1 and count >= num:
            break
    vid_cap.release()

def cv_video_merage_video(source_video_path, target_video_path, out_video_path, target_pos=('right', 'bottom'), target_ratio=(1/3, 1/3), target_ratio_fixed:tuple=None,
        target_margin=1, target_margin_color=(255, 255, 255), target_margin_space=(1,1,1,1,0), target_audio=False, fps=24, codec='libx264'):
    '''
    视频合并视频
    '''
    source = VideoFileClip(source_video_path, audio=True)
    w, h = source.size
    if target_ratio_fixed:
        target_ratio = (target_ratio_fixed[0]/w, target_ratio_fixed[1]/h)
    target = (VideoFileClip(target_video_path, audio=target_audio)
        .resize((w * target_ratio[0], h * target_ratio[1]))  # one third of the total screen
        .margin(target_margin, color=target_margin_color)  # white margin
        .margin(left=target_margin_space[0],bottom=target_margin_space[1], right=target_margin_space[2], top=target_margin_space[3], opacity=target_margin_space[4])  # transparent
        .set_pos(target_pos))
    video = CompositeVideoClip([source, target])
    video.write_videofile(out_video_path, fps=fps, codec=codec)
    video.close()
