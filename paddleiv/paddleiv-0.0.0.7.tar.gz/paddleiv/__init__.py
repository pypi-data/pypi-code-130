import numpy as np
import imgvision as iv
import paddle
from paddle import nn
import paddle.nn.functional as F
import os
import warnings


class spatial_degradation(nn.Layer):
    # 仅支持单Batch降维
    def __init__(self, sf, blur):
        super(spatial_degradation, self).__init__()
        if blur.sum() > 1:
            blur = blur / blur.sum()
        w = paddle.ParamAttr(initializer=nn.initializer.Assign(paddle.to_tensor(blur, 'float32')))
        self.c = nn.Conv2D(1, 1, 19, sf, weight_attr=w, bias_attr=None)

    def forward(self, x):
        x = x.transpose([1, 0, 2, 3])
        return self.c(x).transpose([1, 0, 2, 3])

def get_mat_train(path,key,srf,inc,patch_size,sf):
    '''

    :param path: 训练样本Mat格式的放置路径
    :param key:  Mat文件的Key
    :param srf:  转换RGB图像的光谱响应函数
    :param inc:  图像重叠间隔，inc=patch_size时不重叠
    :param patch_size: 图像块大小
    :param sf: 超分辨率因子
    :return: 训练样本列表(LR_HSI,HR_RGB,Label)
    '''
    import glob
    import scipy.io as sio
    flist = glob.glob(path+'*.mat')
    print(f'{len(flist)} Images For Training')
    train_set =[]
    for i in range(len(flist)):
        GT = sio.loadmat(flist[i])[key]
        HR_RGB = GT @ srf
        for x in range(0, GT.shape[0] - patch_size, inc):
            for y in range(0, GT.shape[1] - patch_size, inc):
                label = GT[x:x + patch_size, y:y + patch_size]
                LR_HSI = get_LR(label.T, sf).T
                train_set.append([LR_HSI, HR_RGB[x:x + patch_size, y:y + patch_size], label])
    return train_set

def get_SpaDe_Conv(sf, blur_type='motion'):
    blur = iv.get_blur(blur_type)
    return spatial_degradation(sf=sf, blur=blur)


def get_LR(img, sf, blur_type='motion'):
    img = paddle.to_tensor(img, 'float32').T.unsqueeze(0)
    SpaD_conv = get_SpaDe_Conv(sf=sf, blur_type=blur_type)
    return SpaD_conv(img)[0].numpy().T


def update_lr(optimizer, epoch,total_epoch,start_epoch=0):
    lr_l = 1.0 - max(0, epoch + 1 + total_epoch - start_epoch) / float(total_epoch-start_epoch+ 1)
    for Optimizer__ in optimizer:
        Optimizer__.set_lr(Optimizer__.get_lr() * lr_l)


def init_weights(net, init_type='normal', gain=0.02):
    from paddle.nn import initializer as init
    # 调试成功时间：2022年6月16日
    def init_func(m):
        classname = m.__class__.__name__
        if init_type in ['mean_space', 'mean_channel']:
            batchsize, channel, height, weight = list(m.weight.shape)
            if init_type == 'mean_space':
                num = 1 / (height * weight)
            elif init_type == 'mean_channel':
                num = 1 / (channel)
            para_ = paddle.full(m.weight.shape, num)
            para = paddle.create_parameter(shape=m.weight.shape, dtype='float32',
                                           default_initializer=nn.initializer.Assign(
                                               paddle.to_tensor(para_, 'float32')))
            m.weight = para
        else:
            if init_type == 'normal':
                pre_init = init.Normal()
            elif init_type == 'xavier':
                pre_init = init.XavierNormal()
            elif init_type == 'kaiming':
                pre_init = init.KaimingNormal()
            elif init_type == 'orthogonal':
                pre_init = init.Orthogonal(gain=gain)
            else:
                raise NotImplementedError('initialization method [%s] is not implemented' % init_type)
            pre_init(m.weight)
        # if hasattr(m, 'bias') and m.bias is not None:
        #     pre_init2 = init.Constant( 0.0)
        #     pre_init2(m.bias)
        # elif classname.find('BatchNorm2d') != -1:
        #     pre_init = init.Normal()
        #     pre_init2 = init.Constant( 0.0)
        #     pre_init(m.weight)
        #     pre_init2(m.bias)

    print('initialize network with %s' % init_type)
    net.apply(init_func)


class SAM_Loss(nn.Layer):
    def __init__(self):
        super(SAM_Loss, self).__init__()

    def forward(self, output, label):
        ratio = (paddle.sum((output + 1e-8).multiply(label + 1e-8), axis=1)) / (paddle.sqrt(
            paddle.sum((output + 1e-8).multiply(output + 1e-8), axis=1) * paddle.sum(
                (label + 1e-8).multiply(label + 1e-8), axis=1)))
        angle = paddle.acos(ratio.clip(-1, 1))
        return paddle.mean(angle)

class PSNR_Loss(nn.Layer):
    def __init__(self):
        super(PSNR_Loss,self).__init__()
    def forward(self,output,label):
        mse = F.mse_loss(output,label,reduction='none').mean([-2,-1])
        psnr = 10. * paddle.log10(1/(mse.clip(0)))
        return psnr.mean()

