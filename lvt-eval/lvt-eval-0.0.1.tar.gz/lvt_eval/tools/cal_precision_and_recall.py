from lvt_eval.tools.ap_per_class import ap_per_class
from lvt_eval.utils.boxes import box_iou, box_iou_numpy
# import torch
import numpy as np

def cal_precision_and_recall(target_data, prediction_data, names, nc):
    target_info = target_data
    prediction_info = prediction_data
    iouv = np.linspace(0.5, 0.95, 10)  # iou vector for mAP@0.5:0.95
    niou = iouv.size
    target_list, prediction_list = [], []
    mp, mr, map50, map, seen = 0.0, 0.0, 0.0, 0.0, 0
    stats = []
    # target 
    for i in range(len(target_info['annotations'])):
        tx1, ty1 = target_info['annotations'][i]["bbox"][0], target_info['annotations'][i]["bbox"][1]
        tx2, ty2 = target_info['annotations'][i]["bbox"][0] + target_info['annotations'][i]["bbox"][2], target_info['annotations'][i]["bbox"][1] + target_info['annotations'][i]["bbox"][3]
        timage_id, tcat = float(target_info['annotations'][i]["image_id"]), float(target_info['annotations'][i]["category_id"])
        target_list.append([timage_id, tcat, tx1, ty1, tx2, ty2])
    # target_tensor = torch.from_numpy(np.array(target_list))
    target_tensor = np.array(target_list)
    
    #　prediction
    for j in range(len(prediction_info)):
        px1, py1 = prediction_info[j]["bbox"][0], prediction_info[j]["bbox"][1]
        px2, py2 = prediction_info[j]["bbox"][0] + prediction_info[j]["bbox"][2], prediction_info[j]["bbox"][1] + prediction_info[j]["bbox"][3]
        pimage_id, pcat, score = float(prediction_info[j]["image_id"]), float(prediction_info[j]["category_id"]), prediction_info[j]["score"]
        prediction_list.append([pimage_id, px1, py1, px2, py2, score, pcat])
    # prediction_tensor = torch.from_numpy(np.array(prediction_list))
    prediction_tensor = np.array(prediction_list)

    for si in range(int(prediction_tensor[:,0][-1])):
        labels = target_tensor[target_tensor[:, 0] == si, 1:]
        nl = len(labels)
        
        tcls = labels[:, 0].tolist() if nl else []  # target class
        predn = prediction_tensor[prediction_tensor[:, 0] == si, 1:]
        
        seen += 1 
        # Evaluate
        if nl:
            
            tbox = labels[:, 1:5]  # target boxes
            labelsn = np.column_stack((labels[:, 0:1], tbox))  # native-space labels
            correct = process_batch_numpy(predn, labelsn, iouv)
            
        else:
            correct = np.zeros((predn.shape[0], niou)).astype(bool)
        stats.append((correct, predn[:, 4], predn[:, 5], tcls))  # (correct, conf, pcls, tcls)
    # Compute statistics
    stats = [np.concatenate(x, 0) for x in zip(*stats)]  # to numpy
    
    if len(stats) and stats[0].any():
        
        tp, fp, p, r, f1, ap, ap_class = ap_per_class(*stats, names=names)
        
        ap50, ap = ap[:, 0], ap.mean(1)  # AP@0.5, AP@0.5:0.95
        mp, mr, map50, map = p.mean(), r.mean(), ap50.mean(), ap.mean()
    nt = np.bincount(stats[3].astype(int), minlength=nc)  # number of targets per class
    # else:
    #     nt = np.zeros(1)

    # Print results
    # 类别 + 测试图片的数量（并非统计图片总数，而是测试图片序号的最后一个数值）+ 匹配正确的box数量 + 这个类别的precision + 这个类别的recall + 这个类别的mAP@0.5 + 这个类别的mAP@0.5:0.95
    s = ('%10s' + '%12s' * 2 + '%8s' * 2 + '%11s' * 2) % ('Class', 'Images', 'Labels', 'P', 'R', 'mAP@.5', 'mAP@.5:.95')
    print(s)
    pf = '%10s' + '%9i' * 2 + '%11.3g' * 4  # print format
    print(pf % ('all', seen, nt.sum(), mp, mr, map50, map))

    # Print results per class
    if nc > 1 and len(stats):
        for i, c in enumerate(ap_class):     
            print(pf % (names[c], seen, nt[c], p[i], r[i], ap50[i], ap[i]))

def process_batch(detections, labels, iouv):
    """
    Return correct predictions matrix. Both sets of boxes are in (x1, y1, x2, y2) format.
    Arguments:
        detections (Array[N, 6]), x1, y1, x2, y2, conf, class
        labels (Array[M, 5]), class, x1, y1, x2, y2
    Returns:
        correct (Array[N, 10]), for 10 IoU levels
    """
    correct = torch.zeros(detections.shape[0], iouv.shape[0], dtype=torch.bool, device=iouv.device)
    iou = box_iou(labels[:, 1:], detections[:, :4])
    x = torch.where((iou >= iouv[0]) & (labels[:, 0:1] == detections[:, 5]))  # IoU above threshold and classes match
    if x[0].shape[0]:
        matches = torch.cat((torch.stack(x, 1), iou[x[0], x[1]][:, None]), 1).cpu().numpy()  # [label, detection, iou]
        if x[0].shape[0] > 1:
            matches = matches[matches[:, 2].argsort()[::-1]]
            matches = matches[np.unique(matches[:, 1], return_index=True)[1]]
            # matches = matches[matches[:, 2].argsort()[::-1]]
            matches = matches[np.unique(matches[:, 0], return_index=True)[1]]
        matches = torch.Tensor(matches).to(iouv.device)
        correct[matches[:, 1].long()] = matches[:, 2:3] >= iouv
    return correct

