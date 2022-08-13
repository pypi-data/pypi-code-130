import torch
from pytorch_common.modules import Fn


class PredictMixin:
    def validation(self, data_loader):
        return Fn.validation(self, data_loader, self.device)

    def predict(self, features):
        self.eval()
        with torch.no_grad():
            return self(features.to(self.device))
