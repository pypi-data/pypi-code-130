import torch
import numpy
from tqdm import tqdm
from .general import get_outputs_labels_and_metrics
from .scores import get_scores

def get_thresholds_from_scores(scores):
    print("====>>>> getting thresholds <<<<====")
    thresholds = torch.Tensor(25)

    """
    with torch.no_grad():
        for inputs, targets in loader:
            logits = model(inputs)
            #scores = model_classifier.scores(logits).detach().cpu().numpy()
            scores = get_scores(logits, score_type=score_type).detach().cpu().numpy()

            if accumulated_scores is None:
                accumulated_scores = scores
            else:
                accumulated_scores = numpy.concatenate((accumulated_scores, scores), axis=0)

            #accumulated_batches += 1
            #if accumulated_batches == batches_to_accumulate:
            #    #partition_index = 0 if partition == "train" else 1
            #    for index, percentile in enumerate([0, 0.1, 0.2, 0.3, 0.4, 0.5, 1, 2, 3, 4, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 60, 70, 80, 90, 100]):
            #        #model_classifier.precomputed_thresholds[partition_index, index] = numpy.percentile(accumulated_scores, percentile)
            #        thresholds[index] = numpy.percentile(accumulated_scores, percentile)
            #    accumulated_scores = None
            #    accumulated_batches = 0

    for index, percentile in enumerate([0, 0.1, 0.2, 0.3, 0.4, 0.5, 1, 2, 3, 4, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 60, 70, 80, 90, 100]):
        thresholds[index] = numpy.percentile(accumulated_scores, percentile)
    """

    thresholds = {}
    #for index, percentile in enumerate([0, 0.1, 0.2, 0.3, 0.4, 0.5, 1, 2, 3, 4, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 60, 70, 80, 90, 100]):
    for percentile in tqdm([0, 0.1, 0.2, 0.3, 0.4, 0.5, 1, 2, 3, 4, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 60, 70, 80, 90, 100]):
        #thresholds[index] = numpy.percentile(scores, percentile)
        thresholds[str(percentile/100)] = numpy.percentile(scores, percentile)

    #return thresholds
    results = {}
    results['score_type'] = scores['type']
    results['values'] = thresholds
    return results


def get_thresholds(model, in_data_val_loader, score_type):
    # In the training loop, add the line of code below for preprocessing before forwarding.
    results = get_outputs_labels_and_metrics(model, in_data_val_loader)
    in_data_scores = get_scores(results["outputs"], score_type)

    return get_thresholds_from_scores(in_data_scores)

