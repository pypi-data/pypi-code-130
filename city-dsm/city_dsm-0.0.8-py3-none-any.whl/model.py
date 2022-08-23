import torch
import numpy as np
import os
import time
from torch.utils.tensorboard import SummaryWriter
from .components.data_sampler import normalize_images, data_sampler, choose_pixel_centers
from .components.model_config import * # import static variables

class Model():
    def __init__(self, G, D, G_crit, D_crit, train_dir, batch_size, balance_weights=True):
        self.G = G.to(gpu)
        self.D = D.to(gpu)
        self.G_crit = G_crit.to(gpu)
        self.D_crit = D_crit.to(gpu)
        if balance_weights:
            G_params = list(self.G.parameters()) + list(self.G_crit.logvars.parameters())
        else:
            G_params = list(self.G.parameters())
        self.G_opt = torch.optim.Adam(G_params, lr=0.0005, betas=(0.9, 0.999))
        self.D_opt = torch.optim.Adam(self.D.parameters(), lr=0.0005, betas=(0.9, 0.999))
        self.loss_history = [] # by epoch
        self.loss_history_ = [] # by iter
        self.wb_history = []
        self.global_iter = 0
        self.batch_size = batch_size
        self.train_dir = train_dir

        log_path = os.path.join(self.train_dir, f'{MODEL_VERSION}', 'log')
        if not os.path.isdir(log_path):
            os.makedirs(log_path)
        self.writer = SummaryWriter(log_path)
        
    def optimize_G(self, tasks_out, tile_truths, D_prediction):
        self.G_opt.zero_grad()
        G_loss = self.G_crit(tasks_out, tile_truths, D_prediction.detach())
        G_loss['total'].backward()

        # break if nans occur (immediately stop errors before weights become undefined)
        for k, v in G_loss.items():
            if torch.isnan(v):
                print(tasks_out['height'].shape, tile_truths['height'].shape)
                print(torch.count_nonzero(torch.isnan(tasks_out['height'])))
                print(G_loss)
                raise Exception('nan loss')

        self.G_opt.step()
        self.loss_history_.append({k: v.detach() for k, v in G_loss.items()})
        return G_loss
    
    def optimize_D(self, D_predict_real, D_predict_fake):
        self.D_opt.zero_grad()
        D_loss_real = self.D_crit(D_predict_real, is_ground_truth=1.0)
        D_loss_fake = self.D_crit(D_predict_fake, is_ground_truth=0.0)
        D_loss = (D_loss_fake + D_loss_real) * 0.5
        D_loss.backward()
        self.D_opt.step()
        return D_loss
    
    def predict_one(self, datasets, ds_weights): # predict one batch
        # select an AOI by area weight
        ds_name = np.random.choice(sorted(datasets.keys()), p=ds_weights)

        # sample tiles from one AOI
        pixel_centers = choose_pixel_centers(datasets[ds_name], self.batch_size)
        try:
            inputs, tile_truths = data_sampler(
                datasets,
                ds_name,
                pixel_centers,
                batch_size=self.batch_size
            )
        except:
            print('ds_name: ', ds_name)
            raise
        
        # if only 1 sample in batch, skip it (otherwise batchnorm breaks)
        # TODO: ensure no 1 sample batches at end of ds
        assert inputs.shape[0] > 1, 'must have more than one sample in batch'

        # move data to gpu
        inputs = inputs.type(DATA_TYPE).to(gpu)
        for k in tile_truths.keys():
            tile_truths[k] = tile_truths[k].type(DATA_TYPE).to(gpu)
