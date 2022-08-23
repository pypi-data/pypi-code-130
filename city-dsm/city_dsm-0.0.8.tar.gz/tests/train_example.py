import torch
import numpy as np
import glob

from city_dsm.components.discriminator import CLSGAN
from city_dsm.components.multiloss import MultiLoss, GANLoss
from city_dsm.components.generator import multitask_model_multi_encoder
from city_dsm.model import Model
from city_dsm.load_data import get_datasets_as_paths_dict

from city_dsm.components.model_config import MODEL_VERSION
from train_config import * # import static variables

# task parameters
tasks = sorted(['gan', 'height', 'segmentation', 'norm'])
logvars = torch.nn.ParameterDict({
    'height': torch.nn.Parameter(torch.Tensor(np.array(0.25))),
    'segmentation': torch.nn.Parameter(torch.Tensor(np.array(0.25))),
    'norm': torch.nn.Parameter(torch.Tensor(np.array(0.25))),
}) # estimator for homoscedatic uncertainty for each loss

# set up model
multi_loss = MultiLoss(tasks, logvars)
generator = multitask_model_multi_encoder(encoder_chs=[1,2])
model = Model(generator, CLSGAN(), multi_loss, GANLoss(), train_dir=TRAIN_DIR, batch_size=BATCH_SIZE)

# load datasets
base_paths = glob.glob('maxar/groups/*')
for path in ['maxar/groups/maxar1', 'maxar/groups/maxar10', 'maxar/groups/maxar0']:
    base_paths.remove(path)
train_datasets = get_datasets_as_paths_dict(base_paths)
val_datasets = get_datasets_as_paths_dict(['maxar/groups/maxar1', 'maxar/groups/maxar10'])

# train model
model.train(train_datasets, val_datasets, epochs=EPOCHS, iters=ITERS, val_iters=VAL_ITERS, run_name=f'{RUN_NAME}')

# save model weights
model.save(f'{MODEL_VERSION}/{RUN_NAME}')
