class WebhookError(Exception):
	pass
class WebhookNotFound(WebhookError):
	pass
class InvalidWebhook(WebhookError):
	pass
class InvalidArgumentError(Exception):
	pass
class InvalidTreeError(Exception):
	pass
class CommandError(Exception):
	pass
class EmptyCommand(CommandError):
	pass