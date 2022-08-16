import os
import numpy as np
import logging
logger = logging.getLogger(__name__)

def draw_pr_curve(precision,
                  recall,
                  iou=0.5,
                  out_dir='pr_curve',
                  file_name='precision_recall_curve.jpg'):
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
    output_path = os.path.join(out_dir, file_name)
    try:
        import matplotlib.pyplot as plt
    except Exception as e:
        logger.error('Matplotlib not found, plaese install matplotlib.'
                     'for example: `pip install matplotlib`.')
        raise e
    plt.cla()
    plt.figure('P-R Curve')
    plt.title('Precision/Recall Curve(IoU={})'.format(iou))
    plt.xlabel('Recall')
    plt.ylabel('Precision')
    plt.grid(True)
    plt.plot(recall, precision)
    plt.savefig(output_path)

def get_pr(precisions, coco_gt):
    cat_ids = coco_gt.getCatIds()
    # precision: (iou, recall, cls, area range, max dets)
    assert len(cat_ids) == precisions.shape[2]
    results_per_category = []
    for idx, catId in enumerate(cat_ids):
        # area range index 0: all area ranges
        # max dets index -1: typically 100 per image
        nm = coco_gt.loadCats(catId)[0]
        precision = precisions[:, :, idx, 0, -1]
        precision = precision[precision > -1]
        if precision.size:
            ap = np.mean(precision)
        else:
            ap = float('nan')
        results_per_category.append(
            (str(nm["name"]), '{:0.3f}'.format(float(ap))))
        pr_array = precisions[0, :, idx, 0, 2]
        recall_array = np.arange(0.0, 1.01, 0.01)
        draw_pr_curve(
            pr_array,
            recall_array,
            out_dir='insect/bbox_pr_curve',
            file_name='{}_precision_recall_curve.jpg'.format(nm["name"]))
