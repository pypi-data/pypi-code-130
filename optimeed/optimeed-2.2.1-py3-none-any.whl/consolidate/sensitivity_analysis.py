import shutil
from abc import ABCMeta, abstractmethod
from optimeed.core import SaveableObject, AutosaveStruct, create_unique_dirname, SHOW_INFO, printIfShown, Performance_ListDataStruct
from typing import List
from .sensitivity_analysis_evaluation import evaluate
from optimeed.core import SingleObjectSaveLoad
from optimeed.core import getPath_workspace, SHOW_ERROR, order_lists
from optimeed.optimize import Real_OptimizationVariable
from multiprocessing import Pool
import math
import numpy as np
import os


_filename_sensitivityparams = "sensitivity_params.json"
_foldername_embarrassingly_parallel_results = "_jobs_results"
_filename_sensitivityresults = "sensitivity.json"


class SensitivityResults(SaveableObject):
    paramsToEvaluate: List[float]
    success: bool
    index: int

    def __init__(self):
        self.paramsToEvaluate = [0.0]
        self.device = None
        self.success = False
        self.index = 0

    def add_data(self, params, device, success, index):
        self.device = device
        self.success = success
        self.paramsToEvaluate = params
        self.index = index

    def get_additional_attributes_to_save(self):
        return ["device"]


class SensitivityParameters(SaveableObject):
    list_of_optimization_variables: List[Real_OptimizationVariable]
    param_values: List[List[float]]

    def __init__(self, param_values, list_of_optimization_variables, theDevice, theMathsToPhys, theCharacterization):
        """
        These are the parameters t
        :param list_of_optimization_variables: list of OptiVariables that are analyzed
        :param theDevice: /
        :param theMathsToPhys: /
        :param theCharacterization: /"""
        self.theDevice = theDevice
        self.theMathsToPhys = theMathsToPhys
        self.theCharacterization = theCharacterization
        self.list_of_optimization_variables = list_of_optimization_variables
        self.param_values = param_values

    def get_device(self):
        return self.theDevice

    def get_M2P(self):
        return self.theMathsToPhys

    def get_charac(self):
        return self.theCharacterization

    def get_optivariables(self):
        return self.list_of_optimization_variables

    def get_paramvalues(self):
        return self.param_values

    def get_additional_attributes_to_save(self):
        return ["theDevice", "theMathsToPhys", "theCharacterization"]


