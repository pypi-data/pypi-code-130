from lvt_eval.utils.functions import arc_function
import logging
logging.basicConfig(format='%(asctime)s [%(pathname)s:%(lineno)d] %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    level=logging.INFO)


def cal_new_ap(a_precision, pred_all_boxes, pred_false_boxes, unmatch_pred_img, all_imgs_set, prediction_data, new_jdict_img=[]):
    if a_precision != 1:
        pred_imgs_with_gt = len(all_imgs_set) - len(new_jdict_img) - len(unmatch_pred_img) # 测试图片负样本中没有检测出框的图片数
        logging.info("AP_coco: {};len(pred_false_boxes): {};len(pred_all_boxes): {}".format(a_precision, len(pred_false_boxes), len(pred_all_boxes)))
        logging.info("len(imgs_with_gt): {};len(pred_imgs_without_gt): {};len(all_imgs): {}".format(len(new_jdict_img), pred_imgs_with_gt, len(all_imgs_set)))
        
        new_ap = a_precision * arc_function(len(pred_false_boxes), len(pred_all_boxes)) * ((len(new_jdict_img) + pred_imgs_with_gt) / len(all_imgs_set))
    else:
        if prediction_data == [] and pred_false_boxes == []:
            new_ap = 1
        else:
            pred_imgs_with_gt = len(all_imgs_set) - len(unmatch_pred_img)
            logging.info("len(pred_false_boxes): {}".format(len(pred_false_boxes)))
            logging.info("len(pred_imgs_without_gt): {};len(all_imgs): {}".format(pred_imgs_with_gt, len(all_imgs_set)))
            new_ap = arc_function(len(pred_false_boxes), len(pred_all_boxes)) * pred_imgs_with_gt / len(all_imgs_set)
    logging.info("new_ap_criterion: {}".format(round(new_ap, 3)))