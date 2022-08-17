import cv2
import numpy as np
import torch
from torchvision import transforms
from torch.utils.data.dataset import Dataset
import requests

URL = 'http://3.36.93.19'
# URL = 'http://localhost:8080'

"""
ID: {user_id}/{repository_id}:{version}
        * version : default is 'latest'. The format is {x.x.x}
"""


class DatasetVo:
    totalBatch: int

    def __init__(self, uid):
        super(DatasetVo, self).__init__()
        self.list = list()
        # 배치정보
        self.batch = 1
        # 한 배치당 불러올 이미지 목록수
        self.size = 0
        # 하나의 에폭에 대해서 설정된 batch 의 총 갯수 (self.batch 의 설정에 따라 달라진다)
        self.totalBatch = 0
        # 전체 데이터 수
        self.totalSize = 0
        self.id = uid
        self.loading = False
        self._parseId()

    def _parseId(self):
        if self.id is None or self.id == '':
            raise Exception('Needs Id.')
        splitList = self.id.split('/')
        count = len(list(splitList))
        if splitList is None or len(list(splitList)) == 0 or len(list(splitList)) > 2:
            raise Exception('The information of Id is invalid.')
        repositoryInfo = splitList[1]

        if repositoryInfo is None or repositoryInfo == '':
            raise Exception('The repository information is invalid.')
        parseRepositoryInfo = repositoryInfo.split(':')
        if parseRepositoryInfo is None or len(parseRepositoryInfo) == 0 or len(parseRepositoryInfo) > 1:
            raise Exception('The repository information is invalid.')

        self.userId = splitList[0]
        self.repositoryId = parseRepositoryInfo[0]
        if len(parseRepositoryInfo) == 2:
            self.repositoryVersion = parseRepositoryInfo[1]
        else:
            self.repositoryVersion = 'latest'

    # 데이터 불러오는 함수
    def fetchItemOfDataset(self, func):
        if self.loading:
            return
        if self.batch > 0 and (self.batch == self.totalBatch):
            return
        self.loading = True
        queryString = {
            "id": self.id,
            "batch": self.batch,
            "size": self.size
        }
        response = requests.get(URL + '/data', params=queryString)

        if response.status_code == 200:
            data = response.json()
            self.batch = self.batch + 1
            self.size = data['size']
            self.totalBatch = data['total_batch']
            self.totalSize = data['total_size']
            dataList = data['list']
            self.list.extend(dataList)
            self.loading = False
            func(dataList)
        else:
            self.loading = False

    # 처음부터 다시 호출하고 싶을 경우
    def initialize(self):
        self.batch = 0
        self.totalBatch = 0
        self.totalSize = 0
        self.list = self.list.clear()

    # 불러올 데이터가 더 존재하는지 여부 검사 (에폭이 끝나지 않음을 의미)
    def hasNext(self):
        # 테스트를 위해서 89번째 줄을 사용. 실제 서비스에서는 90번째 줄을 사용하고 현재는 너무 많은 데이터를 불러와서 테스트를 위해서 사용
        return self.batch > 0 and (self.batch < 5)
        # return self.batch > 0 and (self.batch != self.totalBatch)

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
        self.datasetVo = DatasetVo('aimeets/iii')

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

