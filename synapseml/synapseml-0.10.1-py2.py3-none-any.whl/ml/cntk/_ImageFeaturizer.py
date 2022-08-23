# Copyright (C) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE in project root for information.


import sys
if sys.version >= '3':
    basestring = str

from pyspark import SparkContext, SQLContext
from pyspark.sql import DataFrame
from pyspark.ml.param.shared import *
from pyspark import keyword_only
from pyspark.ml.util import JavaMLReadable, JavaMLWritable
from synapse.ml.core.serialize.java_params_patch import *
from pyspark.ml.wrapper import JavaTransformer, JavaEstimator, JavaModel
from pyspark.ml.evaluation import JavaEvaluator
from pyspark.ml.common import inherit_doc
from synapse.ml.core.schema.Utils import *
from pyspark.ml.param import TypeConverters
from synapse.ml.core.schema.TypeConversionUtils import generateTypeConverter, complexTypeConverter


@inherit_doc
class _ImageFeaturizer(ComplexParamsMixin, JavaMLReadable, JavaMLWritable, JavaTransformer):
    """
    Args:
        cntkModel (object): The internal CNTK model used in the featurizer
        cutOutputLayers (int): The number of layers to cut off the end of the network, 0 leaves the network intact, 1 removes the output layer, etc
        dropNa (bool): Whether to drop na values before mapping
        inputCol (str): The name of the input column
        layerNames (list): Array with valid CNTK nodes to choose from, the first entries of this array should be closer to the output node
        outputCol (str): The name of the output column
    """

    cntkModel = Param(Params._dummy(), "cntkModel", "The internal CNTK model used in the featurizer")
    
    cutOutputLayers = Param(Params._dummy(), "cutOutputLayers", "The number of layers to cut off the end of the network, 0 leaves the network intact, 1 removes the output layer, etc", typeConverter=TypeConverters.toInt)
    
    dropNa = Param(Params._dummy(), "dropNa", "Whether to drop na values before mapping", typeConverter=TypeConverters.toBoolean)
    
    inputCol = Param(Params._dummy(), "inputCol", "The name of the input column", typeConverter=TypeConverters.toString)
    
    layerNames = Param(Params._dummy(), "layerNames", "Array with valid CNTK nodes to choose from, the first entries of this array should be closer to the output node", typeConverter=TypeConverters.toListString)
    
    outputCol = Param(Params._dummy(), "outputCol", "The name of the output column", typeConverter=TypeConverters.toString)

    
    @keyword_only
    def __init__(
        self,
        java_obj=None,
        cntkModel=None,
        cutOutputLayers=1,
        dropNa=True,
        inputCol=None,
        layerNames=None,
        outputCol="ImageFeaturizer_f2aaf388a7c7_output"
        ):
        super(_ImageFeaturizer, self).__init__()
        if java_obj is None:
            self._java_obj = self._new_java_obj("com.microsoft.azure.synapse.ml.cntk.ImageFeaturizer", self.uid)
        else:
            self._java_obj = java_obj
        self._setDefault(cutOutputLayers=1)
        self._setDefault(dropNa=True)
        self._setDefault(outputCol="ImageFeaturizer_f2aaf388a7c7_output")
        if hasattr(self, "_input_kwargs"):
            kwargs = self._input_kwargs
        else:
            kwargs = self.__init__._input_kwargs
    
        if java_obj is None:
            for k,v in kwargs.items():
                if v is not None:
                    getattr(self, "set" + k[0].upper() + k[1:])(v)

    @keyword_only
    def setParams(
        self,
        cntkModel=None,
        cutOutputLayers=1,
        dropNa=True,
        inputCol=None,
        layerNames=None,
        outputCol="ImageFeaturizer_f2aaf388a7c7_output"
        ):
        """
        Set the (keyword only) parameters
        """
        if hasattr(self, "_input_kwargs"):
            kwargs = self._input_kwargs
        else:
            kwargs = self.__init__._input_kwargs
        return self._set(**kwargs)

    @classmethod
    def read(cls):
        """ Returns an MLReader instance for this class. """
        return JavaMMLReader(cls)

    @staticmethod
    def getJavaPackage():
        """ Returns package name String. """
        return "com.microsoft.azure.synapse.ml.cntk.ImageFeaturizer"

    @staticmethod
    def _from_java(java_stage):
        module_name=_ImageFeaturizer.__module__
        module_name=module_name.rsplit(".", 1)[0] + ".ImageFeaturizer"
        return from_java(java_stage, module_name)

    def setCntkModel(self, value):
        """
        Args:
            cntkModel: The internal CNTK model used in the featurizer
        """
        self._set(cntkModel=value)
        return self
    
    def setCutOutputLayers(self, value):
        """
        Args:
            cutOutputLayers: The number of layers to cut off the end of the network, 0 leaves the network intact, 1 removes the output layer, etc
        """
        self._set(cutOutputLayers=value)
        return self
    
    def setDropNa(self, value):
        """
        Args:
            dropNa: Whether to drop na values before mapping
        """
        self._set(dropNa=value)
        return self
    
    def setInputCol(self, value):
        """
        Args:
            inputCol: The name of the input column
        """
        self._set(inputCol=value)
        return self
    
    def setLayerNames(self, value):
        """
        Args:
            layerNames: Array with valid CNTK nodes to choose from, the first entries of this array should be closer to the output node
        """
        self._set(layerNames=value)
        return self
    
    def setOutputCol(self, value):
        """
        Args:
            outputCol: The name of the output column
        """
        self._set(outputCol=value)
        return self

    
    def getCntkModel(self):
        """
        Returns:
            cntkModel: The internal CNTK model used in the featurizer
        """
        return JavaParams._from_java(self._java_obj.getCntkModel())
    
    
    def getCutOutputLayers(self):
        """
        Returns:
            cutOutputLayers: The number of layers to cut off the end of the network, 0 leaves the network intact, 1 removes the output layer, etc
        """
        return self.getOrDefault(self.cutOutputLayers)
    
    
    def getDropNa(self):
        """
        Returns:
            dropNa: Whether to drop na values before mapping
        """
        return self.getOrDefault(self.dropNa)
    
    
    def getInputCol(self):
        """
        Returns:
            inputCol: The name of the input column
        """
        return self.getOrDefault(self.inputCol)
    
    
    def getLayerNames(self):
        """
        Returns:
            layerNames: Array with valid CNTK nodes to choose from, the first entries of this array should be closer to the output node
        """
        return self.getOrDefault(self.layerNames)
    
    
    def getOutputCol(self):
        """
        Returns:
            outputCol: The name of the output column
        """
        return self.getOrDefault(self.outputCol)

    

    
        