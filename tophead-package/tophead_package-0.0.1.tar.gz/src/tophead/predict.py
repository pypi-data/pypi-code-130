import time 
import argparse
import torch
from PIL import Image
import torchvision.transforms.functional as TF
import torchvision.transforms as transforms
from torchvision.utils import save_image
import cv2
import numpy as np
import os

from pathlib import Path

import sys
# TODO
from models import *

SRC_DIR = Path(__file__).resolve().parent.parent


def build_model(model_version, quantize, model_path, device) :
    if model_version == 1:
        if quantize:
            net = quantized_modelv1(pretrained=True, device=device).to(device)
        else:
            net = modelv1(pretrained=True, device=device).to(device)
    elif model_version == 2:
        if quantize:
            net = quantized_modelv2(pretrained=True, device=device).to(device)
        else:
            net = modelv2(pretrained=True, device=device).to(device)
    else:
        raise Exception('[!] Unexpected model version')

    net = load_model(net, model_path, device)
    return net


def load_model(net, model_path, device):
    if model_path:
        print(f'[*] Load Model from {model_path}')
        net.load_state_dict(torch.load(model_path, map_location=device)['state_dict'])

    return net

def gamma_correction(image, white):

    if white: 
        return TF.adjust_gamma(image, 1.1)

    transform = transforms.ToTensor()
    # convert the image to PyTorch Tensor
    imgTensor = transform(image)

    r, g, b = torch.mean(imgTensor, dim=[1, 2])

    
    avg = (r + g + b ) /3 
    # print("AVERAGE VALUE: ", avg)
    if avg < 0.45:
        image = TF.adjust_gamma(image, 0.5)
        print("UNDER EXPOSED, INCREASING LIGHT")
        return image
    elif avg >=0.55: 
        image = TF.adjust_gamma(image, 1.1)
        print("OVER EXPOSED, DECREASING LIGHT")
        return image
    else: 
        print("NORMAL, NO GAMMA")
        return image

def saveMultipleImage():
    '''args here'''
    # save_image(torch.cat([image, result, mask]), os.path.join(self.sample_dir, f"{step}.jpg"))
    # save_image(torch.cat([(image * result), image, result, mask]), os.path.join(self.sample_dir, f"{step}.jpg"))
    # save_image(torch.cat([resized]), os.path.join(args.result_path, "0.jpg"))

def calculate_hair_ratio(bald_patch, mask, start_time):
 
    whitePixel = 0
    for i in range(0,bald_patch.shape[0]):
        for j in range(0,bald_patch.shape[1]):
            if bald_patch[i,j] > 0: 
                # print(grayImage[i,j])
                whitePixel += 1
    hairArea = 0
    for i in range(0,mask.shape[0]):
        for j in range(0,mask.shape[1]):
            if mask[i,j] > 0: 
                # print(grayImage[i,j])
                hairArea += 1
    proportion = whitePixel / (hairArea) * 100
    print(f'{__name__} -- ratio: {proportion:.2f}%')
    print(f'{__name__} -- calculation: {time.time() - start_time}')
    return 100 - proportion # since we want black / overall

def plot_image(resized, bald_patch, mask):
    cv2.imshow("Image",resized)
    cv2.imshow("bald patch & mask", np.hstack([bald_patch, mask]))
    cv2.waitKey(0)
    cv2.destroyAllWindows() 

def preprocess(resized,image, device, net, white=False):
    # convert original image into gray scale
    resized = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)

    if white:
        image = gamma_correction(image, True)
    else:
        image = gamma_correction(image, False)

    # resize image to 224x224 and image normalization around mean
    image = TF.to_tensor(image).to(device)
    image = TF.resize(image, [224, 224])
    image = TF.normalize(image, [0.5, 0.5, 0.5], [0.5, 0.5, 0.5])
    # print('IMAGE TIMES BINARY MASK : ', image.shape)
    # print('IMAGE TIMES BINARY MASK : ', image.unsqueeze(0).shape)
    start = time.time()
    mask = net(image.unsqueeze(0))
    print(f'inference time: {time.time() - start}')
    mask = mask.argmax(dim=1)
    mask = TF.resize(mask, [224, 224]).squeeze()
    print(f'IMAGE shape: {image.shape} vs BINARY MASK : {mask.shape} ')

    # generate mask
    bald_patch = (image * mask)

    bald_patch =  bald_patch.permute(1, 2, 0).cpu().detach().numpy()
    mask =  mask.cpu().detach().numpy()
    bald_patch = cv2.cvtColor(bald_patch, cv2.COLOR_BGR2GRAY)

    return resized, image, mask, bald_patch

