from tqdm import tqdm
import os
import cv2
import json
import numpy as np
from PIL import Image
import logging
logging.basicConfig(format='%(asctime)s [%(pathname)s:%(lineno)d] %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    level=logging.INFO)

def draw_groundtruth(gt_info, root_dir, output_dir, mapping):
    for i in tqdm(gt_info['annotations']):
        im_path = os.path.join(root_dir, "download_images", mapping[str(i['image_id'])])
        gt_output_img = os.path.join(root_dir, output_dir, mapping[str(i['image_id'])])

        if not os.path.exists(gt_output_img):
            gt_out = cv2.imread(im_path) # bgr
            b,g,r = cv2.split(gt_out)
            gt_out = cv2.merge([r,g,b]) 
            # gt_out = cv2.imdecode(np.fromfile(im_path, dtype=np.uint8), -1)
            if gt_out is None:
                gt_out = Image.open(im_path).convert('RGB') # rgb
            
        else: 
            gt_out = cv2.imread(gt_output_img)
            b,g,r = cv2.split(gt_out)
            gt_out = cv2.merge([r,g,b]) 
            # gt_out = cv2.imdecode(np.fromfile(gt_output_img, dtype=np.uint8), -1)
            if gt_out is None:
                gt_out = Image.open(gt_output_img).convert('RGB')
        gt_out = cv2.cvtColor(np.asarray(gt_out), cv2.COLOR_RGB2BGR)

        x, y, w, h = i["bbox"]
        x, y, w, h = int(x), int(y), int(w), int(h)
        x2, y2 = x + w, y + h
        cv2.rectangle(gt_out, (x, y), (x2, y2), (0, 0, 255), thickness=2) # red 
        cv2.imwrite(gt_output_img, gt_out)
    logging.info("Groundtruth done.")

def draw_predictions(pred_info, root_dir, output_dir, mapping):
    for p in tqdm(pred_info):
        img_path = os.path.join(root_dir, "download_images", mapping[str(p['image_id'])])
        pred_output_img = os.path.join(root_dir, output_dir, mapping[str(p['image_id'])])
        
        score = p["score"]
        category = p['category_id']
        if not os.path.exists(pred_output_img):
            pred_out = cv2.imread(img_path)
            b,g,r = cv2.split(pred_out)
            pred_out = cv2.merge([r,g,b]) 
            # pred_out = cv2.imdecode(np.fromfile(img_path, dtype=np.uint8), -1)    
            if pred_out is None:
                pred_out = Image.open(img_path).convert('RGB')
        else: 
            pred_out = cv2.imread(pred_output_img)
            b,g,r = cv2.split(pred_out)
            pred_out = cv2.merge([r,g,b]) 
            # pred_out = cv2.imdecode(np.fromfile(pred_output_img, dtype=np.uint8), -1)
            if pred_out is None:
                pred_out = Image.open(pred_output_img).convert('RGB')
        pred_out = cv2.cvtColor(np.asarray(pred_out), cv2.COLOR_RGB2BGR)
        
        x, y, w, h = p["bbox"]
        x, y, w, h = int(x), int(y), int(w), int(h)
        x2, y2 = x + w, y + h
        if float(score) >= 0.1:
            cv2.rectangle(pred_out, (x, y), (x2, y2), (0, 255, 0), thickness=2) # green
            cv2.putText(pred_out, "{:.3f} {}".format(score, category),(x + 5, y), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,127,0), 2)
        cv2.imwrite(pred_output_img, pred_out)
    logging.info("Prediction done.")

def draw_box(gt_data, pred_data, clas, threshold, draw=True):
    if draw == True:
        gt_info = gt_data
        mapping = json.load(open('mapping_dirs/studio_image_id_mapping.json'))
        output_dir = "draw_images_output/{}/{}/".format(clas, threshold)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        # draw groundtruth
        root_dir = os.getcwd()
        draw_groundtruth(gt_info, root_dir, output_dir, mapping)
        
        # draw predictions
        pred_info = pred_data
        draw_predictions(pred_info, root_dir, output_dir, mapping)