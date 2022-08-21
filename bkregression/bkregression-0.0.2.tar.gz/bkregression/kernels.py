import torch
import math

class BaseKernel(object):
    def __init__(self) -> None:
        super().__init__()
        pass

    def _create_parameters_ax(self) -> list:
        """Returns a list for the parameter configuration needed for AX.

        Returns:
            list: List of dictionaries used to setup hyperparameter search with AX.
        """
        parameter_list = []
        for p in self.parameters.keys():
            if self.types[p] == "range":
                p_dict = {"name":p, "type": "range", "bounds":self.values[p], "value_type":"float"}
            elif self.types[p] == "choice":
                p_dict = {"name":p, "type": "choice", "values":self.values[p], "value_type":"float"}
            elif self.types[p] == "fixed": 
                p_dict = {"name":p, "type": "fixed", "value":self.values[p], "value_type":"float"}
            parameter_list.append(p_dict)
        
        return parameter_list

class RBF(BaseKernel):
    def __init__(self,scale:float=None,scale_lower_bound:float=0.001,scale_upper_bound:float=100.0) -> None:
        """Initializes the basic parameters and search bounds for RBF kernel.

        Args:
            scale (float, optional): Prior value for the kernel scale length. Only used if not optimized during fitting. Defaults to 1.0.
            scale_lower_bound (float, optional): Lower bound of scale length for optimization during fitting. Defaults to 0.001.
            scale_upper_bound (float, optional): Lower bound of scale length for optimization during fitting. Defaults to 100.0.
        """
        super().__init__()

        self.parameters = {"scale":scale}
        self.types = {"scale":"range" if scale is None else "fixed"}
        self.values = {"scale":[scale_lower_bound,scale_upper_bound] if scale is None else scale}
    
    def __call__(self,values:torch.Tensor,query:torch.Tensor) -> torch.Tensor:
        scale = self.parameters["scale"]
        dim1a = values.shape[-1]
        dim1b = values.shape[-2]
        dim2a = query.shape[-1]
        dim2b = query.shape[-2]
        values = (values.reshape(dim1b,dim1a,1)).permute((1,2,0))
        query = (query.reshape(dim2b,dim2a,1)).permute((2,1,0))
        diff_sq = torch.pow(values-query,2)
        sum_diff_sq = torch.sum(diff_sq,dim=2)
        d = torch.sqrt(sum_diff_sq)
        # kernel_mat = torch.exp(-1/scale*d**2)
        # kernel_mat = torch.exp(-d**2/(2*scale**2))
        kernel_mat = torch.exp(-1/scale*d**2)
        kernel_mat = kernel_mat/torch.sum(kernel_mat,axis=0)
        return kernel_mat

class Matern(BaseKernel):
    def __init__(self,rho:float=None,rho_lower_bound:float=0.001,rho_upper_bound=100.0,nu:float=None) -> None:
        super().__init__()

        self.allowed_nu = [0.5,1.5,2.5]

        if nu not in self.allowed_nu+[None]:
            raise NotImplementedError

        self.parameters = {"rho":rho, "nu":nu}
        self.types = {"rho":"range" if rho is None else "fixed","nu":"choice" if nu is None else "fixed"}
        self.values = {"rho":[rho_lower_bound,rho_upper_bound] if rho is None else rho,"nu":self.allowed_nu if nu is None else nu}  #choices of nu are made based on easy calculation for matern covariance function
        
        

    def __call__(self,values:torch.Tensor,query:torch.Tensor) -> torch.Tensor:
        if self.parameters["nu"] not in self.allowed_nu:
            raise NotImplementedError
        
        rho = self.parameters["rho"]
        nu = self.parameters["nu"]
        dim1a = values.shape[-1]
        dim1b = values.shape[-2]
        dim2a = query.shape[-1]
        dim2b = query.shape[-2]
        values = (values.reshape(dim1b,dim1a,1)).permute((1,2,0))
        query = (query.reshape(dim2b,dim2a,1)).permute((2,1,0))
        diff_sq = torch.pow(values-query,2)
        sum_diff_sq = torch.sum(diff_sq,dim=2)
        d = torch.sqrt(sum_diff_sq)

        if nu==0.5:
            kernel_mat = torch.exp(-d/rho)

        elif nu==1.5:
            kernel_mat = (1+math.sqrt(3)*d/rho)*torch.exp(-math.sqrt(3)*d/rho)
        
        elif nu==2.5:
            kernel_mat = (1+(math.sqrt(5)*d)/(rho)+(5*d**2)/(3*rho**2))*torch.exp(-math.sqrt(5)*d/rho)
        
        else:
            raise NotImplementedError

        kernel_mat = kernel_mat/torch.sum(kernel_mat,axis=0)
        return kernel_mat

