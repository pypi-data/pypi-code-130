# Copyright (C) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE in project root for information.


"""
SynapseML is an ecosystem of tools aimed towards expanding the distributed computing framework
Apache Spark in several new directions. SynapseML adds many deep learning and data science tools to the Spark
ecosystem, including seamless integration of Spark Machine Learning pipelines with
Microsoft Cognitive Toolkit (CNTK), LightGBM and OpenCV. These tools enable powerful and
highly-scalable predictive and analytical models for a variety of datasources.

SynapseML also brings new networking capabilities to the Spark Ecosystem. With the HTTP on Spark project,
users can embed any web service into their SparkML models. In this vein, SynapseML provides easy to use SparkML
transformers for a wide variety of Microsoft Cognitive Services. For production grade deployment,
the Spark Serving project enables high throughput, sub-millisecond latency web services,
backed by your Spark cluster.

SynapseML requires Scala 2.12, Spark 3.0+, and Python 3.6+.
"""

__version__ = "0.10.1"
__spark_package_version__ = "0.10.1"

from synapse.ml.cognitive.AddDocuments import *
from synapse.ml.cognitive.AnalyzeBusinessCards import *
from synapse.ml.cognitive.AnalyzeCustomModel import *
from synapse.ml.cognitive.AnalyzeDocument import *
from synapse.ml.cognitive.AnalyzeIDDocuments import *
from synapse.ml.cognitive.AnalyzeImage import *
from synapse.ml.cognitive.AnalyzeInvoices import *
from synapse.ml.cognitive.AnalyzeLayout import *
from synapse.ml.cognitive.AnalyzeReceipts import *
from synapse.ml.cognitive.AzureSearchWriter import *
from synapse.ml.cognitive.BingImageSearch import *
from synapse.ml.cognitive.BreakSentence import *
from synapse.ml.cognitive.ConversationTranscription import *
from synapse.ml.cognitive.DescribeImage import *
from synapse.ml.cognitive.Detect import *
from synapse.ml.cognitive.DetectAnomalies import *
from synapse.ml.cognitive.DetectFace import *
from synapse.ml.cognitive.DetectLastAnomaly import *
from synapse.ml.cognitive.DetectMultivariateAnomaly import *
from synapse.ml.cognitive.DictionaryExamples import *
from synapse.ml.cognitive.DictionaryLookup import *
from synapse.ml.cognitive.DocumentTranslator import *
from synapse.ml.cognitive.EntityDetector import *
from synapse.ml.cognitive.EntityDetectorSDK import *
from synapse.ml.cognitive.EntityDetectorV2 import *
from synapse.ml.cognitive.FindSimilarFace import *
from synapse.ml.cognitive.FitMultivariateAnomaly import *
from synapse.ml.cognitive.FormOntologyLearner import *
from synapse.ml.cognitive.FormOntologyTransformer import *
from synapse.ml.cognitive.GenerateThumbnails import *
from synapse.ml.cognitive.GetCustomModel import *
from synapse.ml.cognitive.GroupFaces import *
from synapse.ml.cognitive.HealthcareSDK import *
from synapse.ml.cognitive.IdentifyFaces import *
from synapse.ml.cognitive.KeyPhraseExtractor import *
from synapse.ml.cognitive.KeyPhraseExtractorSDK import *
from synapse.ml.cognitive.KeyPhraseExtractorV2 import *
from synapse.ml.cognitive.LanguageDetector import *
from synapse.ml.cognitive.LanguageDetectorSDK import *
from synapse.ml.cognitive.LanguageDetectorV2 import *
from synapse.ml.cognitive.ListCustomModels import *
from synapse.ml.cognitive.NER import *
from synapse.ml.cognitive.NERSDK import *
from synapse.ml.cognitive.NERV2 import *
from synapse.ml.cognitive.OCR import *
from synapse.ml.cognitive.OpenAICompletion import *
from synapse.ml.cognitive.PII import *
from synapse.ml.cognitive.PIISDK import *
from synapse.ml.cognitive.ReadImage import *
from synapse.ml.cognitive.RecognizeDomainSpecificContent import *
from synapse.ml.cognitive.RecognizeText import *
from synapse.ml.cognitive.SimpleDetectAnomalies import *
from synapse.ml.cognitive.SpeechToText import *
from synapse.ml.cognitive.SpeechToTextSDK import *
from synapse.ml.cognitive.TagImage import *
from synapse.ml.cognitive.TextAnalyze import *
from synapse.ml.cognitive.TextSentiment import *
from synapse.ml.cognitive.TextSentimentSDK import *
from synapse.ml.cognitive.TextSentimentV2 import *
from synapse.ml.cognitive.TextToSpeech import *
from synapse.ml.cognitive.Translate import *
from synapse.ml.cognitive.Transliterate import *
from synapse.ml.cognitive.VerifyFaces import *

