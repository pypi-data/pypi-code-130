from faster_coco_eval.faster_coco_eval import COCO

def get_classes_and_imgs(gt_json):
    names = {}
    # get categories 
    coco_api = COCO(gt_json)
    cat_ids = sorted(coco_api.getCatIds())
    cats = coco_api.loadCats(cat_ids)
    classes = [c["name"] for c in sorted(cats, key=lambda x: x["id"])]
    img_ids = coco_api.getImgIds()
    img_len = len(img_ids)

    for c in cats:
        names[c["id"]] = c["name"]

    return names, classes, img_len, img_ids