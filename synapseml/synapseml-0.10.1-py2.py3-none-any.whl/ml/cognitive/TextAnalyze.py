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
class TextAnalyze(ComplexParamsMixin, JavaMLReadable, JavaMLWritable, JavaTransformer):
    """
    Args:
        backoffs (list): array of backoffs to use in the handler
        concurrency (int): max number of concurrent calls
        concurrentTimeout (float): max number seconds to wait on futures if concurrency >= 1
        entityLinkingTasks (object): the entity linking tasks to perform on submitted documents
        entityRecognitionPiiTasks (object): the entity recognition pii tasks to perform on submitted documents
        entityRecognitionTasks (object): the entity recognition tasks to perform on submitted documents
        errorCol (str): column to hold http errors
        initialPollingDelay (int): number of milliseconds to wait before first poll for result
        keyPhraseExtractionTasks (object): the key phrase extraction tasks to perform on submitted documents
        language (object): the language code of the text (optional for some services)
        maxPollingRetries (int): number of times to poll
        outputCol (str): The name of the output column
        pollingDelay (int): number of milliseconds to wait between polling
        sentimentAnalysisTasks (object): the sentiment analysis tasks to perform on submitted documents
        subscriptionKey (object): the API key to use
        suppressMaxRetriesExceededException (bool): set true to suppress the maxumimum retries exception and report in the error column
        text (object): the text in the request body
        timeout (float): number of seconds to wait before closing the connection
        url (str): Url of the service
    """

    backoffs = Param(Params._dummy(), "backoffs", "array of backoffs to use in the handler", typeConverter=TypeConverters.toListInt)
    
    concurrency = Param(Params._dummy(), "concurrency", "max number of concurrent calls", typeConverter=TypeConverters.toInt)
    
    concurrentTimeout = Param(Params._dummy(), "concurrentTimeout", "max number seconds to wait on futures if concurrency >= 1", typeConverter=TypeConverters.toFloat)
    
    entityLinkingTasks = Param(Params._dummy(), "entityLinkingTasks", "the entity linking tasks to perform on submitted documents")
    
    entityRecognitionPiiTasks = Param(Params._dummy(), "entityRecognitionPiiTasks", "the entity recognition pii tasks to perform on submitted documents")
    
    entityRecognitionTasks = Param(Params._dummy(), "entityRecognitionTasks", "the entity recognition tasks to perform on submitted documents")
    
    errorCol = Param(Params._dummy(), "errorCol", "column to hold http errors", typeConverter=TypeConverters.toString)
    
    initialPollingDelay = Param(Params._dummy(), "initialPollingDelay", "number of milliseconds to wait before first poll for result", typeConverter=TypeConverters.toInt)
    
    keyPhraseExtractionTasks = Param(Params._dummy(), "keyPhraseExtractionTasks", "the key phrase extraction tasks to perform on submitted documents")
    
    language = Param(Params._dummy(), "language", "ServiceParam: the language code of the text (optional for some services)")
    
    maxPollingRetries = Param(Params._dummy(), "maxPollingRetries", "number of times to poll", typeConverter=TypeConverters.toInt)
    
    outputCol = Param(Params._dummy(), "outputCol", "The name of the output column", typeConverter=TypeConverters.toString)
    
    pollingDelay = Param(Params._dummy(), "pollingDelay", "number of milliseconds to wait between polling", typeConverter=TypeConverters.toInt)
    
    sentimentAnalysisTasks = Param(Params._dummy(), "sentimentAnalysisTasks", "the sentiment analysis tasks to perform on submitted documents")
    
    subscriptionKey = Param(Params._dummy(), "subscriptionKey", "ServiceParam: the API key to use")
    
    suppressMaxRetriesExceededException = Param(Params._dummy(), "suppressMaxRetriesExceededException", "set true to suppress the maxumimum retries exception and report in the error column", typeConverter=TypeConverters.toBoolean)
    
    text = Param(Params._dummy(), "text", "ServiceParam: the text in the request body")
    
    timeout = Param(Params._dummy(), "timeout", "number of seconds to wait before closing the connection", typeConverter=TypeConverters.toFloat)
    
    url = Param(Params._dummy(), "url", "Url of the service", typeConverter=TypeConverters.toString)

    
    @keyword_only
    def __init__(
        self,
        java_obj=None,
        backoffs=[100,500,1000],
        concurrency=1,
        concurrentTimeout=None,
        entityLinkingTasks=[],
        entityRecognitionPiiTasks=[],
        entityRecognitionTasks=[],
        errorCol="TextAnalyze_d7420730934a_error",
        initialPollingDelay=300,
        keyPhraseExtractionTasks=[],
        language=None,
        languageCol=None,
        maxPollingRetries=1000,
        outputCol="TextAnalyze_d7420730934a_output",
        pollingDelay=300,
        sentimentAnalysisTasks=[],
        subscriptionKey=None,
        subscriptionKeyCol=None,
        suppressMaxRetriesExceededException=False,
        text=None,
        textCol=None,
        timeout=60.0,
        url=None
        ):
        super(TextAnalyze, self).__init__()
        if java_obj is None:
            self._java_obj = self._new_java_obj("com.microsoft.azure.synapse.ml.cognitive.TextAnalyze", self.uid)
        else:
            self._java_obj = java_obj
        self._setDefault(backoffs=[100,500,1000])
        self._setDefault(concurrency=1)
        self._setDefault(entityLinkingTasks=[])
        self._setDefault(entityRecognitionPiiTasks=[])
        self._setDefault(entityRecognitionTasks=[])
        self._setDefault(errorCol="TextAnalyze_d7420730934a_error")
        self._setDefault(initialPollingDelay=300)
        self._setDefault(keyPhraseExtractionTasks=[])
        self._setDefault(maxPollingRetries=1000)
        self._setDefault(outputCol="TextAnalyze_d7420730934a_output")
        self._setDefault(pollingDelay=300)
        self._setDefault(sentimentAnalysisTasks=[])
        self._setDefault(suppressMaxRetriesExceededException=False)
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
        backoffs=[100,500,1000],
        concurrency=1,
        concurrentTimeout=None,
        entityLinkingTasks=[],
        entityRecognitionPiiTasks=[],
        entityRecognitionTasks=[],
        errorCol="TextAnalyze_d7420730934a_error",
        initialPollingDelay=300,
        keyPhraseExtractionTasks=[],
        language=None,
        languageCol=None,
        maxPollingRetries=1000,
        outputCol="TextAnalyze_d7420730934a_output",
        pollingDelay=300,
        sentimentAnalysisTasks=[],
        subscriptionKey=None,
        subscriptionKeyCol=None,
        suppressMaxRetriesExceededException=False,
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
        return "com.microsoft.azure.synapse.ml.cognitive.TextAnalyze"

    @staticmethod
    def _from_java(java_stage):
        module_name=TextAnalyze.__module__
        module_name=module_name.rsplit(".", 1)[0] + ".TextAnalyze"
        return from_java(java_stage, module_name)

    def setBackoffs(self, value):
        """
        Args:
            backoffs: array of backoffs to use in the handler
        """
        self._set(backoffs=value)
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
    
    def setEntityLinkingTasks(self, value):
        """
        Args:
            entityLinkingTasks: the entity linking tasks to perform on submitted documents
        """
        self._set(entityLinkingTasks=value)
        return self
    
    def setEntityRecognitionPiiTasks(self, value):
        """
        Args:
            entityRecognitionPiiTasks: the entity recognition pii tasks to perform on submitted documents
        """
        self._set(entityRecognitionPiiTasks=value)
        return self
    
    def setEntityRecognitionTasks(self, value):
        """
        Args:
            entityRecognitionTasks: the entity recognition tasks to perform on submitted documents
        """
        self._set(entityRecognitionTasks=value)
        return self
    
    def setErrorCol(self, value):
        """
        Args:
            errorCol: column to hold http errors
        """
        self._set(errorCol=value)
        return self
    
    def setInitialPollingDelay(self, value):
        """
        Args:
            initialPollingDelay: number of milliseconds to wait before first poll for result
        """
        self._set(initialPollingDelay=value)
        return self
    
    def setKeyPhraseExtractionTasks(self, value):
        """
        Args:
            keyPhraseExtractionTasks: the key phrase extraction tasks to perform on submitted documents
        """
        self._set(keyPhraseExtractionTasks=value)
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
    
    def setMaxPollingRetries(self, value):
        """
        Args:
            maxPollingRetries: number of times to poll
        """
        self._set(maxPollingRetries=value)
        return self
    
    def setOutputCol(self, value):
        """
        Args:
            outputCol: The name of the output column
        """
        self._set(outputCol=value)
        return self
    
    def setPollingDelay(self, value):
        """
        Args:
            pollingDelay: number of milliseconds to wait between polling
        """
        self._set(pollingDelay=value)
        return self
    
    def setSentimentAnalysisTasks(self, value):
        """
        Args:
            sentimentAnalysisTasks: the sentiment analysis tasks to perform on submitted documents
        """
        self._set(sentimentAnalysisTasks=value)
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
    
    def setSuppressMaxRetriesExceededException(self, value):
        """
        Args:
            suppressMaxRetriesExceededException: set true to suppress the maxumimum retries exception and report in the error column
        """
        self._set(suppressMaxRetriesExceededException=value)
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

    
    def getBackoffs(self):
        """
        Returns:
            backoffs: array of backoffs to use in the handler
        """
        return self.getOrDefault(self.backoffs)
    
    
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
    
    
    def getEntityLinkingTasks(self):
        """
        Returns:
            entityLinkingTasks: the entity linking tasks to perform on submitted documents
        """
        return self.getOrDefault(self.entityLinkingTasks)
    
    
    def getEntityRecognitionPiiTasks(self):
        """
        Returns:
            entityRecognitionPiiTasks: the entity recognition pii tasks to perform on submitted documents
        """
        return self.getOrDefault(self.entityRecognitionPiiTasks)
    
    
    def getEntityRecognitionTasks(self):
        """
        Returns:
            entityRecognitionTasks: the entity recognition tasks to perform on submitted documents
        """
        return self.getOrDefault(self.entityRecognitionTasks)
    
    
    def getErrorCol(self):
        """
        Returns:
            errorCol: column to hold http errors
        """
        return self.getOrDefault(self.errorCol)
    
    
    def getInitialPollingDelay(self):
        """
        Returns:
            initialPollingDelay: number of milliseconds to wait before first poll for result
        """
        return self.getOrDefault(self.initialPollingDelay)
    
    
    def getKeyPhraseExtractionTasks(self):
        """
        Returns:
            keyPhraseExtractionTasks: the key phrase extraction tasks to perform on submitted documents
        """
        return self.getOrDefault(self.keyPhraseExtractionTasks)
    
    
    def getLanguage(self):
        """
        Returns:
            language: the language code of the text (optional for some services)
        """
        return self._java_obj.getLanguage()
    
    
    def getMaxPollingRetries(self):
        """
        Returns:
            maxPollingRetries: number of times to poll
        """
        return self.getOrDefault(self.maxPollingRetries)
    
    
    def getOutputCol(self):
        """
        Returns:
            outputCol: The name of the output column
        """
        return self.getOrDefault(self.outputCol)
    
    
    def getPollingDelay(self):
        """
        Returns:
            pollingDelay: number of milliseconds to wait between polling
        """
        return self.getOrDefault(self.pollingDelay)
    
    
    def getSentimentAnalysisTasks(self):
        """
        Returns:
            sentimentAnalysisTasks: the sentiment analysis tasks to perform on submitted documents
        """
        return self.getOrDefault(self.sentimentAnalysisTasks)
    
    
    def getSubscriptionKey(self):
        """
        Returns:
            subscriptionKey: the API key to use
        """
        return self._java_obj.getSubscriptionKey()
    
    
    def getSuppressMaxRetriesExceededException(self):
        """
        Returns:
            suppressMaxRetriesExceededException: set true to suppress the maxumimum retries exception and report in the error column
        """
        return self.getOrDefault(self.suppressMaxRetriesExceededException)
    
    
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
    
    def setLinkedService(self, value):
        self._java_obj = self._java_obj.setLinkedService(value)
        return self
        