import torch
import os

def get_device():
    return torch.device('cuda' if torch.cuda.is_available() else 'cpu')

def disable_cuda():
    os.environ["CUDA_VISIBLE_DEVICES"]="-1"
    if torch.cuda.is_available():
        print("Disable CUDA fail!")
    else:
        print("Disable CUDA success!")