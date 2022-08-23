import torch
import numpy as np

from .model_config import DATA_TYPE, gpu

sd_reg_coeff = {
    'height': 10,
    'segmentation': 1,
    'norm': 0.1
} # scale factor of the homoscedatic uncertainty regularization term (cite https://arxiv.org/pdf/1705.07115.pdf)

# reference https://github.com/SimonVandenhende/Multi-Task-Learning-PyTorch
class MultiLoss(torch.nn.Module):
    def __init__(self, tasks: list, logvars: torch.nn.ParameterDict):
        super().__init__()
        assert tasks == sorted(list(logvars.keys()) + ['gan'])
        self.tasks = tasks
        self.criteria = torch.nn.ModuleDict(
            sorted([
                [c, loss_classes[c]] for c in tasks
            ])
        ) # losses for the tasks
        self.logvars = logvars # criteria weights
    
    def forward(self, tasks_out, tasks_truth, D_prediction):
        # wire up the losses to the right task outputs
        if not 'norm' in tasks_out:
            tasks_out['norm'] = tasks_out['height']
        if not 'gan' in tasks_out:
            tasks_out['gan'] = tasks_out['height']

        # output all losses
        losses = {
            t: self.criteria[t](tasks_out[t], tasks_truth[t]) for t in self.tasks if t != 'gan'
        }
        losses['gan'] = self.criteria['gan'](D_prediction, is_ground_truth=1.0) # want D to predict GT
        losses['total'] = torch.sum(torch.stack([
#             torch.exp(self.logvars[t]) * sd_reg_coeff[t] * losses[t] for t in self.tasks if t != 'gan'
            sd_reg_coeff[t] * losses[t] for t in self.tasks if t != 'gan'
        ])) # balanced losses
        losses['total'] += losses['gan']
#         losses['total'] += torch.sum(torch.stack([
#             -1/2 * self.logvars[t] for t in self.logvars
#         ])) # regularization
        return losses

# regular distance loss
class HeightLoss(torch.nn.L1Loss):
    def forward(self, height: torch.Tensor, target: torch.Tensor) -> torch.Tensor:
        in_mask = ~torch.isnan(height)
        target_mask = ~torch.isnan(target)
        mask = torch.logical_and(in_mask, target_mask)
        return torch.nn.functional.l1_loss(height[mask], target[mask], reduction=self.reduction)
# inverse distance loss
# class HeightLoss(torch.nn.L1Loss):
#     def forward(self, height: torch.Tensor, target: torch.Tensor) -> torch.Tensor:
#         in_mask = ~torch.isnan(height)
#         target_mask = ~torch.isnan(target)
#         mask = torch.logical_and(in_mask, target_mask)
#         inv_h = 1/height[mask]
#         inv_t = 1/target[mask]
#         return torch.nn.functional.l1_loss(inv_h, inv_t, reduction=self.reduction)

class SegLoss(torch.nn.CrossEntropyLoss):
    def forward(self, logits: torch.Tensor, target: torch.Tensor) -> torch.Tensor:
        target_ = torch.squeeze(target, dim=1)
        return torch.nn.functional.cross_entropy(
            logits,
            target_.long(), # this is the change: float -> long for target dtype
            weight=self.weight, ignore_index=self.ignore_index, reduction=self.reduction, 
            label_smoothing=self.label_smoothing
        )

# for norm calc
# CITE: https://arxiv.org/abs/1803.08673
class Sobel(torch.nn.Module):
    def __init__(self):
        super(Sobel, self).__init__()
        self.edge_conv = torch.nn.Conv2d(1, 2, kernel_size=3, stride=1, padding=1, bias=False)
        edge_kx = np.array([[1, 0, -1], [2, 0, -2], [1, 0, -1]])
        edge_ky = np.array([[1, 2, 1], [0, 0, 0], [-1, -2, -1]])
        edge_k = np.stack((edge_kx, edge_ky))

        edge_k = torch.from_numpy(edge_k).float().view(2, 1, 3, 3)
        self.edge_conv.weight = torch.nn.Parameter(edge_k)
        
        for param in self.parameters():
            param.requires_grad = False

    def forward(self, x):
        out = self.edge_conv(x)
        out = out.contiguous().view(-1, 2, x.size(2), x.size(3))
  
        return out

class NormLoss(torch.nn.Module):
    def __init__(self):
        super(NormLoss, self).__init__()
        self.get_gradient = Sobel()
        self.cos = torch.nn.CosineSimilarity(dim=1, eps=0)
        
    def forward(self, height: torch.Tensor, target: torch.Tensor) -> torch.Tensor:
        get_gradient = self.get_gradient
        cos = self.cos
        ones = torch.ones(*height.shape).type(DATA_TYPE).to(gpu)

        out_grad = get_gradient(height)
        target_grad = get_gradient(target)

        dout_dx = out_grad[:, 0, :, :].contiguous().view_as(height)
        dout_dy = out_grad[:, 1, :, :].contiguous().view_as(height)
        dtarget_dx = target_grad[:, 0, :, :].contiguous().view_as(height)
        dtarget_dy = target_grad[:, 1, :, :].contiguous().view_as(height)

        out_normal = torch.cat((-dout_dx, -dout_dy, ones), 1)
        target_normal = torch.cat((-dtarget_dx, -dtarget_dy, ones), 1)
        loss_normal = torch.abs(1 - cos(out_normal, target_normal))
        mask = ~torch.isnan(loss_normal) # ignore nans
        
        # set nan gradients to 0 (due to zeroed gradients from masked tensor)
        if height.requires_grad: # if not in test mode
            height.register_hook(lambda grad: torch.nan_to_num(grad))

        return loss_normal[mask].mean()
    
class GANLoss(torch.nn.Module):
    def forward(self, D_prediction, is_ground_truth):
        gt_tensor = torch.full(D_prediction.shape, is_ground_truth, dtype=DATA_TYPE).to(gpu)
        loss = torch.nn.MSELoss()(D_prediction, gt_tensor)
        return loss

loss_classes = {
    'gan': GANLoss(),
    'height': HeightLoss(), 
    'segmentation': SegLoss(),
    'norm': NormLoss()
}
