import argparse

from .general import save_json


def merge_bbox(gt, pre_bbox):
    merge_results = dict()

    merge_results['gt'] = gt
    merge_results['bbox'] = pre_bbox

    return merge_results


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Start evaluation.')
    parser.add_argument('--gt_json', type=str, help='groundtruth absolute path', default='')
    parser.add_argument('--pred_json', type=str, help='prediction absolute path', default='')
    args = parser.parse_args()

    groundtruth_json = args.gt_json
    prediction_json = args.pred_json

    results = merge_bbox(groundtruth_json, prediction_json)
    save_json(results, 'prediction_dirs/eval_details.json')

    