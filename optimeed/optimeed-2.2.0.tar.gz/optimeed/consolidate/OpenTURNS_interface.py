from .sensitivity_analysis import SensitivityAnalysis_LibInterface
import openturns as ot
import openturns.viewer as viewer
from matplotlib import pylab as plt
from typing import List
import numpy as np
import math


class SensitivityAnalysis_OpenTURNS_Chaos(SensitivityAnalysis_LibInterface):
    """Polynomial chaos expansions based.
    Sobol indices are computed from metamodel."""

    def __init__(self):
        super().__init__()
        self.chaosresult = None
        self.objectives_fitted = list()
        self.degree_fitted = 1
        self.fit_performed = False
        self.view = None

    def sample_sobol(self, theOptimizationVariables, N):
        distributionList = [ot.Uniform(variable.get_min_value(), variable.get_max_value()) for variable in theOptimizationVariables]
        distribution = ot.ComposedDistribution(distributionList)
        inputDesign = ot.SobolIndicesExperiment(distribution, N, True)
        return inputDesign.generate()

    # def get_summary(self, theSensitivityParameters, theObjectives):
    #     chaosSI = ot.FunctionalChaosSobolIndices(self._get_chaos(theSensitivityParameters, theObjectives))
    #     print(chaosSI.summary())

    def get_sobol_S1(self, theSensitivityParameters, theObjectives):
        chaosSI = ot.FunctionalChaosSobolIndices(self._get_chaos(theSensitivityParameters, theObjectives))
        return [chaosSI.getSobolIndex(i) for i in range(len(theSensitivityParameters.get_optivariables()))]

    def get_sobol_S1conf(self, theSensitivityParameters, theObjectives):
        """Not available using Chaos Expansion"""
        return [np.nan]*len(theSensitivityParameters.get_optivariables())

    def get_sobol_ST(self, theSensitivityParameters, theObjectives):
        chaosSI = ot.FunctionalChaosSobolIndices(self._get_chaos(theSensitivityParameters, theObjectives))
        return [chaosSI.getSobolTotalIndex(i) for i in range(len(theSensitivityParameters.get_optivariables()))]

    def get_sobol_STconf(self, theSensitivityParameters, theObjectives):
        """Not available using Chaos Expansion"""
        return [np.nan] * len(theSensitivityParameters.get_optivariables())

    def get_sobol_S2(self, theSensitivityParameters, theObjectives):
        """Not available using Chaos Expansion"""
        N = len(theSensitivityParameters.get_optivariables())
        a = np.empty((N, N,))
        a[:] = np.nan
        return a

    def _end_training_index(self, outputs):
        return int(0.7*len(outputs))

    def _get_chaos(self, theSensitivityParameters, theObjectives):
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
        return self.chaosresult

    def _get_metamodel(self, theSensitivityParameters, theObjectives):
        return self._get_chaos(theSensitivityParameters, theObjectives).getMetaModel()

    def set_fit_degree(self, degree):
        self.degree_fitted = degree
        self.fit_performed = False

    def check_goodness_of_fit(self, theSensitivityParameters, theObjectives, hold=True):
        end_training = self._end_training_index(theObjectives)
        inputs = theSensitivityParameters.get_paramvalues()[end_training:]
        outputs = theObjectives[end_training:]
        outputs = [[obji] for obji in outputs]
        val = ot.MetaModelValidation(inputs, outputs, self._get_metamodel(theSensitivityParameters, theObjectives))
        Q2 = val.computePredictivityFactor()[0]
        graph = val.drawValidation()
        graph.setTitle("Q2=%.2f%%" % (Q2*100))
        view = viewer.View(graph)
        self.view = view
        plt.show(block=hold)


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

#
# chaosalgo.run()
# result = chaosalgo.getResult()
# metamodel = result.getMetaModel()
#
# # %%
# # Validation of the metamodel
# # ---------------------------
#
# # %%
# # In order to validate the metamodel, we generate a test sample.
#
# # %%
# n_valid = 1000
# distrib = ot.Uniform(0, 1)
# inputs = [np.random.random(2) for _ in range(n_valid)]
# outputTest = [mymethod(*inputTest) for inputTest in inputs]
# val = ot.MetaModelValidation(inputs, outputTest, metamodel)
# print(metamodel)
# Q2 = val.computePredictivityFactor()[0]
#
#
# # %%
# # The Q2 is very close to 1: the metamodel is excellent.
#
# # %%
# graph = val.drawValidation()
# graph.setTitle("Q2=%.2f%%" % (Q2*100))
# view = viewer.View(graph)
#
# sensitivityAnalysis = ot.FunctionalChaosSobolIndices(result)
# print(sensitivityAnalysis.summary())
#
# from optimeed.consolidate import SensitivityParameters
# theParameters = SensitivityParameters(inputs, variables, None, None, None)
# print(SALib_interface.analyse_sobol_create_array(theParameters, outputs.flatten()))
#
#
# plt.show()
#
# # %%
# # The metamodel has a good predictivity, since the points are almost on the first diagonal.
