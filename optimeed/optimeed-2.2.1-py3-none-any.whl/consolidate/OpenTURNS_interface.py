from .sensitivity_analysis import SensitivityAnalysis_LibInterface
import openturns as ot
from typing import List
import numpy as np
import math
from optimeed.core.collection import ListDataStruct_Interface


class LiveChaosCollection(ListDataStruct_Interface):
    """Class for live-fitting a PCE, mimicking the behaviour of a collection so that it can be used with LinkDataGraph"""

    def __init__(self, theSensitivityParameters, theCollection):
        self.fitted_chaos = dict()

        self.theSensitivityParameters = theSensitivityParameters
        self.theCollection = theCollection

        inputs = [theCollection.get_list_attributes("device.{}".format(optivariable.get_attribute_name()))
                  for optivariable in theSensitivityParameters.get_optivariables()]
        self.inputs = list(zip(*inputs))
        self.updateMethods = set()

    def _update_children(self):
        for updateMethod in self.updateMethods:
            updateMethod()

    def add_update_method(self, childObject):
        self.updateMethods.add(childObject)

    def save(self, filename):
        """Save the datastructure to filename"""
        pass

    @staticmethod
    def load(filename, **kwargs):
        pass

    def clone(self, filename):
        """Clone the datastructure to a new location"""
        raise NotImplementedError("Polynomial expansion should not be used for that")

    def add_data(self, data_in):
        raise NotImplementedError("Polynomial expansion should not be used for that")

    def get_data_at_index(self, index):
        raise NotImplementedError("Polynomial expansion should not be used for that")

    def get_data_generator(self):
        return
        yield
        # raise NotImplementedError("Polynomial expansion should not be used for that")

    def delete_points_at_indices(self, indices):
        raise NotImplementedError("Polynomial expansion should not be used for that")

    def get_nbr_elements(self):
        raise NotImplementedError("Polynomial expansion should not be used for that")

    def extract_collection_from_indices(self, theIndices):
        raise NotImplementedError("Polynomial expansion should not be used for that")

    def get_list_attributes(self, attributeName):
        """Returns the interpolation of original collection objectives 'attributeName'.
        If the fit has not been performed, fit it.

        :param attributeName:
        :return:
        """
        if not attributeName:
            return []

        SA_chaos = self.get_chaos(attributeName)
        objectives = self.theCollection.get_list_attributes(attributeName)
        return SA_chaos.evaluate_metamodel(self.inputs, SA_chaos.get_metamodel(self.theSensitivityParameters, objectives))

    def refresh_attribute(self, attributeName):
        if attributeName not in self.fitted_chaos:
            self.fitted_chaos[attributeName] = SensitivityAnalysis_OpenTURNS_Chaos()
            self._update_children()

    def set_degree(self, attributeName, degree):
        self.refresh_attribute(attributeName)
        self.fitted_chaos[attributeName].set_fit_degree(degree)

    def get_chaos(self, attributeName):
        self.refresh_attribute(attributeName)
        return self.fitted_chaos[attributeName]

    def __str__(self):
        return "Chaos Expansion Fit"


