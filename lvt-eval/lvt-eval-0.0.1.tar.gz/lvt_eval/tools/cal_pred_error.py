import jsonpath
import logging
logging.basicConfig(format='%(asctime)s [%(pathname)s:%(lineno)d] %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    level=logging.INFO)

def cal_per_image_prediction_boxes_error(unmatched_data, img_num, threshold): # 平均每张图片的误报框数量
    raw_data = unmatched_data
    prediction_boxes_error = round(len(raw_data) / img_num, 5) # p = 所有误报框数（指的是负样本图片中预测出框的数量） / 总图片数
    logging.info("所有误报框数量（预测框所在的图片没有包含任何一个真实框，属于误报）: {};有效测试图片总数量: {}".format(len(raw_data), img_num))
    logging.info('在threshold = {0}的情况下，平均每张图片的误报框数量:{1}'.format(threshold, prediction_boxes_error))
    logging.info("==" * 40)
    
def cal_image_prediction_error_rate(pred_data, pred_false_boxes, gt_data, img_len, threshold, classes):

    category_num = dict()
    pred_image_id = jsonpath.jsonpath(pred_data, "$[*].image_id")
    gt_image_id = jsonpath.jsonpath(gt_data, "$.annotations[*].image_id")
    false_image_id = jsonpath.jsonpath(pred_false_boxes, "$[*].image_id")
    pred_image_id_set = set(pred_image_id)
    gt_image_id_set = set(gt_image_id)
    if pred_false_boxes != []:
        false_image_id_set = set(false_image_id)
        if pred_image_id_set and gt_image_id_set:
            total_image_prediction_error_rate = round(len(false_image_id_set) / img_len, 5)
            logging.info("错误预测图片的数量: {};有效测试图片总数量: {}".format(len(false_image_id_set), img_len))
            logging.info('在threshold = {0}的情况下，图片级别的总预测错误率(image_predictions_error_rate, iper):{1}.'.format(threshold, total_image_prediction_error_rate))
                
            for i in range(len(classes)):
                category_num.setdefault(classes[i], [])
                for p in pred_false_boxes:
                    if p["category_id"] == classes[i].index(classes[i]) and p["score"] > threshold:
                        category_num[classes[i]].append(p["image_id"])
            
            score_list = []
            for k in range(len(classes)):
                per_class_false_image_nums = set(category_num[classes[k]])
                per_class_image_prediction_error_rate = round(len(per_class_false_image_nums) / img_len, 5)
                logging.info("{}类错误预测图片的数量: {}".format(classes[k], len(per_class_false_image_nums)))
                score_list.append(per_class_image_prediction_error_rate)
            
            for x in zip(classes, score_list):
                logging.info('图片级别——{0}类别的预测错误率为: {1}'.format(x[0], x[1]))
    else:
        logging.info("no false images.")



    

