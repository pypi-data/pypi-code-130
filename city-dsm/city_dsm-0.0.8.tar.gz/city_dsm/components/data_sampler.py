import torch
import numpy as np
import rasterio
import cv2 as cv

from .model_config import LARGE_VAL_IMG_SIZE

def choose_pixel_centers(dataset, num_pc=5, large_img=False):
    valid_pixel_mask = dataset['valid_pixel_mask']
    sampling_weights = dataset['sampling_weights']
    
    # we need to reduce range of vpc when sampling for a large image
    # TODO: move this step to data pre-processing
    if large_img: 
        valid_pixel_mask = cv.erode(
            valid_pixel_mask.astype('uint8'), 
            np.ones((LARGE_VAL_IMG_SIZE+1, LARGE_VAL_IMG_SIZE+1))
        )
        sampling_weights = sampling_weights & valid_pixel_mask
        sampling_weights = sampling_weights / np.nansum(sampling_weights)
    valid_pixel_centers = np.moveaxis(np.array(np.where(valid_pixel_mask)), 0, 1)
    sampling_weights_1d = sampling_weights[valid_pixel_mask.astype('bool')]
    pixel_centers = valid_pixel_centers[
        np.random.choice(len(valid_pixel_centers), size=(num_pc), p=sampling_weights_1d)
    ]
    return pixel_centers

def data_sampler(datasets, ds_name, pixel_centers, TILE_SIZE=256):
    # set up inputs and truth
    def get_input_ch(ds):
        return {
            'dsm': ds['input'],
            'optic': ds['optic']
        }
    def get_tasks_truth(ds):
        return {
#                 'height': ds['truth'] + ds['ground'] - ds['input'][0], # predict residual
            'height': ds['truth'], # predict real height (may be ground normalized, e.g. in case of maxar)
            'segmentation': ds['seg_truth'],
            'norm': ds['truth'],
            'gan': ds['truth_inter']
        }

    aug_methods = {
        'rot0': lambda x: x,
        'rot90': lambda x: np.rot90(x, k=1, axes=(-2, -1)),
        'rot180': lambda x: np.rot90(x, k=2, axes=(-2, -1)),
        'rot270': lambda x: np.rot90(x, k=3, axes=(-2, -1)),
    } # add flipping?
    aug = np.random.choice(list(aug_methods.keys())) # randomly augment data for each sample
    aug = aug_methods[aug]

    ds = datasets[ds_name]
    data_tiles = {}
    for k in ['input', 'optic', 'truth', 'truth_inter', 'seg_truth']:
        if k not in data_tiles:
            data_tiles[k] = []
        for pixel_center in pixel_centers:
            window=rasterio.windows.Window(
                pixel_center[1]-round(TILE_SIZE/2), # x coords
                pixel_center[0]-round(TILE_SIZE/2), # y coords
                TILE_SIZE, TILE_SIZE 
            )
            with rasterio.open(ds[k]) as f:
                tile = f.read(window=window)
                tile = aug(tile)
            data_tiles[k].append(tile)
        data_tiles[k] = torch.Tensor(np.stack(data_tiles[k]))

    input_ch = get_input_ch(data_tiles)
    batch_inputs = torch.Tensor(torch.cat([
        input_ch[k] for k in sorted(input_ch.keys())
    ], dim=1))
    batch_tile_truths = get_tasks_truth(data_tiles)

    return batch_inputs, batch_tile_truths

# simple cropping of a raster
# def data_cropper(raster, pixel_centers):
#     raster_tiles = torch.unsqueeze(torch.Tensor(np.array([
#         raster[
#             pixel_center[0]-round(TILE_SIZE/2): pixel_center[0]+round(TILE_SIZE/2),
#             pixel_center[1]-round(TILE_SIZE/2): pixel_center[1]+round(TILE_SIZE/2)
#         ] for pixel_center in pixel_centers
#     ])), 1)
#     return raster_tiles

def normalize_images(images): # to 0, 1 range
    low = torch.nanquantile(images, 0.05)
    high = torch.nanquantile(images, 0.95)
    im_range = high - low
    images = (images - low) / im_range
    images = torch.clamp(images, 0, 1)
    return images
