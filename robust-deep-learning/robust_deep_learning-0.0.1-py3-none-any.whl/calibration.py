from .tools import get_outputs_labels_and_metrics
from .metrics import ECELoss
import scipy.optimize as opt
import torch
import numpy


def calibrate_temperature(model_last_layer, model, loader, optimize="ECE"):
    print("Calibrating...")

    results = get_outputs_labels_and_metrics(model, loader)

    #calibrate_temperature_from_outputs(model_last_layer, results["outputs"], optimize=optimize)

    if optimize == "ECE":
        ece_criterion = ECELoss()
     
        def ece_eval(temperature):
            #loss = ece_criterion.loss(logits.numpy()/temperature,labels.numpy(),15)
            #loss = ece_criterion.loss(logits.cpu().numpy()/temperature,labels.cpu().numpy(),15)
            loss = ece_criterion.loss(results["outputs"].cpu().numpy()/temperature, results["labels"].cpu().numpy(),15)
            return loss
        temperature_for_min, min_value, _ = opt.fmin_l_bfgs_b(ece_eval, numpy.array([1.0]), approx_grad=True, bounds=[(0.001,100)])
        #print("\n################################")
        #print(metric_to_optimize, min_value)
        #print("Temperature", temperature_for_min[0])
        #print("################################")
        temperature_for_min = temperature_for_min[0]
        model_last_layer.temperature.data = torch.tensor([temperature_for_min]).to(torch.device('cuda')) 
    elif optimize == "NONE":
        temperature_for_min = 1
        model_last_layer.temperature = temperature_for_min

    print("Calibrated!!!")

    """
    elif metric_to_optimize == "NLL":
        model_last_layer.temperature = torch.nn.Parameter(torch.tensor([1.0]), requires_grad=True)
        #def nll_eval(temperature):
        #    loss = nll_criterion(logits/temperature,labels).item()
        #    #loss = nll_criterion(logits.cpu().numpy()/temperature,labels).item()
        #    return loss
        #temperature_for_min, min_value, _ = opt.fmin_l_bfgs_b(nll_eval, np.array([1.0]), approx_grad=True, bounds=[(0.001,100)])
        ##temperature_for_min, min_value, _ = opt.fmin_l_bfgs_b(nll_eval, np.array([1.0]), bounds=[(0.001,100)])
        optimizer = optim.LBFGS([model_last_layer.temperature], lr=0.001, max_iter=1000, line_search_fn="strong_wolfe")
        def nll_eval(temperature):
            loss = nll_criterion(logits/temperature, labels)
            loss.backward()
            return loss
        optimizer.step(nll_eval)
        model_last_layer.temperature = model_last_layer.temperature.item()
    """

