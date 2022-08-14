import typing as t
from ...render import RenderOptions


ViewType = t.TypeVar("ViewType" ''', bound=t.Type[AbstractView]''')
ViewHint = t.TypeVar("ViewHint", ''', bound=t.Union[str, t.Type[AbstractView]]''')
ToRender = t.TypeVar("ToRender", bound=t.Union[str, RenderOptions])

Bot = t.TypeVar("Bot")
Bot.__doc__ = "Represents `Bot` object of adaptee lib."

Message = t.TypeVar("Message")
Message.__doc__ = ("Represents `Message` object of adaptee lib."
				  " It generally corresponds to `Message` type of Telegram API.")

Query = t.TypeVar("Query")
Query.__doc__ = ("Represents `Query` object of adaptee lib."
                " It generally corresponds to `Query` type of Telegram API.")