class Exponential(BaseKernel):
    def __init__(self,scale:float=None,scale_lower_bound:float=0.001,scale_upper_bound:float=100.0) -> None:
        """Initializes the basic parameters and search bounds for exponential kernel.

        Args:
            scale (float, optional): Prior value for the kernel scale length. Only used if not optimized during fitting. Defaults to 1.0.
            scale_lower_bound (float, optional): Lower bound of scale length for optimization during fitting. Defaults to 0.001.
            scale_upper_bound (float, optional): Lower bound of scale length for optimization during fitting. Defaults to 100.0.
        """
        super().__init__()

        self.parameters = {"scale":scale}
        self.types = {"scale":"range" if scale is None else "fixed"}
        self.values = {"scale":[scale_lower_bound,scale_upper_bound] if scale is None else scale}
    
    def __call__(self,values:torch.Tensor,query:torch.Tensor) -> torch.Tensor:
        scale = self.parameters["scale"]
        dim1a = values.shape[-1]
        dim1b = values.shape[-2]
        dim2a = query.shape[-1]
        dim2b = query.shape[-2]
        values = (values.reshape(dim1b,dim1a,1)).permute((1,2,0))
        query = (query.reshape(dim2b,dim2a,1)).permute((2,1,0))
        diff_sq = torch.pow(values-query,2)
        sum_diff_sq = torch.sum(diff_sq,dim=2)
        d = torch.sqrt(sum_diff_sq)
        kernel_mat = torch.exp(-d/scale)
        kernel_mat = kernel_mat/torch.sum(kernel_mat,axis=0)
        return kernel_mat


class GammaExponential(BaseKernel):
    def __init__(self,scale:float=None,scale_lower_bound:float=0.001,scale_upper_bound:float=100.0,gamma:float=1.0,gamma_lower_bound:float=0.001,gamma_upper_bound:float=2.0) -> None:
        """Initializes the basic parameters and search bounds for gamma-exponential kernel.

        Args:
            scale (float, optional): Prior value for the kernel scale length. Only used if not optimized during fitting. Defaults to 1.0.
            scale_lower_bound (float, optional): Lower bound of scale length for optimization during fitting. Defaults to 0.001.
            scale_upper_bound (float, optional): Lower bound of scale length for optimization during fitting. Defaults to 100.0.
            gamma (float, optional): Prior value for the kernel exponent. Only used if not optimized during fitting. Defaults to 1.0.
            gamma_lower_bound (float, optional): Lower bound of kernel exponent for optimization during fitting. Defaults to 0.001.
            gamma_upper_bound (float, optional): Lower bound of kernel exponent for optimization during fitting. Defaults to 2.0.
        """
        super().__init__()

        self.parameters = {"scale":scale,"gamma":gamma}
        self.types = {"scale":"range" if scale is None else "fixed","gamma":"range" if gamma is None else "fixed"}
        self.values = {"scale":[scale_lower_bound,scale_upper_bound] if scale is None else scale,"gamma":[gamma_lower_bound,gamma_upper_bound] if gamma is None else gamma}
    
    def __call__(self,values:torch.Tensor,query:torch.Tensor) -> torch.Tensor:
        scale = self.parameters["scale"]
        gamma = self.parameters["gamma"]
        dim1a = values.shape[-1]
        dim1b = values.shape[-2]
        dim2a = query.shape[-1]
        dim2b = query.shape[-2]
        values = (values.reshape(dim1b,dim1a,1)).permute((1,2,0))
        query = (query.reshape(dim2b,dim2a,1)).permute((2,1,0))
        diff_sq = torch.pow(values-query,2)
        sum_diff_sq = torch.sum(diff_sq,dim=2)
        d = torch.sqrt(sum_diff_sq)
        kernel_mat = torch.exp(-(d/scale)**gamma)
        kernel_mat = kernel_mat/torch.sum(kernel_mat,axis=0)
        return kernel_mat

class RationalQuadratic(BaseKernel):
    def __init__(self,scale:float=None,scale_lower_bound:float=0.001,scale_upper_bound:float=100.0,alpha:float=1.0,alpha_lower_bound:float=0.001,alpha_upper_bound:float=100.0) -> None:
        """Initializes the basic parameters and search bounds for rational quadratic kernel.

        Args:
            scale (float, optional): Prior value for the kernel scale length. Only used if not optimized during fitting. Defaults to 1.0.
            scale_lower_bound (float, optional): Lower bound of scale length for optimization during fitting. Defaults to 0.001.
            scale_upper_bound (float, optional): Lower bound of scale length for optimization during fitting. Defaults to 100.0.
            alpha (float, optional): Prior value for the alpha parameter. Only used if not optimized during fitting. Defaults to 1.0.
            alpha_lower_bound (float, optional): Lower bound of the alpha parameter for optimization during fitting. Defaults to 0.001.
            alpha_upper_bound (float, optional): Lower bound of the alpha parameter for optimization during fitting. Defaults to 100.0.
        """
        super().__init__()

        self.parameters = {"scale":scale,"alpha":alpha}
        self.types = {"scale":"range" if scale is None else "fixed","alpha":"range" if alpha is None else "fixed"}
        self.values = {"scale":[scale_lower_bound,scale_upper_bound] if scale is None else scale,"alpha":[alpha_lower_bound,alpha_upper_bound] if alpha is None else alpha}
    
    def __call__(self,values:torch.Tensor,query:torch.Tensor) -> torch.Tensor:
        scale = self.parameters["scale"]
        alpha = self.parameters["alpha"]
        dim1a = values.shape[-1]
        dim1b = values.shape[-2]
        dim2a = query.shape[-1]
        dim2b = query.shape[-2]
        values = (values.reshape(dim1b,dim1a,1)).permute((1,2,0))
        query = (query.reshape(dim2b,dim2a,1)).permute((2,1,0))
        diff_sq = torch.pow(values-query,2)
        sum_diff_sq = torch.sum(diff_sq,dim=2)
        d = torch.sqrt(sum_diff_sq)
        kernel_mat = (1+(d**2)/(2*scale**2*alpha))**(-alpha)
        kernel_mat = kernel_mat/torch.sum(kernel_mat,axis=0)
        return kernel_mat

        