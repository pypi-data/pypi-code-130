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
class _CNTKModel(ComplexParamsMixin, JavaMLReadable, JavaMLWritable, JavaModel):
    """
    Args:
        batchInput (bool): whether to use a batcher
        convertOutputToDenseVector (bool): whether to convert the output to dense vectors
        feedDict (dict):  Provide a map from CNTK/ONNX model input variable names (keys) to column names of the input dataframe (values)
        fetchDict (dict): Provide a map from column names of the output dataframe (keys) to CNTK/ONNX model output variable names (values)
        miniBatcher (object): Minibatcher to use
        model (object): Array of bytes containing the serialized CNTKModel
    """

    batchInput = Param(Params._dummy(), "batchInput", "whether to use a batcher", typeConverter=TypeConverters.toBoolean)
    
    convertOutputToDenseVector = Param(Params._dummy(), "convertOutputToDenseVector", "whether to convert the output to dense vectors", typeConverter=TypeConverters.toBoolean)
    
    feedDict = Param(Params._dummy(), "feedDict", " Provide a map from CNTK/ONNX model input variable names (keys) to column names of the input dataframe (values)")
    
    fetchDict = Param(Params._dummy(), "fetchDict", "Provide a map from column names of the output dataframe (keys) to CNTK/ONNX model output variable names (values)")
    
    miniBatcher = Param(Params._dummy(), "miniBatcher", "Minibatcher to use")
    
    model = Param(Params._dummy(), "model", "Array of bytes containing the serialized CNTKModel")

    
    @keyword_only
    def __init__(
        self,
        java_obj=None,
        batchInput=True,
        convertOutputToDenseVector=True,
        feedDict={"ARGUMENT_0":"ARGUMENT_0"},
        fetchDict={"OUTPUT_0":"OUTPUT_0"},
        miniBatcher=None,
        model=None
        ):
        super(_CNTKModel, self).__init__()
        if java_obj is None:
            self._java_obj = self._new_java_obj("com.microsoft.azure.synapse.ml.cntk.CNTKModel", self.uid)
        else:
            self._java_obj = java_obj
        self._setDefault(batchInput=True)
        self._setDefault(convertOutputToDenseVector=True)
        self._setDefault(feedDict={"ARGUMENT_0":"ARGUMENT_0"})
        self._setDefault(fetchDict={"OUTPUT_0":"OUTPUT_0"})
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
        batchInput=True,
        convertOutputToDenseVector=True,
        feedDict={"ARGUMENT_0":"ARGUMENT_0"},
        fetchDict={"OUTPUT_0":"OUTPUT_0"},
        miniBatcher=None,
        model=None
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
        return "com.microsoft.azure.synapse.ml.cntk.CNTKModel"

    @staticmethod
    def _from_java(java_stage):
        module_name=_CNTKModel.__module__
        module_name=module_name.rsplit(".", 1)[0] + ".CNTKModel"
        return from_java(java_stage, module_name)

    def setBatchInput(self, value):
        """
        Args:
            batchInput: whether to use a batcher
        """
        self._set(batchInput=value)
        return self
    
    def setConvertOutputToDenseVector(self, value):
        """
        Args:
            convertOutputToDenseVector: whether to convert the output to dense vectors
        """
        self._set(convertOutputToDenseVector=value)
        return self
    
    def setFeedDict(self, value):
        """
        Args:
            feedDict:  Provide a map from CNTK/ONNX model input variable names (keys) to column names of the input dataframe (values)
        """
        self._set(feedDict=value)
        return self
    
    def setFetchDict(self, value):
        """
        Args:
            fetchDict: Provide a map from column names of the output dataframe (keys) to CNTK/ONNX model output variable names (values)
        """
        self._set(fetchDict=value)
        return self
    
    def setMiniBatcher(self, value):
        """
        Args:
            miniBatcher: Minibatcher to use
        """
        self._set(miniBatcher=value)
        return self
    
    def setModel(self, value):
        """
        Args:
            model: Array of bytes containing the serialized CNTKModel
        """
        self._set(model=value)
        return self

    
    def getBatchInput(self):
        """
        Returns:
            batchInput: whether to use a batcher
        """
        return self.getOrDefault(self.batchInput)
    
    
    def getConvertOutputToDenseVector(self):
        """
        Returns:
            convertOutputToDenseVector: whether to convert the output to dense vectors
        """
        return self.getOrDefault(self.convertOutputToDenseVector)
    
    
    def getFeedDict(self):
        """
        Returns:
            feedDict:  Provide a map from CNTK/ONNX model input variable names (keys) to column names of the input dataframe (values)
        """
        return self.getOrDefault(self.feedDict)
    
    
    def getFetchDict(self):
        """
        Returns:
            fetchDict: Provide a map from column names of the output dataframe (keys) to CNTK/ONNX model output variable names (values)
        """
        return self.getOrDefault(self.fetchDict)
    
    
    def getMiniBatcher(self):
        """
        Returns:
            miniBatcher: Minibatcher to use
        """
        return JavaParams._from_java(self._java_obj.getMiniBatcher())
    
    
    def getModel(self):
        """
        Returns:
            model: Array of bytes containing the serialized CNTKModel
        """
        return self.getOrDefault(self.model)

    

    
        