class SensitivityAnalysis_LibInterface(metaclass=ABCMeta):
    def __init__(self):
        pass

    @abstractmethod
    def sample_sobol(self, theOptimizationVariables, N):
        pass

    @abstractmethod
    def get_sobol_S1(self, theSensitivityParameters: SensitivityParameters, theObjectives):
        """
        Get first order sobol indices
        :param theSensitivityParameters: :class:`optimeed.consolidate.sensitivity_analysis.SensitivityParameters`
        :param theObjectives: array-like objective associated to evaluation, using Sobol sampling
        :return:
        """
        pass

    @abstractmethod
    def get_sobol_S1conf(self, theSensitivityParameters: SensitivityParameters, theObjectives):
        pass

    @abstractmethod
    def get_sobol_S2(self, theSensitivityParameters: SensitivityParameters, theObjectives):
        """
        Get second order sobol indices
        :param theSensitivityParameters: :class:`optimeed.consolidate.sensitivity_analysis.SensitivityParameters`
        :param theObjectives: array-like objective associated to evaluation, using Sobol sampling
        :return:
        """
        pass

    @abstractmethod
    def get_sobol_ST(self, theSensitivityParameters: SensitivityParameters, theObjectives):
        """
        Get total order sobol indices
        :param theSensitivityParameters: :class:`optimeed.consolidate.sensitivity_analysis.SensitivityParameters`
        :param theObjectives: array-like objective associated to evaluation, using Sobol sampling
        :return:
        """
        pass

    @abstractmethod
    def get_sobol_STconf(self, theSensitivityParameters: SensitivityParameters, theObjectives):
        pass

    def get_summary(self, theSensitivityParameters, objectives):
        """Display a summary of the sobol indices"""
        S1 = self.get_sobol_S1(theSensitivityParameters, objectives)
        S1conf = self.get_sobol_S1conf(theSensitivityParameters, objectives)
        ST = self.get_sobol_ST(theSensitivityParameters, objectives)
        STconf = self.get_sobol_STconf(theSensitivityParameters, objectives)

        nb_params = len(theSensitivityParameters.get_optivariables())
        _, ordered_S1 = order_lists(S1, list(range(nb_params)))
        _, ordered_ST = order_lists(ST, list(range(nb_params)))
        ordered_S1.reverse()
        ordered_ST.reverse()

        def format_array(permutations, S, Sconf, name):
            theStr = ''
            theStr += '─' * 120 + '\n'
            theStr += "{:^12}{:^14}{:^25}{:<}".format(*["Rank (" + name + ")", "Sobol value", "+- 95% conf", "Param name"]) + '\n'
            theStr += '─' * 120 + '\n'
            for i, map_index in enumerate(permutations):
                row = [i + 1, S[map_index], Sconf[map_index], theSensitivityParameters.get_optivariables()[map_index].get_attribute_name()]
                theStr += "{:^12}{:^14.3f}{:^25.3f}{}".format(*row) + '\n'
            theStr += '─' * 50 + '\n'
            theStr += "{:^12}{:^14.3f}{:^25}{:<}".format("SUM", sum(S), "", "") + '\n'
            return theStr

        S1_array = format_array(ordered_S1, S1, S1conf, "S1")
        ST_array = format_array(ordered_ST, ST, STconf, "ST")
        print(S1_array)
        print(ST_array)

    def get_convergence_S1(self, theSensitivityParameters: SensitivityParameters, objectives, stepsize=1):
        """
        Create dictionary for convergence plot - First order index

        :param theSensitivityParameters: class:`SensitivityParameters`
        :param objectives: array-like of objective
        :param stepsize: increments of sampling size
        :return: Dictionary
        """
        return self._get_convergence(self.get_sobol_S1, theSensitivityParameters, objectives, stepsize)

    def get_convergence_ST(self, theSensitivityParameters: SensitivityParameters, objectives, stepsize=1):
        """
        Create dictionary for convergence plot - Total order index

        :param theSensitivityParameters: class:`SensitivityParameters`
        :param objectives: array-like of objective
        :param stepsize: increments of sampling size
        :return: Dictionary
        """
        return self._get_convergence(self.get_sobol_ST, theSensitivityParameters, objectives, stepsize)

    @staticmethod
    def _get_convergence(method, theSensitivityParameters: SensitivityParameters, objectives, stepsize):
        opti_variables = theSensitivityParameters.get_optivariables()
        nb_params = len(opti_variables)

        max_nb_step = math.floor(len(objectives) / (2 * nb_params + 2))

        outputs = list()
        steps = list(range(2, max_nb_step, stepsize))
        for sample_size in steps:
            printIfShown("Doing {} over {}".format(sample_size, max_nb_step))
            outputs.append(method(theSensitivityParameters, np.array(objectives[0:sample_size * (2 * nb_params + 2)])))

        outputs_dict = dict()
        for i in range(nb_params):
            outputs_dict[i] = {'S': [output[i] for output in outputs],
                               'step': steps,
                               'name': opti_variables[i].get_attribute_name()}
        return outputs_dict


def _get_sensitivity_result(output):
    """Convert output of "evaluate" function to SensitivityResult"""
    result = SensitivityResults()
    result.add_data(output["x"], output["device"], output["success"], output["index"])
    return result


def _get_job_args(theSensitivityParameters, index):
    """Convert sensitivityparameters at index to args used in "evaluate" function"""
    return [theSensitivityParameters.get_paramvalues()[index], theSensitivityParameters.get_device(),
            theSensitivityParameters.get_M2P(), theSensitivityParameters.get_charac(), theSensitivityParameters.get_optivariables(), index]


def _find_missings(theSensitivityParameters, studyname):
    missings = list()
    for index, _ in enumerate(theSensitivityParameters.get_paramvalues()):
        saved_filename = os.path.join(getPath_workspace(), studyname, _foldername_embarrassingly_parallel_results, "{}.json".format(index))
        if not os.path.exists(saved_filename):
            missings.append(index)
    return missings