class SensitivityAnalysis_OpenTURNS_Chaos(SensitivityAnalysis_LibInterface):
    """Polynomial chaos expansions based.
    Sobol indices are computed from metamodel."""

    def __init__(self):
        super().__init__()
        self.chaosresult = None
        self.objectives_fitted = list()
        self.degree_fitted = 1
        self.fit_performed = False

    def sample_sobol(self, theOptimizationVariables, N):
        distributionList = [ot.Uniform(variable.get_min_value(), variable.get_max_value()) for variable in theOptimizationVariables]
        distribution = ot.ComposedDistribution(distributionList)
        inputDesign = ot.SobolIndicesExperiment(distribution, N, True)
        return inputDesign.generate()

    # def get_summary(self, theSensitivityParameters, theObjectives):
    #     chaosSI = ot.FunctionalChaosSobolIndices(self._get_chaos(theSensitivityParameters, theObjectives))
    #     print(chaosSI.summary())

    def get_sobol_S1(self, theSensitivityParameters, theObjectives):
        chaosSI = ot.FunctionalChaosSobolIndices(self.get_chaos(theSensitivityParameters, theObjectives))
        return [chaosSI.getSobolIndex(i) for i in range(len(theSensitivityParameters.get_optivariables()))]

    def get_sobol_S1conf(self, theSensitivityParameters, theObjectives):
        """Not available using Chaos Expansion"""
        return [np.nan]*len(theSensitivityParameters.get_optivariables())

    def get_sobol_ST(self, theSensitivityParameters, theObjectives):
        chaosSI = ot.FunctionalChaosSobolIndices(self.get_chaos(theSensitivityParameters, theObjectives))
        return [chaosSI.getSobolTotalIndex(i) for i in range(len(theSensitivityParameters.get_optivariables()))]

    def get_sobol_STconf(self, theSensitivityParameters, theObjectives):
        """Not available using Chaos Expansion"""
        return [np.nan] * len(theSensitivityParameters.get_optivariables())

    def get_sobol_S2(self, theSensitivityParameters, theObjectives):
        """Not available using Chaos Expansion (yet)"""
        N = len(theSensitivityParameters.get_optivariables())
        a = np.empty((N, N,))
        a[:] = np.nan
        return a

    def _end_training_index(self, outputs):
        return int(0.7*len(outputs))

    def get_chaos(self, theSensitivityParameters, theObjectives):
        end_training = self._end_training_index(theObjectives)
        subset_objectives = theObjectives[0:end_training]
        subset_inputs = theSensitivityParameters.get_paramvalues()[0:end_training]

        if not self.fit_performed or self.objectives_fitted != subset_objectives:  # Perform the fit
            variables = theSensitivityParameters.get_optivariables()
            marginals = [ot.Uniform(variable.get_min_value(), variable.get_max_value()) for variable in variables]
            d = ot.ComposedDistribution(marginals)
            polynomials = [ot.StandardDistributionPolynomialFactory(m) for m in marginals]
            basis = ot.OrthogonalProductPolynomialFactory(polynomials)
            total_size = basis.getEnumerateFunction().getStrataCumulatedCardinal(self.degree_fitted)
            adaptive = ot.FixedStrategy(basis, total_size)
            chaosalgo = ot.FunctionalChaosAlgorithm(subset_inputs, [[obji] for obji in subset_objectives], d, adaptive)

            chaosalgo.run()
            self.chaosresult = chaosalgo.getResult()
            self.objectives_fitted = subset_objectives
            self.fit_performed = True
        return self.chaosresult

    def get_metamodel(self, theSensitivityParameters, theObjectives):
        return self.get_chaos(theSensitivityParameters, theObjectives).getMetaModel()

    def get_metamodel_as_python_method(self, theSensitivityParameters, theObjectives):
        arg_name = "theDevice"
        theStr = "def mymetamodel({}):\n".format(arg_name)

        for k, optiVariable in enumerate(theSensitivityParameters.get_optivariables()):
            a, b, n = optiVariable.get_min_value(), optiVariable.get_max_value(), optiVariable.get_attribute_name()
            T1 = 2/(b-a)
            T2 = -(a+b)/(b-a)
            if T2 < 0:
                theStr += "    x{} = {}*{}.{} - {}\n".format(k, T1, arg_name, n, -T2)
            else:
                theStr += "    x{} = {}*{}.{} + {}\n".format(k, T1, arg_name, n, T2)
        theComposedMetamodel = str(self.get_chaos(theSensitivityParameters, theObjectives).getComposedMetaModel())
        theStr += "    return {}\n".format(theComposedMetamodel.replace("^", "**"))
        return theStr

    @staticmethod
    def evaluate_metamodel(inputs, theMetaModel):
        return np.array(theMetaModel(np.array(inputs))).flatten()

    def set_fit_degree(self, degree):
        self.degree_fitted = degree
        self.fit_performed = False

    def check_goodness_of_fit(self, theSensitivityParameters, theObjectives):
        end_training = self._end_training_index(theObjectives)
        inputs = theSensitivityParameters.get_paramvalues()[end_training:]
        outputs_real = theObjectives[end_training:]
        outputs = [[obji] for obji in outputs_real]
        theMetaModel = self.get_metamodel(theSensitivityParameters, theObjectives)

        val = ot.MetaModelValidation(inputs, outputs, theMetaModel)
        Q2 = val.computePredictivityFactor()[0]
        outputs_model = self.evaluate_metamodel(inputs, theMetaModel)
        return Q2, outputs_real, outputs_model


class SensitivityAnalysis_OpenTURNS(SensitivityAnalysis_LibInterface):
    degree_fitted: int
    coefficients: List[List[float]]

    def __init__(self):
        super().__init__()
        self.SA = None
        self.theObjectives = list()

    def _raw_sample(self, theOptimizationVariables, N):
        distributionList = [ot.Uniform(variable.get_min_value(), variable.get_max_value()) for variable in theOptimizationVariables]
        distribution = ot.ComposedDistribution(distributionList)
        return ot.SobolIndicesExperiment(distribution, N, True).generate()

    def sample_sobol(self, theOptimizationVariables, N):
        return np.array(self._raw_sample(theOptimizationVariables, N))

    def get_sobol_S1(self, theSensitivityParameters, theObjectives):
        return self._get_SA(theSensitivityParameters, theObjectives).getFirstOrderIndices()

    def get_sobol_S1conf(self, theSensitivityParameters, theObjectives):
        intervals = self._get_SA(theSensitivityParameters, theObjectives).getFirstOrderIndicesInterval()
        lower_bounds = intervals.getLowerBound()
        upper_bounds = intervals.getUpperBound()
        return [up - (low+up)/2 for low, up in zip(lower_bounds, upper_bounds)]

    def get_sobol_ST(self, theSensitivityParameters, theObjectives):
        return self._get_SA(theSensitivityParameters, theObjectives).getTotalOrderIndices()

    def get_sobol_STconf(self, theSensitivityParameters, theObjectives):
        intervals = self._get_SA(theSensitivityParameters, theObjectives).getTotalOrderIndicesInterval()
        lower_bounds = intervals.getLowerBound()
        upper_bounds = intervals.getUpperBound()
        return [up - (low+up)/2 for low, up in zip(lower_bounds, upper_bounds)]

    def get_sobol_S2(self, theSensitivityParameters, theObjectives):
        return np.matrix(self._get_SA(theSensitivityParameters, theObjectives).getSecondOrderIndices())

    def _get_SA(self, theSensitivityParameters, theObjectives):
        if self.theObjectives != theObjectives or self.SA is None:
            self._analyze(theSensitivityParameters, theObjectives)
        return self.SA

    def _analyze(self, theSensitivityParameters, theObjectives):
        nb_params = len(theSensitivityParameters.get_optivariables())

        # Size of sample
        if nb_params == 2:
            eval_per_sample = (2 + nb_params)
        else:
            eval_per_sample = (2 + 2*nb_params)
        max_N = int(math.floor(len(theObjectives) / eval_per_sample))
        objectives = np.array(theObjectives[0:max_N * eval_per_sample])
        params = np.array(theSensitivityParameters.get_paramvalues()[0:max_N * eval_per_sample])
        self.SA = ot.SaltelliSensitivityAlgorithm(params, [[obji] for obji in objectives], max_N)
