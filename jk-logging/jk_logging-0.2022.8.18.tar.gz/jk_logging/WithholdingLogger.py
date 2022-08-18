

import os
import typing

from .impl.IDCounter import IDCounter

from .ExceptionInChildContextException import ExceptionInChildContextException
from .EnumLogLevel import EnumLogLevel
from .impl.LogStats import LogStats
from .AbstractLogger import AbstractLogger
from .impl.Converter import Converter
from .impl.JSONDict import JSONDict
from .BufferLogger import BufferLogger
from .InvalidExtraArgumentsException import InvalidExtraArgumentsException







class WithholdingLogger(BufferLogger):

	################################################################################################################################
	## Constructor
	################################################################################################################################

	#
	# Constructor method.
	#
	def __init__(self,
			idCounter:IDCounter = None,
			parentID:int = None,
			indentLevel:int = 0,
			logItemList = None,
			logStats:LogStats = None,
			extraProperties:JSONDict = None,
			mainLogger:AbstractLogger = None,
			bVerbose:bool = False,
		):

		super().__init__(idCounter, parentID, indentLevel, logItemList, logStats, extraProperties)

		self.__mainLogger = mainLogger
		self.__bVerbose = bVerbose
	#

	################################################################################################################################
	## Public Properties
	################################################################################################################################

	################################################################################################################################
	## Helper Methods
	################################################################################################################################

	def _descend(self, logEntryStruct:list) -> AbstractLogger:
		self._logStats.increment(logEntryStruct[5])

		nextID = logEntryStruct[1]
		newList = logEntryStruct[7]

		return WithholdingLogger(
			idCounter=self._idCounter,
			parentID=nextID,
			indentLevel=self._indentationLevel + 1,
			logItemList=newList,
			logStats=self._logStats,
			extraProperties=self._extraProperties,
			mainLogger=None,
			bVerbose=self.__bVerbose,
		)
	#

	################################################################################################################################
	## Public Methods
	################################################################################################################################

	def __str__(self):
		return "<" + self.__class__.__name__ + "(" + hex(id(self)) + ", indent=" + str(self._indentationLevel) + ",parentID=" + str(self._parentLogEntryID) + ")>"
	#

	def __repr__(self):
		return "<" + self.__class__.__name__ + "(" + hex(id(self)) + ", indent=" + str(self._indentationLevel) + ",parentID=" + str(self._parentLogEntryID) + ")>"
	#

	def __exit__(self, ex_type:type, ex_value:Exception, ex_traceback):
		if ex_type != None:
			if isinstance(ex_value, ExceptionInChildContextException):
				if self.__mainLogger:
					self.forwardTo(self.__mainLogger)
				return False
			if isinstance(ex_value, GeneratorExit):
				if self.__mainLogger:
					self.forwardTo(self.__mainLogger)
				return False
			#e = ex_type(value)
			#self.exception(e)
			self.exception(ex_value)
			if self.__mainLogger:
				self.forwardTo(self.__mainLogger)
			raise ExceptionInChildContextException(ex_value)

		if self.__mainLogger:
			if self.stats.hasAtLeastWarning or self.__bVerbose:
				self.forwardTo(self.__mainLogger)

		return False
	#

	################################################################################################################################
	## Public Static Methods
	################################################################################################################################

	@staticmethod
	def create(
			mainLogger:AbstractLogger = None,
			*args,
			jsonData:typing.Union[dict,list] = None,
			bVerbose:bool = False,
		):

		if args:
			raise InvalidExtraArgumentsException()

		# ----

		appendData, extraProperties = BufferLogger._convertJSONToInternal(jsonData)

		# ----

		logger = WithholdingLogger(extraProperties=extraProperties, mainLogger=mainLogger, bVerbose=bVerbose)

		if appendData is not None:
			logger._logiAll(appendData, True)

		return logger
	#

#







