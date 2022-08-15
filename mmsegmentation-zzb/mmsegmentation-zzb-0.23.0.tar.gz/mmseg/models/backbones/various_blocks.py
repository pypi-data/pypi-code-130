import torch
import torch.nn as nn
from mmcv.cnn import ConvModule
class Dilated(nn.Module):
    def __init__(self,dilation_date,input_channels,output_channels):
        super(Dilated, self).__init__()
        self.aspp = ConvModule(
            in_channels=input_channels,
            out_channels=output_channels,
            stride=1,
            kernel_size=3,
            dilation=dilation_date,
        )
    def forward(self, x):
        out = self.aspp(x)
        return out

aspp = Dilated(input_channels=3, output_channels=16, dilation_date=3)
x = torch.rand(1,3,16,16)
y = aspp(x)
print(y.shape)