def prepare_embarrassingly_parallel_sensitivity(theSensitivityParameters, studyname):
    project_foldername = os.path.join(getPath_workspace(), studyname)
    foldername_tempfiles = os.path.join(project_foldername, _foldername_embarrassingly_parallel_results)
    shutil.rmtree(foldername_tempfiles, ignore_errors=True)
    os.makedirs(foldername_tempfiles)  # Also create project_foldername dir
    SingleObjectSaveLoad.save(theSensitivityParameters, os.path.join(project_foldername, _filename_sensitivityparams))
    printIfShown("Files created. There will be {} indices to evaluate".format(len(theSensitivityParameters.get_paramvalues())), SHOW_INFO)


def launch_embarrassingly_parallel_sensitivity(theSensitivityParameters, studyname, index):
    saved_filename = os.path.join(getPath_workspace(), studyname, _foldername_embarrassingly_parallel_results, "{}.json".format(index))
    if not os.path.exists(saved_filename):
        output = evaluate(_get_job_args(theSensitivityParameters, index))
        result = _get_sensitivity_result(output)
        SingleObjectSaveLoad.save(result, saved_filename)


def gather_embarrassingly_parallel_sensitivity(theSensitivityParameters, studyname):
    missings = _find_missings(theSensitivityParameters, studyname)
    if len(missings):
        printIfShown("Could not gather results yet, several parameters remain unevaluated:", SHOW_ERROR)
        printIfShown("{}".format(missings), SHOW_ERROR)
        exit(-1)

    results = Performance_ListDataStruct()

    for index, _ in enumerate(theSensitivityParameters.get_paramvalues()):
        saved_filename = os.path.join(getPath_workspace(), studyname, _foldername_embarrassingly_parallel_results, "{}.json".format(index))
        with open(saved_filename, 'r') as f:
            theStr = f.read()
        results.add_json_data(theStr)
    results.save(os.path.join(getPath_workspace(), studyname, _filename_sensitivityresults))


def evaluate_sensitivities(theSensitivityParameters: SensitivityParameters,
                           numberOfCores=2, studyname="sensitivity", indices_to_evaluate=None):
    """
    Evaluate the sensitivities

    :param theSensitivityParameters: class`~SensitivityParameters`
    :param numberOfCores: number of core for multicore evaluation
    :param studyname: Name of the study, that will be the subfolder name in workspace
    :param indices_to_evaluate: if None, evaluate all param_values, otherwise if list: evaluate subset of param_values defined by indices_to_evaluate
    :return: collection of class`~SensitivityResults`
    """
    myDataStruct = Performance_ListDataStruct()
    foldername = create_unique_dirname(os.path.join(getPath_workspace(), studyname))

    SingleObjectSaveLoad.save(theSensitivityParameters, os.path.join(foldername, _filename_sensitivityparams))
    # Start saving
    autosaveStruct = AutosaveStruct(myDataStruct, filename=os.path.join(foldername, _filename_sensitivityresults))
    autosaveStruct.start_autosave(timer_autosave=60*5)

    param_values = theSensitivityParameters.get_paramvalues()
    try:
        param_values = param_values.tolist()
    except AttributeError:
        pass

    if indices_to_evaluate is None:
        indices = list(range(len(param_values)))
    else:
        indices = indices_to_evaluate
        param_values = [param_values[index] for index in indices_to_evaluate]

    # create jobs
    jobs = [_get_job_args(theSensitivityParameters, index) for index in indices]

    pool = Pool(numberOfCores)
    nb_to_do = len(param_values)
    nb_done = 0
    permutations = list()
    for output in pool.imap_unordered(evaluate, jobs):
        result = _get_sensitivity_result(output)
        myDataStruct.add_data(result)
        permutations.append(output["index"])
        nb_done += 1
        printIfShown("did {} over {}".format(nb_done, nb_to_do), SHOW_INFO)

    # save results
    autosaveStruct.stop_autosave()

    myDataStruct.reorder(permutations=permutations)
    autosaveStruct.save()

    pool.close()
    pool.join()
    return myDataStruct