def predict(filename):

    # device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    device = "cpu"
    # TODO
    # net = build_model(2, False, r"C:\Users\ferdy\Documents\Project5\tophead\checkpoints\best.pth", device).to(device)
    net = build_model(2, False, SRC_DIR / "checkpoints/best.pth", device).to(device)
    start = time.time()

    image = Image.open(filename)

    Original_resized = cv2.resize(cv2.imread(filename), (224,224), interpolation = cv2.INTER_AREA)
    
    resized, _ , mask, bald_patch = preprocess(Original_resized, image, device, net, False)

    ratio = calculate_hair_ratio(bald_patch, mask, start)

    if ratio <  30: 
        resized, image, mask, bald_patch = preprocess(Original_resized, image, device, net, True)
        ratio = calculate_hair_ratio(bald_patch, mask,start)

    '''
    about to change, depend on what the caller expect, currently its plotting the result to windows using opencv
    '''
    return ratio # in percentage
    # plot_image(resized, bald_patch, mask)


'''
this is used for running python predict.py directly
'''
def predict_internal(args, device, net):
    start = time.time()

    image = Image.open(args.image_path)

    Original_resized = cv2.resize(cv2.imread(args.image_path), (224,224), interpolation = cv2.INTER_AREA)
    
    resized, _ , mask, bald_patch = preprocess(Original_resized, image, device, net, False)
    # ratio = calculate_hair_ratio(bald_patch, mask, start)

    # if ratio > 70: 
    #     resized, image, mask, bald_patch = preprocess(Original_resized, image, device, net, True)
    #     ratio = calculate_hair_ratio(bald_patch, mask,start)
    print(mask.shape)
    plot_image(resized, bald_patch, mask)

def get_coordinate(image_path, x):
    import os
    import head_segmentation.segmentation_pipeline as seg_pipeline
    import head_segmentation.visualization as vis

    os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

    image = Image.open(image_path)
    
    Original_resized = cv2.resize(cv2.imread(image_path), (224,224), interpolation = cv2.INTER_AREA)
    segmentation_pipeline = seg_pipeline.HumanHeadSegmentationPipeline()
    mask = segmentation_pipeline.predict(Original_resized)

    # if ratio > 70: 
    #     resized, image, mask, bald_patch = preprocess(Original_resized, image, device, net, True)
    #     ratio = calculate_hair_ratio(bald_patch, mask,start)

    for row in range(mask.shape[0]):
        for col in range(mask.shape[1]):
            if mask[row][col] == 1:
                # print("HOY GRALI: ",row, col)
                cv2.circle(Original_resized, (x, row), 5, (0, 255, 0), -1)
                import matplotlib.pyplot as plt
                # TODO IF WANT TO SHOW VIZ
                # cv2.imshow('original image', Original_resized)
                # cv2.waitKey(0)
                # cv2.destroyAllWindows()
                # plt.imshow(mask, cmap="gray")
                # plt.show()
                # cv2.imshow("Image",Original_resized)
                # cv2.waitKey(0)
                # cv2.destroyAllWindows() 
                # plot_image(Original_resized, bald_patch, mask)
                return row

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument('--model_version', type=int, default=2, help='MobileHairNet version')
    parser.add_argument('--quantize', nargs='?', const=True, default=False, help='load and train quantizable model')
    parser.add_argument('--model_path', type=str, default=None)
    parser.add_argument('-i', '--image_path', type=str, default=None, help='path of the image')
    parser.add_argument('-o', '--result_path', type=str, default=None, help='path of the image')

    args = parser.parse_args()

    device = torch.device("cuda:0" if torch.cuda.is_available() and not args.quantize else "cpu")
    net = build_model(args.model_version, args.quantize, args.model_path, device).to(device)

    predict_internal(args, device, net)

