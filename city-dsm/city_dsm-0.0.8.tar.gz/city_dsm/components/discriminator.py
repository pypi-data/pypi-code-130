import torch

class CLSGAN(torch.nn.Module):
    def __init__(self, num_layers=3):
        super().__init__()
        chs_mul = 64
        input_block_params = {
            'in_channels': 1,
            'out_channels': chs_mul,
            'kernel_size': (1,1),
            'padding': 1
        } # get same size feature maps from inputs
        self.stereo_fe = torch.nn.Conv2d(**input_block_params) # stereo dsm feature extractor
        self.clean_fe = torch.nn.Conv2d(**input_block_params) # clean dsm feature extractor
        
        chs = 1
        chs_prev = 1
        self.conv_blocks = [
            torch.nn.Conv2d(128, chs_mul, kernel_size=(4,4), stride=2, padding=1),
            torch.nn.LeakyReLU(0.2, True)
        ]
        for i in range(num_layers):
            chs_prev = chs
            chs = min(2**i, 8)
            self.conv_blocks += [
                torch.nn.Conv2d(chs_prev*chs_mul, chs*chs_mul, kernel_size=(4,4), stride=2, padding=1),
                torch.nn.BatchNorm2d(chs*chs_mul),
                torch.nn.LeakyReLU(0.2, True)
            ]
        chs_prev = chs
        chs = min(2**num_layers, 8)
        self.conv_blocks += [
            torch.nn.Conv2d(chs_prev*chs_mul, chs*chs_mul, kernel_size=(4,4), stride=1, padding=1),
            torch.nn.BatchNorm2d(chs*chs_mul),
            torch.nn.LeakyReLU(0.2, True)
        ]
        self.conv_blocks += [
            torch.nn.Conv2d(chs*chs_mul, 1, kernel_size=(4,4), stride=1, padding=1)
        ]
        self.conv = torch.nn.Sequential(*self.conv_blocks)
    
    def forward(self, stereo_dsm, clean_dsm): # clean dsm is either G output or ground truth
        stereo_f = self.stereo_fe(stereo_dsm)
        clean_f = self.clean_fe(clean_dsm)
        features = torch.cat([stereo_f, clean_f], axis=1)
        out = self.conv(features)
        return out