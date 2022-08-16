# conding: utf-8
# import torch
import numpy as np

def box_iou(box1, box2):
    # https://github.com/pytorch/vision/blob/master/torchvision/ops/boxes.py
    """
    Return intersection-over-union (Jaccard index) of boxes.
    Both sets of boxes are expected to be in (x1, y1, x2, y2) format.
    Arguments:
        box1 (Tensor[N, 4])
        box2 (Tensor[M, 4])
    Returns:
        iou (Tensor[N, M]): the NxM matrix containing the pairwise
            IoU values for every element in boxes1 and boxes2
    """

    def box_area(box):
        # box = 4xn
        return (box[2] - box[0]) * (box[3] - box[1])

    area1 = box_area(box1.T)
    area2 = box_area(box2.T)
    # inter(N,M) = (rb(N,M,2) - lt(N,M,2)).clamp(0).prod(2)
    inter = (torch.min(box1[:, None, 2:], box2[:, 2:]) - torch.max(box1[:, None, :2], box2[:, :2])).clamp(0).prod(2)
    return inter / (area1[:, None] + area2 - inter)  # iou = inter / (area1 + area2 - inter)

def box_iou_numpy(box1, box2):
    # https://github.com/pytorch/vision/blob/master/torchvision/ops/boxes.py
    """
    Return intersection-over-union (Jaccard index) of boxes.
    Both sets of boxes are expected to be in (x1, y1, x2, y2) format.
    Arguments:
        box1 (numpy[N, 4])
        box2 (numpy[M, 4])
    Returns:
        iou (numpy[N, M]): the NxM matrix containing the pairwise
            IoU values for every element in boxes1 and boxes2
    """
    def box_area(box):
        return (box[:,2] - box[:,0]) * (box[:,3] - box[:,1])

    area1 = box_area(box1)
    area2 = box_area(box2)
    inter = (np.minimum(box1[:, None, 2:], box2[:, 2:]) - np.maximum(box1[:, None, :2], box2[:, :2])).clip(0).prod(2)
    return inter / (area1[:, None] + area2 - inter)



def xywh2xyxy(x):
    # Convert nx4 boxes from [x, y, w, h] to [x1, y1, x2, y2] where xy1=top-left, xy2=bottom-right
    # y = x.clone() if isinstance(x, torch.Tensor) else np.copy(x)
    y = np.copy(x)
    y[:, 0] = x[:, 0] - x[:, 2] / 2  # top left x
    y[:, 1] = x[:, 1] - x[:, 3] / 2  # top left y
    y[:, 2] = x[:, 0] + x[:, 2] / 2  # bottom right x
    y[:, 3] = x[:, 1] + x[:, 3] / 2  # bottom right y
    return y

if __name__ == '__main__':
    box1 = torch.Tensor([[10, 10, 50, 50],
                [70, 70, 120, 120]])
    box2 = torch.Tensor([[10, 10, 50, 50],
                [100, 100, 150, 150],
                [80, 80, 160, 160],
                [130, 130, 200, 200]])
    print(box_iou(box1, box2))
    box1 = np.array([[10, 10, 50, 50],
                [70, 70, 120, 120]])
    box2 = np.array([[10, 10, 50, 50],
                [100, 100, 150, 150],
                [80, 80, 160, 160],
                [130, 130, 200, 200]])
    print(box_iou_numpy(box1, box2))

    '''
    tensor([[1.0000, 0.0000, 0.0000, 0.0000],
        [0.0000, 0.0870, 0.2192, 0.0000]])
        '''

