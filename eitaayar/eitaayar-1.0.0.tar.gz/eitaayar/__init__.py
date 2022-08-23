from .methods import (Methods,)


__author__ = 'Shayan Heidari'
__version__ = '1.0.0b'


class Eitaa(object,):
	def __init__(self, token,):
		self.request = Methods(token = token,)

	def getMe(self,):
		result = self.request.createMethod('getMe', {})
		if result.get('ok'):
			return result.get('result')
		else:
			del result
			return None

	def sendMessage(self, chat_id, text, title = None, notification_disable = None, reply_to_message_id = None, date = None, pin = None, viewCountForDelete = None,):
		"""
this is method only for send message in channels or super groups
		"""
		result = self.request.createMethod('sendMessage',
		{
			'chat_id': chat_id,
			'text': text,
			'title': title,
			'notification_disable': notification_disable,
			'reply_to_message_id': reply_to_message_id,
			'date': date,
			'pin': pin,
			'viewCountForDelete': viewCountForDelete,
		},)
		if result.get('ok'):
			return result
		else:
			del result
			return None

	def sendDocument(self,):
		pass

	def sendFile(self, file, caption = None):
		pass