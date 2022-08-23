import rasterio
import os
import numpy as np

def get_datasets_as_paths_dict(base_paths):
    # have to specify channels in optical image - can't train RGB on mono-channel optic encoder for example

    datasets = {}
    for base_path in base_paths:
        with rasterio.open(os.path.join(base_path, 'valid_pixel_mask.tiff')) as f:
            valid_pixel_mask = f.read(1).astype('uint8')
        with rasterio.open(os.path.join(base_path, 'built_up_areas_morph.tiff')) as f:
            built_up_areas_morph = f.read(1).astype('uint8')
        with rasterio.open(os.path.join(base_path, 'sampling_weights.tiff')) as f:
            sampling_weights = f.read(1)
        valid_px = np.count_nonzero(valid_pixel_mask)
        valid_built_up_mask = built_up_areas_morph.astype('bool') & valid_pixel_mask
        valid_built_up_px = np.count_nonzero(valid_built_up_mask)
        ds_weight = 0.8 * valid_built_up_px + 0.2 * (valid_px - valid_built_up_px)
        
        # build datasets (augmented)
        datasets[base_path] = {
            'optic': os.path.join(base_path, 'norm-optic.tiff'),
            'input': os.path.join(base_path, 'ground-norm-dsm.tiff'),
            'truth': os.path.join(base_path, 'truth-dsm.tiff'),
            'truth_inter': os.path.join(base_path, 'truth-inter-dsm.tiff'),
            'seg_truth': os.path.join(base_path, 'seg-truth-crop.tiff'),
            'valid_pixel_mask': valid_pixel_mask,
            'sampling_weights': sampling_weights,
            'ds_weight': ds_weight
        }
    return datasets
