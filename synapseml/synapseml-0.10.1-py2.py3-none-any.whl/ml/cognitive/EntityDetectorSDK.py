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
class EntityDetectorSDK(ComplexParamsMixin, JavaMLReadable, JavaMLWritable, JavaTransformer):
    """
    Args:
        batchSize (int): The max size of the buffer
        concurrency (int): max number of concurrent calls
        concurrentTimeout (float): max number seconds to wait on futures if concurrency >= 1
        disableServiceLogs (object): disableServiceLogs option
        errorCol (str): column to hold http errors
        includeStatistics (object): includeStatistics option
        language (object): the language code of the text (optional for some services)
        modelVersion (object): modelVersion option
        outputCol (str): The name of the output column
        subscriptionKey (object): the API key to use
        text (object): the text in the request body
        timeout (float): number of seconds to wait before closing the connection
        url (str): Url of the service
    """

    batchSize = Param(Params._dummy(), "batchSize", "The max size of the buffer", typeConverter=TypeConverters.toInt)
    
    concurrency = Param(Params._dummy(), "concurrency", "max number of concurrent calls", typeConverter=TypeConverters.toInt)
    
    concurrentTimeout = Param(Params._dummy(), "concurrentTimeout", "max number seconds to wait on futures if concurrency >= 1", typeConverter=TypeConverters.toFloat)
    
    disableServiceLogs = Param(Params._dummy(), "disableServiceLogs", "ServiceParam: disableServiceLogs option")
    
    errorCol = Param(Params._dummy(), "errorCol", "column to hold http errors", typeConverter=TypeConverters.toString)
    
    includeStatistics = Param(Params._dummy(), "includeStatistics", "ServiceParam: includeStatistics option")
    
    language = Param(Params._dummy(), "language", "ServiceParam: the language code of the text (optional for some services)")
    
    modelVersion = Param(Params._dummy(), "modelVersion", "ServiceParam: modelVersion option")
    
    outputCol = Param(Params._dummy(), "outputCol", "The name of the output column", typeConverter=TypeConverters.toString)
    
    subscriptionKey = Param(Params._dummy(), "subscriptionKey", "ServiceParam: the API key to use")
    
    text = Param(Params._dummy(), "text", "ServiceParam: the text in the request body")
    
    timeout = Param(Params._dummy(), "timeout", "number of seconds to wait before closing the connection", typeConverter=TypeConverters.toFloat)
    
    url = Param(Params._dummy(), "url", "Url of the service", typeConverter=TypeConverters.toString)

    
    @keyword_only
    def __init__(
        self,
        java_obj=None,
        batchSize=5,
        concurrency=1,
        concurrentTimeout=None,
        disableServiceLogs=None,
        disableServiceLogsCol=None,
        errorCol="Error",
        includeStatistics=None,
        includeStatisticsCol=None,
        language=None,
        languageCol=None,
        modelVersion=None,
        modelVersionCol=None,
        outputCol=None,
        subscriptionKey=None,
        subscriptionKeyCol=None,
        text=None,
        textCol=None,
        timeout=60.0,
        url=None
        ):
        super(EntityDetectorSDK, self).__init__()
        if java_obj is None:
            self._java_obj = self._new_java_obj("com.microsoft.azure.synapse.ml.cognitive.EntityDetectorSDK", self.uid)
        else:
            self._java_obj = java_obj
        self._setDefault(batchSize=5)
        self._setDefault(concurrency=1)
        self._setDefault(errorCol="Error")
        self._setDefault(timeout=60.0)
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
        batchSize=5,
        concurrency=1,
        concurrentTimeout=None,
        disableServiceLogs=None,
        disableServiceLogsCol=None,
        errorCol="Error",
        includeStatistics=None,
        includeStatisticsCol=None,
        language=None,
        languageCol=None,
        modelVersion=None,
        modelVersionCol=None,
        outputCol=None,
        subscriptionKey=None,
        subscriptionKeyCol=None,
        text=None,
        textCol=None,
        timeout=60.0,
        url=None
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
        return "com.microsoft.azure.synapse.ml.cognitive.EntityDetectorSDK"

    @staticmethod
    def _from_java(java_stage):
        module_name=EntityDetectorSDK.__module__
        module_name=module_name.rsplit(".", 1)[0] + ".EntityDetectorSDK"
        return from_java(java_stage, module_name)

    def setBatchSize(self, value):
        """
        Args:
            batchSize: The max size of the buffer
        """
        self._set(batchSize=value)
        return self
    
    def setConcurrency(self, value):
        """
        Args:
            concurrency: max number of concurrent calls
        """
        self._set(concurrency=value)
        return self
    
    def setConcurrentTimeout(self, value):
        """
        Args:
            concurrentTimeout: max number seconds to wait on futures if concurrency >= 1
        """
        self._set(concurrentTimeout=value)
        return self
    
    def setDisableServiceLogs(self, value):
        """
        Args:
            disableServiceLogs: disableServiceLogs option
        """
        if isinstance(value, list):
            value = SparkContext._active_spark_context._jvm.com.microsoft.azure.synapse.ml.param.ServiceParam.toSeq(value)
        self._java_obj = self._java_obj.setDisableServiceLogs(value)
        return self
    
    def setDisableServiceLogsCol(self, value):
        """
        Args:
            disableServiceLogs: disableServiceLogs option
        """
        self._java_obj = self._java_obj.setDisableServiceLogsCol(value)
        return self
    
    def setErrorCol(self, value):
        """
        Args:
            errorCol: column to hold http errors
        """
        self._set(errorCol=value)
        return self
    
    def setIncludeStatistics(self, value):
        """
        Args:
            includeStatistics: includeStatistics option
        """
        if isinstance(value, list):
            value = SparkContext._active_spark_context._jvm.com.microsoft.azure.synapse.ml.param.ServiceParam.toSeq(value)
        self._java_obj = self._java_obj.setIncludeStatistics(value)
        return self
    
    def setIncludeStatisticsCol(self, value):
        """
        Args:
            includeStatistics: includeStatistics option
        """
        self._java_obj = self._java_obj.setIncludeStatisticsCol(value)
        return self
    
    def setLanguage(self, value):
        """
        Args:
            language: the language code of the text (optional for some services)
        """
        if isinstance(value, list):
            value = SparkContext._active_spark_context._jvm.com.microsoft.azure.synapse.ml.param.ServiceParam.toSeq(value)
        self._java_obj = self._java_obj.setLanguage(value)
        return self
    
    def setLanguageCol(self, value):
        """
        Args:
            language: the language code of the text (optional for some services)
        """
        self._java_obj = self._java_obj.setLanguageCol(value)
        return self
    
    def setModelVersion(self, value):
        """
        Args:
            modelVersion: modelVersion option
        """
        if isinstance(value, list):
            value = SparkContext._active_spark_context._jvm.com.microsoft.azure.synapse.ml.param.ServiceParam.toSeq(value)
        self._java_obj = self._java_obj.setModelVersion(value)
        return self
    
    def setModelVersionCol(self, value):
        """
        Args:
            modelVersion: modelVersion option
        """
        self._java_obj = self._java_obj.setModelVersionCol(value)
        return self
    
    def setOutputCol(self, value):
        """
        Args:
            outputCol: The name of the output column
        """
        self._set(outputCol=value)
        return self
    
    def setSubscriptionKey(self, value):
        """
        Args:
            subscriptionKey: the API key to use
        """
        if isinstance(value, list):
            value = SparkContext._active_spark_context._jvm.com.microsoft.azure.synapse.ml.param.ServiceParam.toSeq(value)
        self._java_obj = self._java_obj.setSubscriptionKey(value)
        return self
    
    def setSubscriptionKeyCol(self, value):
        """
        Args:
            subscriptionKey: the API key to use
        """
        self._java_obj = self._java_obj.setSubscriptionKeyCol(value)
        return self
    
    def setText(self, value):
        """
        Args:
            text: the text in the request body
        """
        if isinstance(value, list):
            value = SparkContext._active_spark_context._jvm.com.microsoft.azure.synapse.ml.param.ServiceParam.toSeq(value)
        self._java_obj = self._java_obj.setText(value)
        return self
    
    def setTextCol(self, value):
        """
        Args:
            text: the text in the request body
        """
        self._java_obj = self._java_obj.setTextCol(value)
        return self
    
    def setTimeout(self, value):
        """
        Args:
            timeout: number of seconds to wait before closing the connection
        """
        self._set(timeout=value)
        return self
    
    def setUrl(self, value):
        """
        Args:
            url: Url of the service
        """
        self._set(url=value)
        return self

    
    def getBatchSize(self):
        """
        Returns:
            batchSize: The max size of the buffer
        """
        return self.getOrDefault(self.batchSize)
    
    
    def getConcurrency(self):
        """
        Returns:
            concurrency: max number of concurrent calls
        """
        return self.getOrDefault(self.concurrency)
    
    
    def getConcurrentTimeout(self):
        """
        Returns:
            concurrentTimeout: max number seconds to wait on futures if concurrency >= 1
        """
        return self.getOrDefault(self.concurrentTimeout)
    
    
    def getDisableServiceLogs(self):
        """
        Returns:
            disableServiceLogs: disableServiceLogs option
        """
        return self._java_obj.getDisableServiceLogs()
    
    
    def getErrorCol(self):
        """
        Returns:
            errorCol: column to hold http errors
        """
        return self.getOrDefault(self.errorCol)
    
    
    def getIncludeStatistics(self):
        """
        Returns:
            includeStatistics: includeStatistics option
        """
        return self._java_obj.getIncludeStatistics()
    
    
    def getLanguage(self):
        """
        Returns:
            language: the language code of the text (optional for some services)
        """
        return self._java_obj.getLanguage()
    
    
    def getModelVersion(self):
        """
        Returns:
            modelVersion: modelVersion option
        """
        return self._java_obj.getModelVersion()
    
    
    def getOutputCol(self):
        """
        Returns:
            outputCol: The name of the output column
        """
        return self.getOrDefault(self.outputCol)
    
    
    def getSubscriptionKey(self):
        """
        Returns:
            subscriptionKey: the API key to use
        """
        return self._java_obj.getSubscriptionKey()
    
    
    def getText(self):
        """
        Returns:
            text: the text in the request body
        """
        return self._java_obj.getText()
    
    
    def getTimeout(self):
        """
        Returns:
            timeout: number of seconds to wait before closing the connection
        """
        return self.getOrDefault(self.timeout)
    
    
    def getUrl(self):
        """
        Returns:
            url: Url of the service
        """
        return self.getOrDefault(self.url)

    

    
    def setLocation(self, value):
        self._java_obj = self._java_obj.setLocation(value)
        return self
        