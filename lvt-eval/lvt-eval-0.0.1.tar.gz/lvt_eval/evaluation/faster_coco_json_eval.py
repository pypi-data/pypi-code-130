# coding: utf-8
import argparse
import numpy as np
from lvt_eval.utils.general import load_json
from faster_coco_eval.faster_coco_eval import COCO, COCOeval_faster
from lvt_eval.utils.merge_bbox import merge_bbox
from lvt_eval.tools.coco_error_analyze import coco_error_analysis
from lvt_eval.tools.cal_pred_error import cal_per_image_prediction_boxes_error, cal_image_prediction_error_rate
from lvt_eval.tools.cal_new_ap import cal_new_ap
from lvt_eval.tools.cal_precision_and_recall import cal_precision_and_recall
from lvt_eval.utils.check_predictions import check_predictions, check_json
from lvt_eval.utils.get_classes_and_imgs import get_classes_and_imgs

import logging
logging.basicConfig(format='%(asctime)s [%(pathname)s:%(lineno)d] %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    level=logging.INFO)

total_results = dict()

class FasterCocoJsonEvaluation:
    def __init__(self, gt_json, pred_json):
        self.gt_json = gt_json
        self.pred_json = pred_json
    
    def indicator(self):
        thresholds = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7] 
        pred_data = load_json(self.pred_json)
        gt_data = load_json(self.gt_json) 
        names, classes, img_len, img_ids = get_classes_and_imgs(self.gt_json) 
        nc = len(names)  
        for threshold in thresholds:
            logging.info("+-----------------------------------------------------------------------------------+") 
            logging.info('threshold = {}'.format(threshold))
            if gt_data["annotations"] == [] and len(pred_data) == 0:
                logging.info('The model accuracy is 100%, AP = 1.0, AR = 1.0')

            elif gt_data["annotations"] == [] and pred_data:
                a_precision = 1
                pred_false_boxes = matched_pred_boxes = pred_data
                all_imgs_set = img_ids
                unmatch_pred_img = check_predictions(pred_data)
                cal_new_ap(a_precision, pred_data, pred_false_boxes, unmatch_pred_img, all_imgs_set, matched_pred_boxes)

            elif gt_data["annotations"] != [] and pred_data:           
                matched_pred_boxes, pred_false_boxes, unmatch_pred_img, matched_pred_imgs, all_imgs_set = check_json(pred_data, gt_data, threshold)

                if matched_pred_boxes == [] and pred_false_boxes == []:
                    a_precision = 1
                elif matched_pred_boxes or (matched_pred_boxes and pred_false_boxes):
                    cal_image_prediction_error_rate(matched_pred_boxes, pred_false_boxes, gt_data, img_len, threshold, classes)  
                    a_precision = self.cal_map(gt_data, matched_pred_boxes)
                    cal_precision_and_recall(gt_data, matched_pred_boxes, names, nc)
                    merge_results = merge_bbox(gt_data, matched_pred_boxes)
                    coco_error_analysis(merge_results, save_dir='./insect')
                    if pred_false_boxes:
                        cal_per_image_prediction_boxes_error(pred_false_boxes, img_len, threshold)
                
                elif pred_false_boxes and unmatch_pred_img and not matched_pred_boxes:
                    cal_per_image_prediction_boxes_error(pred_false_boxes, img_len, threshold)
                    a_precision = 1
                
                cal_new_ap(a_precision, pred_data, pred_false_boxes, unmatch_pred_img, all_imgs_set, matched_pred_boxes, matched_pred_imgs)


    def cal_map(self, gt_data, pred_data):
    
        anno = COCO(gt_data)
        pred = anno.loadRes(pred_data)
        
        eval = COCOeval_faster(anno, pred, 'bbox')
        eval.evaluate()
        eval.accumulate()
        eval.summarize()

        precisions = eval.eval['precision']
        a_precision = np.mean(precisions[:, :, :, 0, -1])

        return a_precision

if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(description='Start evaluation.')
    parser.add_argument('--gt_json', type=str, help='groundtruth absolute path', default='')
    parser.add_argument('--pred_json', type=str, help='prediction absolute path', default='')
    args = parser.parse_args()

    groundtruth_json = args.gt_json
    prediction_json = args.pred_json

    eval = FasterCocoJsonEvaluation(groundtruth_json, prediction_json)
    eval.indicator()