def process_batch_numpy(detections, labels, iouv):
    """
    Return correct predictions matrix. Both sets of boxes are in (x1, y1, x2, y2) format.
    Arguments:
        detections (Array[N, 6]), x1, y1, x2, y2, conf, class
        labels (Array[M, 5]), class, x1, y1, x2, y2
    Returns:
        correct (Array[N, 10]), for 10 IoU levels
    """
    correct = np.zeros((detections.shape[0], iouv.shape[0])).astype(bool)
    iou = box_iou_numpy(labels[:, 1:], detections[:, :4])
    
    x = np.where((iou >= iouv[0]) & (labels[:, 0:1] == detections[:, 5]))  # IoU above threshold and classes match
    if x[0].shape[0]:
        matches = np.column_stack((np.stack(x, 1), iou[x[0], x[1]][:, None]))#.cpu().numpy()  # [label, detection, iou]
        if x[0].shape[0] > 1:
            matches = matches[matches[:, 2].argsort()[::-1]]
            matches = matches[np.unique(matches[:, 1], return_index=True)[1]]
            # matches = matches[matches[:, 2].argsort()[::-1]]
            matches = matches[np.unique(matches[:, 0], return_index=True)[1]]
        # matches = torch.Tensor(matches).to(iouv.device)
        correct[matches[:, 1].astype(int)] = matches[:, 2:3] >= iouv
    return correct

def process_batch_v2(detections, labels, iouv):
    """
    Return correct predictions matrix. Both sets of boxes are in (x1, y1, x2, y2) format.
    Arguments:
        detections (Array[N, 6]), x1, y1, x2, y2, conf, class
        labels (Array[M, 5]), class, x1, y1, x2, y2
    Returns:
        correct (Array[N, 10]), for 10 IoU levels
    """
    correct = np.zeros((detections.shape[0], iouv.shape[0])).astype(bool)
    iou = box_iou_numpy(labels[:, 1:], detections[:, :4])
    for i in range(len(iouv)):
        x = np.where((iou >= iouv[i]) & (labels[:, 0:1] == detections[:, 5]))  # IoU above threshold and classes match
        if x[0].shape[0]:
            matches = np.concatenate((np.stack(x, 1), iou[x[0], x[1]][:, None], detections[x[1],4:5]), 1) #.cpu().numpy()  # [label, detection, iou, score]
            if x[0].shape[0] > 1:
                # sort matches by iou to choose the best matched box
                matches = matches[matches[:, 2].argsort()[::-1]]
                matches = matches[np.unique(matches[:, 1], return_index=True)[1]]
                # sort matches by score to choose the best matched class
                matches = matches[matches[:, 3].argsort()[::-1]]
                matches = matches[np.unique(matches[:, 0], return_index=True)[1]]
            # matches = torch.Tensor(matches).to(iouv.device)
            correct[matches[:, 1].astype(int),i] = True
    
    return correct

if __name__ == '__main__':
    detections = np.array([[166.7203, 378.4348, 196.1190, 398.7478,   0.9387,   0.0000],
        [168.0732, 399.3882, 194.4995, 419.9093,   0.9304,   0.0000],
        [134.6291, 521.1181, 163.5203, 545.9926,   0.7533,   0.0000]])
    labels = np.array([[  0.0000, 167.4550, 397.9094, 198.7564, 418.9667],
        [  0.0000, 137.3941, 521.1845, 161.7689, 546.5866],
        [  0.0000, 137.0474, 500.2992, 163.5090, 518.9866],
        [  0.0000, 167.9946, 379.5518, 195.5183, 395.2098],
        [  0.0000, 112.2710, 278.8515, 122.8941, 296.7064]])
    iouv = np.array([0.5000, 0.5500, 0.6000, 0.6500, 0.7000, 0.7500, 0.8000, 0.8500, 0.9000,
        0.9500])
    print(process_batch_v2(detections, labels, iouv))
    detections = torch.tensor([[166.7203, 378.4348, 196.1190, 398.7478,   0.9387,   0.0000],
        [168.0732, 399.3882, 194.4995, 419.9093,   0.9304,   0.0000],
        [134.6291, 521.1181, 163.5203, 545.9926,   0.7533,   0.0000]])
    labels = torch.tensor([[  0.0000, 167.4550, 397.9094, 198.7564, 418.9667],
        [  0.0000, 137.3941, 521.1845, 161.7689, 546.5866],
        [  0.0000, 137.0474, 500.2992, 163.5090, 518.9866],
        [  0.0000, 167.9946, 379.5518, 195.5183, 395.2098],
        [  0.0000, 112.2710, 278.8515, 122.8941, 296.7064]])
    iouv = torch.tensor([0.5000, 0.5500, 0.6000, 0.6500, 0.7000, 0.7500, 0.8000, 0.8500, 0.9000,
        0.9500])
    print(process_batch(detections, labels, iouv))
    '''
    [[ True  True  True  True  True False False False False False]
 [ True  True  True  True  True  True False False False False]
 [ True  True  True  True  True  True  True False False False]]'''