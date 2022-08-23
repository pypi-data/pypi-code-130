from pygrambot.data_objects.objects import UpdateDt
from config.bot_settings import RELATIVE_PATH_TO_MIDDLEWARES
import time
from pygrambot.bot.botcommands.api_commands import SendCommand
from config.bot_settings import TOKEN


class NewMiddleware:
    """
    Class for creating middleware.
    To do this, you need to inherit from this class and implement the run method.
    """
    _middlewares_list: list = []
    enable: bool = True

    @classmethod
    async def run(cls, updatedt: UpdateDt) -> UpdateDt:
        """
        Middleware startup method.

        :return: UpdateDt
        """
        return updatedt


class ThrottlingMiddleware(NewMiddleware):
    time = time.time()
    users = {}
    timeout: float = 1
    message: str = 'Too many messages.'

    @classmethod
    async def set_message(cls, message: str):
        cls.message = message
        return cls

    @classmethod
    async def run(cls, updatedt: UpdateDt) -> UpdateDt:
        try:
            if not updatedt.message.id in cls.users.keys():
                cls.users[updatedt.message.id] = [updatedt.message.message_id, time.time()]
            else:
                t1 = cls.users[updatedt.message.id][1]
                t2 = time.time()
                mtime = t2 - t1
                if mtime < cls.timeout:
                    await SendCommand(TOKEN).sendMessage(chat_id=updatedt.message.id, text=cls.message,
                                                         reply_to_message_id=cls.users[updatedt.message.id][0])
                cls.users[updatedt.message.id] = [updatedt.message.message_id, time.time()]
        except Exception as e:
            print(f'ThrottlingMiddleware error: {e}')

        return updatedt

    @classmethod
    def set_timeout_sec(cls, value: float):
        cls.timeout = value
        return cls


class CatchNextMessageMiddleware(NewMiddleware):
    """
    Middleware that catches a single message and sends it for processing.
    """
    enable = True
    messages = []

    @classmethod
    async def add_message(cls, message_id):
        cls.messages.append(message_id)

    @classmethod
    async def run(cls, updatedt: UpdateDt) -> UpdateDt:
        if updatedt.message.id in cls.messages:
            updatedt.data['catch_msg'] = []
            updatedt.data['catch_msg'].append(updatedt)
            cls.messages.remove(updatedt.message.id)
        return updatedt


def get_middlewares() -> list[NewMiddleware]:
    """
    Returns a list with all middlewares.
    """
    middl = []
    for path in RELATIVE_PATH_TO_MIDDLEWARES:
        p = path.replace('/', '.').replace('\\', '.')
        if p.endswith('.'):
            p = p[:len(p) - 1] + p[len(p):]
        module = __import__(p, fromlist=['middlewares'])
        middl_module = getattr(module, 'middlewares')

        for i in middl_module.middlewareslist:
            middl.append(i)
    middl.append(CatchNextMessageMiddleware)
    return middl