#         surface_tile = surface_tile.type(DATA_TYPE).to(gpu)

        # make predictions
        tasks_out = self.G(inputs)
        tasks_out['norm'] = tasks_out['height'] # true surface
        D_prediction = self.D(inputs[:,0:1], tasks_out['height'])
        
        return inputs, tasks_out, tile_truths, D_prediction
    
    def train(self, train_datasets, val_datasets, epochs, iters, val_iters, run_name='test'):
        # balance datasets by eligible sample points
        log_name = f'{MODEL_VERSION}/{run_name}'
        total_ds_weights = sum([
            v['ds_weight'] for v in train_datasets.values()
        ])
        ds_weights = [
            train_datasets[k]['ds_weight'] / total_ds_weights for k in sorted(train_datasets.keys())
        ] # dataset sample weights
        total_val_ds_weights = sum([
            v['ds_weight'] for v in val_datasets.values()
        ])
        val_ds_weights = [
            val_datasets[k]['ds_weight'] / total_val_ds_weights for k in sorted(val_datasets.keys())
        ] # dataset sample weights
        
        # training loop (dynamic data loading)
        start_time = time.time()
        self.G.train()
        self.D.train()
        torch.autograd.set_detect_anomaly(False)
        for epoch in range(int(self.global_iter/iters), epochs):  # loop over the dataset multiple times
            # loop over training iters
            for i in range(self.global_iter%iters, iters):
                # predict one batch
                inputs, tasks_out, tile_truths, D_prediction = self.predict_one(train_datasets, ds_weights)
                
                if i % 100 == 0: # log images each 100 iters
                    self.log_images(log_name, inputs, tasks_out, tile_truths)
                
                # backward and optimize (generator loss)
                G_loss = self.optimize_G(tasks_out, tile_truths, D_prediction)

                # backward and optimze (discriminator loss)
                D_predict_real = self.D(inputs[:,0:1], tile_truths['gan'])
                D_predict_fake = self.D(inputs[:,0:1], tasks_out['height'].detach())
                self.optimize_D(D_predict_real, D_predict_fake)
                
                # log generator log variance, loss weights, and losses
                self.log_scalars(log_name, epoch, i, self.G_crit.logvars.copy(), G_loss, iters)
                
                self.global_iter += 1

            # do validation
            with torch.no_grad():
                for i in range(val_iters):
                    self.G.eval()
                    self.D.eval()
                    self.G_crit.eval()
                    inputs, tasks_out, tile_truths, D_prediction = self.predict_one(val_datasets, val_ds_weights)
                    G_loss = self.G_crit(tasks_out, tile_truths, D_prediction.detach())

                    # log val loss
                    logvars = self.G_crit.logvars.copy()
                    logvars['weight_reg'] = sum([x.item() for x in logvars.values()])/2
                    losses = G_loss.copy()
                    losses['multi_loss'] = losses['total'] - logvars['weight_reg']
                    losses = {'val_'+k: v for k, v in losses.items()}
                    for k in losses:
                        self.writer.add_scalars(f'val_loss/{k}', {run_name: losses[k]}, (epoch)*iters+i)
                    self.log_images(log_name+'_val', inputs, tasks_out, tile_truths)

                    self.G.train()
                    self.D.train()
                    self.G_crit.train()
            
            # save model every 10 epochs
            if epoch % 10 == 0:
                self.save(f'{MODEL_VERSION}/{run_name}/checkpoints/iter_{self.global_iter}')
                self.validate_large_image(log_name, val_datasets, val_ds_weights)
            
            # track weight balance and loss
            self.wb_history.append([x.item() for x in self.G_crit.logvars.values()])
            cum_loss = {k: 0 for k in self.loss_history_[0].keys()}
            for x in self.loss_history_:
                for k, v in x.items():
                    cum_loss[k] += v
            avg_loss = {k: v/len(self.loss_history_) for k, v in cum_loss.items()}
            self.loss_history.append(avg_loss)
            self.loss_history_ = []

            # print statistics
            print(f"[{epoch + 1}, {i + 1:5d}] loss: {self.loss_history[-1]['total']:.3f}")
            print(f"           losses  : {[v.item() for k, v in self.loss_history[-1].items() if k != 'total']}")
            print(f'           logvars: {[x.item() for x in self.G_crit.logvars.parameters()]}')
        
        self.writer.close()
        end_time = time.time()
        print(f'time: {end_time-start_time}')
    
    def log_images(self, run_name, inputs, tasks_out, tile_truths):
        # track image
        images = [
            inputs[:,1:2].to(cpu), inputs[:,0:1].to(cpu), 
            tasks_out['height'].to(cpu), tile_truths['height'].to(cpu), 
            tasks_out['segmentation'].argmax(dim=1, keepdims=True).to(cpu), tile_truths['segmentation'].to(cpu)
        ]
        images = torch.concat([
            normalize_images(image.detach().type(torch.float32)) for image in images
        ], dim=1) # optic, input, output, truth, seg_out, seg_truth
        images = torch.unsqueeze(images, dim=2)
        
        i = 0
        for image in images:
            self.writer.add_images(f'{run_name}_img/iter_{self.global_iter}_sample_{i}', 
                                  image,
                                  global_step=self.global_iter,
                                  dataformats='NCHW')
            i += 1
    
    def log_scalars(self, run_name, epoch, i, logvars, G_loss, max_iters):
        logvars['weight_reg'] = sum([x.item() for x in logvars.values()])/2
        weights = {k: np.exp(-v) for k, v in logvars.items() if k != 'weight_reg'}
        losses = G_loss.copy()
        losses['multi_loss'] = losses['total'] - logvars['weight_reg']

        for k in losses:
            self.writer.add_scalars(f'loss/{k}', {run_name: losses[k]}, (epoch)*max_iters+i)
        for k in weights:
            self.writer.add_scalars(f'weight/{k}', {run_name: weights[k]}, (epoch)*max_iters+i)
        for k in logvars:
            self.writer.add_scalars(f'logvar/{k}', {run_name: logvars[k]}, (epoch)*max_iters+i)
            
    def validate_large_image(self, log_name, datasets, ds_weights, ret_img=False):
        self.G.eval()
        self.D.eval()
        self.G_crit.eval()
        # select an AOI by area weight
        ds_name = np.random.choice(sorted(datasets.keys()), p=ds_weights)

        pc = choose_pixel_centers(datasets[ds_name], num_pc=1, large_img=True) # get one pixel center for large val img
        large_val_img_tiles = int(LARGE_VAL_IMG_SIZE / TILE_SIZE)
        large_val_img_range = range(int(-large_val_img_tiles/2), int(large_val_img_tiles/2))
        pixel_centers = [[[pc[0]+i*TILE_SIZE, pc[1]+j*TILE_SIZE] for j in large_val_img_range] for i in large_val_img_range] # pcs of tiles of big img
        pixel_centers = np.concatenate(np.array(pixel_centers), axis=0)

        inputs, tile_truths = data_sampler(datasets, ds_name, pixel_centers)
        
        # if only 1 sample in batch, skip it (otherwise batchnorm breaks)
        # TODO: ensure no 1 sample batches at end of ds
        assert inputs.shape[0] > 1, 'must have more than one sample in batch'

        # move data to gpu # make sure data will fit by using smaller large val image
        inputs = inputs.type(DATA_TYPE).to(gpu)
        tasks_out = {}
        for img in inputs:
            img_ = img.unsqueeze(0)
            out = self.G(img_)
            for k in out.keys():
                if not k in tasks_out.keys(): tasks_out[k] = []
                out_ = out[k][0].detach().to(cpu)
                tasks_out[k].append(out_)
        for k in tasks_out.keys():
            tasks_out[k] = torch.stack(tasks_out[k])
        for k in tile_truths.keys():
            tile_truths[k] = tile_truths[k].type(DATA_TYPE)
            
        # reshape images for logging
        inputs = inputs.reshape(large_val_img_tiles, large_val_img_tiles, *inputs.shape[1:]) # NH, NW, C, H, W
        NH, NW, C, H, W = inputs.shape
        inputs = inputs.moveaxis(1, 3) # NH, C, H, NW, W
        inputs = inputs.moveaxis(0, 1) # C, NH, H, NW, W
        inputs = inputs.reshape(C, NH*H, NW, W)
        inputs = inputs.reshape(C, NH*H, NW*W)
        inputs = inputs.reshape(1, C, NH*H, NW*W)
        for k in tasks_out.keys():
            tmp = tasks_out[k] # NH*NW, 1, H, W
            C, H, W = tmp.shape[1:]
            tmp = tmp.reshape(NH, NW, C, H, W)
            tmp = tmp.moveaxis(1, 3)
            tmp = tmp.moveaxis(0, 1)
            tmp = tmp.reshape(C, NH*H, NW, W)
            tmp = tmp.reshape(C, NH*H, NW*W)
            tmp = tmp.reshape(1, C, NH*H, NW*W)
            tasks_out[k] = tmp
        for k in tile_truths.keys():
            tmp = tile_truths[k] # NH*NW, 1, H, W
            C, H, W = tmp.shape[1:]
            tmp = tmp.reshape(NH, NW, 1, H, W)
            tmp = tmp.moveaxis(1, 3)
            tmp = tmp.moveaxis(0, 1)
            tmp = tmp.reshape(1, NH*H, NW, W)
            tmp = tmp.reshape(1, NH*H, NW*W)
            tmp = tmp.reshape(1, 1, NH*H, NW*W)
            tile_truths[k] = tmp
        print('validate large image:', inputs.shape, tasks_out.keys())

        self.G.train()
        self.D.train()
        self.G_crit.train()
        
        if ret_img:
            print(ds_name)
            return inputs[:, 0:1].detach().to(cpu), tasks_out['height'].detach().to(cpu), \
            tile_truths['height'].detach().to(cpu)
        else:
            self.log_images(log_name+'_big_val', inputs, tasks_out, tile_truths)
    
    def save(self, path, force=False):
        if not os.path.isdir(os.path.join(self.train_dir, path)):
            os.makedirs(os.path.join(self.train_dir, path))
        if os.path.isfile(os.path.join(self.train_dir, path, 'generator.pt')) and force:
            print('Overwriting...')
        if os.path.isfile(os.path.join(self.train_dir, path, 'generator.pt')) and not force:
            print('Model of same name already exists. Save manually if you intend to overwrite it.')
        else:
            torch.save(self.G.state_dict(), os.path.join(self.train_dir, path, 'generator.pt'))
            torch.save(self.D.state_dict(), os.path.join(self.train_dir, path, 'discriminator.pt'))
            torch.save(self.G_crit.state_dict(), os.path.join(self.train_dir, path, 'multiloss.pt'))
            with open(os.path.join(self.train_dir, path, 'global_iter.txt'), 'w') as f:
                f.write(str(self.global_iter))
            print('Model saved.')

    def load(self, path):
        if os.path.isdir(os.path.join(self.train_dir, path)):
            self.G.load_state_dict(torch.load(os.path.join(self.train_dir, path, 'generator.pt')))
            self.D.load_state_dict(torch.load(os.path.join(self.train_dir, path, 'discriminator.pt')))
            self.G_crit.load_state_dict(torch.load(os.path.join(self.train_dir, path, 'multiloss.pt')))
            with open(os.path.join(self.train_dir, path, 'global_iter.txt')) as f:
                self.global_iter = int(f.read())
            print('Model loaded.')
        else:
            print('No model to load.')
