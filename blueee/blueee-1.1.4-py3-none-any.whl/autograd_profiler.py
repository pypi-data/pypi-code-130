


import torch


class Net(torch.nn.Module):
    def __init__(self):
        super(Net, self).__init__()

        self.l1 = torch.nn.Linear(4,16)
        self.l2 = torch.nn.Linear(16,10000)
        self.drop = torch.nn.Dropout()



    def forward(self,x):
        x = (self.l2(self.l1(x)))
        x = self.drop(x)
        return x
from torchvision import models

model = models.resnet18().cuda()

x = torch.randn(3,3,224,224).cuda()

# print(x,'\n',model(x))
#
with torch.autograd.profiler.profile(enabled=True, use_cuda=True, record_shapes=True) as prof:
    outputs = model(x)
print(prof.table())

