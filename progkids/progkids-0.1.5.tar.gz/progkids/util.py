from .__progkids__ import sendCommand


def postToChat(message):
    return sendCommand('chat:post', [message])
