from typing import Tuple
import warnings; warnings.filterwarnings(action='ignore')
from numpy import ix_
import torch
import torch.nn.functional as F
from torch import nn
from torch.fft import fft2, ifft2, fftshift


class GIST(nn.Module):
    """
    Must input resized crop (imagesize, bilinear)
    Need not convert to grey scale(auto)
    """
    def __init__(
        self, 
        orientations_per_scale: Tuple = (8, 8, 8, 8), 
        num_blocks=4, 
        fc_prefilt=4,
        image_size: Tuple[int, int] = (256, 256),
        boundary_extension=32):
        
        super(GIST, self).__init__()
        self.orientations_per_scale = orientations_per_scale
        self.num_blocks = num_blocks
        self.fc_prefilt = fc_prefilt
        self.image_size = image_size
        self.boundary_extension = boundary_extension
        self.gabors = self._create_gabor(
            orientations_per_scale=orientations_per_scale,
            image_size=(
                image_size[0] + 2*boundary_extension,
                image_size[1] + 2*boundary_extension,
            )
        )
        self.n_features = self.gabors.shape[2]*num_blocks**2
        
        
    def forward(self, x):
        if len(x.shape) == 3: # Single image
            x = x.mean(axis=0) # convert to gray scale(code from Olivia's LMgist.m)
            x -= x.min()
            x *= 255/x.max()
            
            # prefiltering: local contrast scaling
            output = self._prefilt(x, self.fc_prefilt) 
            
            # get gist:
            g = self._gist_gabor(output);
            
        elif len(x.shape) == 4: # Batch images
            """ TODO : Batch processing """
            x = x.mean(axis=1)
            x -= x.min(dim=2, keepdim=True).values.min(dim=1, keepdim=True).values
            x *= 255/x.max(dim=1, keepdim=True).values.max(dim=2, keepdim=True).values
            
            # prefiltering: local contrast scaling
            outputs = torch.cat([self._prefilt(i, self.fc_prefilt).unsqueeze(dim=0) for i in x], dim=0)
            
            # get gist:
            g = torch.cat([self._gist_gabor(i).unsqueeze(dim=0) for i in outputs], dim=0)
        else:
            raise Exception("Tensor dimensions must be 3(single image) or 4(batch images).")

        return g.flatten(start_dim=0) if len(g.shape) == 2 else g.flatten(start_dim=1)
    
    
    def _gist_gabor(self, img):
        n_img = 1 # TODO : Batch image processing
        ny, nx, n_filters = self.gabors.shape
        n_windows = self.num_blocks*self.num_blocks

        # pad image
        img = self._symmetric_pad(img, (self.boundary_extension, self.boundary_extension))
            
        g = torch.zeros(n_windows*n_filters, n_img)
        
        img = fft2(img)
        k = 0
        for n in range(n_filters):
            if n_img == 1:
                gist = self.gabors[:, :, n]
            else:
                gist = torch.tile(self.gabors[:, :, n].reshape(self.gabors.shape[0], self.gabors.shape[0], 1), (1, 1, n_img))
            ig = torch.abs(ifft2(img * gist))
            ig = ig[self.boundary_extension:ny - self.boundary_extension, self.boundary_extension:nx - self.boundary_extension]
            v = self._down_n(ig, self.num_blocks)
            g[k:k + n_windows, :] = v.T.reshape((n_windows, n_img))
            k += n_windows
            
        return g
    
    
    def _down_n(self, x, num):
        nx = torch.fix(torch.linspace(0, x.shape[0], num + 1))
        ny = torch.fix(torch.linspace(0, x.shape[1], num + 1))
        y = torch.zeros((num, num))
        
        for i in range(num):
            for j in range(num):
                if len(x.shape) == 2:
                    avg = torch.mean(torch.mean(x[int(nx[i]):int(nx[i + 1]), int(ny[j]):int(ny[j + 1])]), 0)
                    y[i, j] = avg.flatten()
                else:
                    pass
        return y
    
    
    def _prefilt(self, img, fc=4):
        w, s1 = 5, fc/torch.sqrt(torch.log(torch.Tensor([2])))

        # Pad images to reduce boundary artifacts
        img = torch.log(img + 1)
        
        if len(img.shape) == 2: # Single image
            img = self._symmetric_pad(img, (w, w))
            sn, sm = img.shape
            n = max(sn, sm)
            n += n % 2
            img = self._symmetric_pad(img, (n - sn, n - sm), 'post')
        elif len(img.shape) == 3: # Batch images
            img = torch.cat([self._symmetric_pad(i, (w, w)).unsqueeze(dim=0) for i in img], dim=0)
            sn, sm = img.shape[1:]
            n = max(sn, sm)
            n += n % 2
            img = torch.cat([self._symmetric_pad(i, (n - sn, n - sm), 'post').unsqueeze(dim=0) for i in img], dim=0)        

        # Filter
        fy, fx = torch.meshgrid(torch.arange(-n//2, n//2), torch.arange(-n//2, n//2))
        gf = fftshift(torch.exp(-(fx**2 + fy**2)/(s1**2)))

        # Whitening
        if len(img.shape) == 2: # Single image
            output = img - (ifft2(fft2(img)*gf)).real
            
            # Local contrast normalization
            localstd = torch.sqrt(torch.abs(ifft2(fft2((output**2))*gf)))
            output /= .2 + localstd
        elif len(img.shape) == 3: # Batch images
            output = torch.cat([(i - (ifft2(fft2(i)*gf)).real).unsqueeze(dim=0) for i in img], dim=0)
            
            # Local contrast normalization
            localstd = torch.cat([torch.sqrt(torch.abs(ifft2(fft2((i**2))*gf))).unsqueeze(dim=0) for i in output], dim=0)
            output /= .2 + localstd
        del img

        # crop output to have same size than the input
        return output[w:(sn - w), w:(sm - w)]
    
    
    def _create_gabor(
        self, 
        orientations_per_scale: Tuple, 
        image_size: Tuple
        ) -> torch.FloatTensor:
        num_scales, num_filters = len(orientations_per_scale), sum(orientations_per_scale)
        param = []

        for i in range(num_scales):
            for j in range(orientations_per_scale[i]):        
                param.append(torch.Tensor([
                    .35, 
                    .3/(1.85**i),
                    16*orientations_per_scale[i]**2/32**2,
                    torch.pi/(orientations_per_scale[i])*j
                ]).unsqueeze(dim=1))
        param = torch.cat(param, dim=1).T

        # Frequencies
        fy, fx = torch.meshgrid(
            torch.Tensor([i for i in range(-image_size[1]//2, image_size[1]//2)]),
            torch.Tensor([i for i in range(-image_size[0]//2, image_size[0]//2)]))
        fr = fftshift(torch.sqrt(fx**2 + fy**2))
        t = fftshift(torch.angle(fx + 1j*fy))

        # Transfer functions
        gabors = torch.zeros([image_size[0], image_size[1], num_filters])

        gabors = []
        for i in range(0, num_filters):
            tr = t + param[i, 3]
            tr += 2*torch.pi*(tr < -torch.pi) - 2*torch.pi*(tr > torch.pi)
            gabors.append((torch.exp(-10*param[i, 0]*(fr/image_size[1]/param[i, 1] - 1)**2 - 2*param[i,2]*torch.pi*tr**2)).unsqueeze(dim=-1))
        gabors = torch.cat(gabors, dim=2)

        return gabors
    
    
    def _symmetric_pad(self, arr, pad_size, direction = 'both'):
        ''' Matlab padarray function '''
        num_dims = len(pad_size)

        idx = []
        if len(arr.shape) == 1:
            size_arr = (1, len(arr))
        else:
            size_arr = arr.shape

        for k_indx in range(num_dims):
            tot = size_arr[k_indx]
            dim_nums = []
            dim_nums.append(torch.Tensor(range(1, tot + 1)))
            dim_nums.append(torch.Tensor(range(tot, 0, -1)))
            dim_nums = torch.cat(dim_nums, dim=0)
            pad = pad_size[k_indx]

            if direction == 'pre':
                idx.append([dim_nums[torch.remainder(torch.arange(-pad, tot), 2 * tot)]])
            elif direction == 'post':
                idx.append([dim_nums[torch.remainder(torch.arange(tot + pad), 2 * tot)]])
            elif direction == 'both':
                idx.append([dim_nums[torch.remainder(torch.arange(-pad, tot + pad), 2 * tot)]])

        first = idx[0][0] - 1
        second = idx[1][0] - 1
        return arr[ix_(first, second)]