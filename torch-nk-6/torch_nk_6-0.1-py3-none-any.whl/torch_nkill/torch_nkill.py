import dataset_vo
import cv2
import requests
import numpy as np
import torch
from torchvision import transforms
from torch.utils.data.dataset import Dataset

class CustomDataset(Dataset):
    def __init__(self, x_tensor, y_tensor):
        self.x = x_tensor
        self.y = y_tensor
        self.trans = transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406],
                                 std=[0.229, 0.224, 0.225])])

    def __getitem__(self, index):

        return self.trans(self.x[index]),  self.y[index]

    def __len__(self):
        return len(self.x)


class IteratorOfMyClass():
    def __init__(self):
        self.data_len = 5
        self.count = 0
        self.images = []
        self.datasetVo = dataset_vo.DatasetVo('aimeets/iii')

        self.cifar_labels = {"airplane" : 0, "automobile" : 1, "bird" : 2, "cat":3, "deer":4, "dog":5, "frog":6,
                            "horse":7, "ship":8, "truck":9}


    def do(self, dataList):
        self.images = []
        self.labels = []
        for row in dataList:
            label = row['category']
            image_nparray = np.asarray(bytearray(requests.get(row['uri']).content), dtype=np.uint8)
            image = cv2.imdecode(image_nparray, cv2.IMREAD_COLOR)
            self.images.append(image)
            self.labels.append(self.cifar_labels[label])

    def __iter__(self):
        return self

    def __next__(self):

        if self.count == 0:

            self.datasetVo.fetchItemOfDataset(
                lambda dataList: self.do(dataList)
            )

        else:
            while self.datasetVo.hasNext():
                self.datasetVo.fetchItemOfDataset(
                    lambda dataList: self.do(dataList)
                )

        if self.count == self.data_len:
            raise StopIteration

        self.count += 1

        # 여기서 dataloader를 만들어서 return
        x_train_tensor = self.images
        y_train_tensor =self.labels

        train_data = CustomDataset(x_train_tensor, y_train_tensor)
        my_dataset_loader = torch.utils.data.DataLoader(dataset=train_data,
                                                        batch_size=len(train_data))

        return next(iter(my_dataset_loader))
