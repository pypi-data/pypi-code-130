import torch

MODEL_VERSION = 'model_9'
TILE_SIZE = 256 # size of length of square tile sampled from dsm
LARGE_VAL_IMG_SIZE = 1024 # must be multiple of TILE_SIZE
DATA_TYPE = torch.float32 # data type for height (modify to adjust precision vs memory cost)

gpu = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
cpu = torch.device('cpu')
print(f"gpu is {'' if torch.cuda.is_available() else 'not '}available")