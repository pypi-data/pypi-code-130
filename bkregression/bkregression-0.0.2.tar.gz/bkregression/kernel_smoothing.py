import torch
from ax.service.ax_client import AxClient
from tqdm import tqdm
import logging

class KernelRegressor():
    def __init__(self,X,y,kernel):
        self.X = X
        self.y = y
        self.kernel = kernel
        self.regularization_constant = 0.5

    def fit(self,iterations=50,verbose=True):
        def evaluate(parameters):
            self.kernel.parameters = parameters
            l = self.likelihood(self.X,self.y).item()
            return {"fun": (l, 0.0)}

        logger = logging.getLogger("ax")
        logger.setLevel(level=logging.WARNING)

        ax_client = AxClient(verbose_logging=False)
        params = self.kernel._create_parameters_ax()
        ax_client.create_experiment(
            name="Fit BKR",
            parameters=params,
            objective_name="fun",
            minimize=True,  # Optional, defaults to False.
        )

        if verbose:
            for i in range(iterations):
                parameters, trial_index = ax_client.get_next_trial()
                # Local evaluation here can be replaced with deployment to external system.
                ax_client.complete_trial(trial_index=trial_index, raw_data=evaluate(parameters))
                best_parameters, _ = ax_client.get_best_parameters()
                print("{}/{}\t Evaluation parameters: {}\t Best parameters: {}".format(i+1,iterations,parameters,best_parameters))

        else:
            for i in tqdm(range(iterations)):
                parameters, trial_index = ax_client.get_next_trial()
                # Local evaluation here can be replaced with deployment to external system.
                ax_client.complete_trial(trial_index=trial_index, raw_data=evaluate(parameters))
        
        best_parameters, _ = ax_client.get_best_parameters()
        self.kernel.parameters = best_parameters


    def __call__(self,Xq):
        print("####Final Parameters############")
        for p in list(self.kernel.parameters.keys()):
            print(p,": ",self.kernel.parameters[p])
        print("################################")
        yq, yq_std = self.kernel_smoothing(self.X,self.y,Xq)
        yq = yq.detach()
        yq_std = yq_std.detach()
        return yq, yq_std
    
    def likelihood(self,x,y):
        if len(x.shape)<2:
            x = x.reshape(1,-1)
        kernel_mat = self.kernel(x,x)
        mean = y.reshape((1,-1)) @ kernel_mat
        mean = mean.squeeze()
        std = self.get_std(y,mean,mean,kernel_mat)
        dist = torch.distributions.Normal(mean,std)
        log_probs = dist.log_prob(y)
        # regularization_term = ((1/(2*torch.Tensor(list(kernel.parameters.values()))**2))**2).sum()
        regularization_term = ((1/torch.Tensor(list(self.kernel.parameters.values())))**2).sum()
        result = -log_probs.mean()+self.regularization_constant*regularization_term #(1/(2*kernel.parameters["scale"]**2))**2    #add to sum of all parameters eventually
        return result

    def kernel_smoothing(self,x,y,xq):
        if len(x.shape)<2:
            x = x.reshape(1,-1)
            xq = xq.reshape(1,-1)
        
        #query points
        kernel_mat = self.kernel(x,xq)
        smoothed_points = y.reshape((1,-1)) @ kernel_mat
        smoothed_points = smoothed_points.squeeze()

        #data points
        kernel_mat_dp = self.kernel(x,x)
        smoothed_points_dp = y.reshape((1,-1)) @ kernel_mat_dp
        smoothed_points_dp = smoothed_points_dp.squeeze()

        #get std
        std = self.get_std(y,smoothed_points,smoothed_points_dp,kernel_mat)
        # log_probs = likelihood(x,y,kernel_function,distance_function,scale)
        return smoothed_points, std

    def get_std(self,y,yq,y_dp,kernel_mat,eps=1e-06):
        N = y.shape[0]
        std = torch.zeros_like(yq)
        # for i in range(std.shape[0]):
        #     std[i] = torch.sqrt((kernel_mat[:,i] @ (y-y_dp)**2)/((N-1)/N)) + eps
        std = torch.sqrt((kernel_mat.T @ (y-y_dp)**2)/((N-1)/N)) + eps
        # for i in range(std.shape[0]):
            # std[i] = torch.sqrt((kernel_mat[:,i] @ (y-yq[i])**2)/((N-1)/N)) + eps
        return std


