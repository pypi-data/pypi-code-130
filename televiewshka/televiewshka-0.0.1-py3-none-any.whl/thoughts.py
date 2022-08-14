
'''

Testing:

from views import TextView, KeyboardView
from type_aliases import Message, Query
from render import render
from bot import Bot 


bot = Bot()

@bot.command_handler("start")
def handle_start(message: Message):
    return render("FirstView")


class FirstView(KeyboardView):
    @bot.action_handler(action="next")
    def go_next(self, query: Query):
        return render("NextView", param=42)
        
    @staticmethod
    def render():
        pass
        
        
class NextView(TextView):
    @bot.action_handler()
    def go_back(self, query: Query):
        return render(FirstView)
    
    def on_message(self, message: Message) -> str:
        answer = f"I don't give a fuck about your {message}!"
        print(f"---> {answer}")
        return answer
    
    @staticmethod
    def render(param: int):
        pass
        
        
bot.register_views([FirstView, NextView])

print("<--- /start")
bot._handle_command(1, "start", None)
print(bot._storage._users)

print("<--- [ next ]")
bot._handle_action(1, "FirstView:next", None)
print(bot._storage._users)

print("<--- hello! ")
bot._handle_message(1, "Hello!")

print("<--- [ back ]")
bot._handle_action(1, "NextView:go_back", None)
print(bot._storage._users)



televiewshka/

    adaptors.py
    base.py -> Base adaptors
    views.py -> Views
    layouts.py -> Layouts
    type_aliases.py -> ...
    render.py -> render
    utils.py -> create_adaptor
    __init__.py

    storage/
            memory/
            redis/
            base.py
            exceptions.py
            __init__.py


from televiewshka import TelegramBot
from .views import * as views

bot = TelegramBot(token, telegram_bot_api=(bot, TeleBotAdapter))
bot.register_all(views)
bot.start_polling()


Base class provides handlers for text | query messages
and accepts data
provided as values of unified, primitive types (str)
Inherited classes are supposed to extract this data
from an underlying lib types (Message, Query) and then
pass it to the superclass methods to get
all the rest job to be done


_handle_text:
to_render = _dispatch_text_message(message)
        if to_render:            
            pass
        # current_view = self._state.get_view(user_id)
        # if isinstance(current_view, TextView):
        #    TODO: think about async `on_message`
        #    result = current_view.on_message(message)      
        #    if result:     
        #        self._bot.send_text_message(result)

_dispatch_text -> render_options | None:
    async or run on executor?

# current_view = self._state.get_view(user_id)
        # if isinstance(current_view, KeyboardView):
        #    handler = self._handlers.get(action)
        #    method = getattr(current_view, handler)
        #    view = current_view.__init__(user_state)
        #    method.__bind__(view).__call__()


class AbstractBotAdaptor(ABC):
    @abstractmethod
    def handler(self, action: str):
        pass

    @abstractmethod
    def text_handler(self, handler: Callable):
        pass

    @abstractmethod
    def save(self):
        pass


### Views

something that can be rendered to user
and than handle user actions on itselves
actions are dispatched to appropriate view' and method
in accordance with user state (e.g. current_scene flag)
which is set when the view is rendered

### Render

to render something, pass params as ctor arg and call render method

Renderable Layout: render

Renderable Scene:  render, [actions, ]
    - holds methods that represents links to another scenes (like a graph)

    - example:


        class MainScene(KeyboardView):
            @command_handler
            def start() -> ToRender[NextScene]:
                pass

            @action_handler
            def next(self):
                pass

            @text_handler
            def handle_message(self, message):
                pass

        class MainScene(televiewshka.KeyboardView):

            def start(self) -> ToRender[NextScene]:
                return render(NextScene, ..., inplace=True)

            def next(self):
                return render()

            def back(self):
                return render()

            def render(self, **kwargs) -> InlneKeyboardMarkup:
                pass

            @classmethod
            def register(cls):
                # super()._registered_counter += 1
                pass

# televiewshka
# messages ?
# views ?
# scenes ?

class GetUsername(televiewshka.TextView):
    # Dialog Message ?
    def on_text_message(self, message: str):
        pass

    def render(self):
        pass


### Dispatch

messages are being dispatched according to user' state
state = current scene
callback data or message = scene method

def dispatch(message) -> ToRender[Scene]:
    user = get_user(message)
    scene = get_scene(user.state)

    if scene:
        callback = get_callback(message)
        method = get_method_by_name(callback.get('action'))
        return method.__bind__(scene).__call__()


def dispatch(?message) -> RenderOptions:
    message = MessageInterface(message)
    user = User(message.get_user())
    layout = user.state.layout

    if layout:
        pass


# MessageInterface
# AbstractMessageAdaptor: MessageInterface
# BaseMessageAdaptor -> just swap class names ?

# render.py

from typing import Optional, Union
from .views import ViewType
from .utils import get_view_type

# views.py
ViewType = TypeVar("ViewType", bound=Type[AbstractBaseView])


class RenderOptions:
    def __init__(self, view_t: ViewType, inplace: bool, params: Optional[dict] = None):
        self.view_t = view_t
        self.inplace = inplace
        self.params = params


# .utils.py
def get_view_type(view_hint: ViewType | str) -> ViewType:
    if issubclass(view_hint, ViewType):
        view_t = view_hint
    elif isinstance(view_hint, str):
        view_t = get_class_by_name('view', view_hint)
    else:
        raise ValueError("")


def render(view_hint: ViewType | str, inplace = False, **kwargs):
    view_t = get_view_type(view_hint)
    return RenderOptions(view_t, inplace, kwargs)


### Recv & Send

def handle(message) -> None:
    to_render = dispatch(message)
    if to_render:
        if has_markup(to_render.scene):
            if to_render.inplace:
                self.render()
            else:
                self.render(edit_message=message)

        else:
            if to_render.inplace:
                self.render()
            else:
                self.render(edit_message=message)

### Register scenes

from .scenes import * as scenes

scenes = {
    scene.register(): scene
}



def _render(to_render: RenderRules) -> None:
    view = to_render.view
    args = to_render.args
    layout = view.render(**args)

    if isinstance(view, KeyboardView):
        # layout must contain both text and keyboard
        self._bot_adapter.send_message(text=layout.text, markup=layout.markup)


@dataclass
class RenderRules:
    view: Type[View]
    args: dict
    inplace: bool


TypeVar('ViewHint', bound=Union[Type[View], str])

def render(view_t: ViewHint, inplace=True, **kwargs) -> RenderRules:
    if isinstance(view_t, str):
        view_t = get_class_by_name(view_t)
    return RenderRules(view_t, inplace, kwargs)


from typing import Tuple


class View:

    def __init__(self, user):
        pass

    @classmethod
    def register(cls):
        pass

    @classmethod
    @abstractmethod
    def render(cls):
        pass


class KeyboardView(View):
    pass


class TextView(View):
    pass


from typing import Iterable, Type
from .view import View


class TelegramBot:

    def __init__(self):
        pass

    def register_all(self, Iterable[Type[View]]):
        pass

    def start_polling(self):
        pass


import functools
from typing import Optional


handlers = {}

def handler(action: Optional[str] = None):
    def func_wrapper(func):
        action_name = action or func.__name__
        handlers[action_name] = func

        @functools.wraps(func)
        def func_args_wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        return func_args_wrapper
    return func_wrapper


class AbstractBaseInputConverter(ABC):
    @staticmethod
    @abstractmethod
    def convert_message() -> MessageType:
        pass

    @staticmethod
    @abstractmethod
    def convert_query() -> QueryType:
        pass


class AbstractBaseAdaptor(ABC):
    def __init__(self, bot, input_converter: AbstractBaseInputConverter):
        pass



# message_interface
# query_interface
#
class AbstractBaseAdaptor(ABC):
    def handle(MessageInterface message):
        pass



template <typename InputMessage, typename InputQuery>
class AbstractBaseInputConverter
{
    public:
            virtual Message convert_message(InputMessage&& message) = 0;
            virtual Query convert_query(InputQuery&& query) = 0;
};


template <typename BotType>
class AbstractBaseAdaptor
{
    public:
            AbstractBaseAdaptor(
                    BotType bot,
                    AbstractBaseInputConverter input_converter):
                bot(bot),
                input_converter(input_converter) {}

            virtual void send_message(Message) = 0;

    protected:
            template <typename Message>
            void handle_message(Message message)
            {
                auto converted_message = input_converter.convert_message(message);
                auto result = dispatch(convert_message);
                send_message(result);
            }
};


# adaptors/base.py
from abc import ABC, abstractmethod


class Message:
    pass


class Query:
    pass


class AbstractInputConverter:
    """ This class is used to convert input data from
        the types specific for concrete framework """
    @staticmethod
    @abstractmethod
    def convert_message(message) -> Message:
        pass

    @staticmethod
    @abstractmethod
    def convert_query(query) -> Query:
        pass



'''
