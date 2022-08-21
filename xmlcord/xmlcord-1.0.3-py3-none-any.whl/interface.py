from types import CoroutineType

from .tags import parse, RootTag, InvalidEntry, EmptyEntry
from .hooks import HookTrigger, Hook


class GeneralInterface:

    def __init__(self, renderer):
        self.renderer = renderer
        self.renderer.inject_trigger_receiver(self.receive_hook_trigger)

        self.root: RootTag = None

        self.input_hooks = []
        self.event_queue = []

        self.__suppress_refresh = False

    # generates a root by parsing the template form
    # and renders the template 
    async def construct(self, form):
        self.root = parse(form)

        await self.root.render(self)
        await self.renderer.construct(self.root)

    # not really sure where this is even used
    async def update(self):
        await self.root.render(self)
        await self.renderer.update(self.root)

    # api for registering input hooks from tags
    def register_hook(self, hook: Hook, func: CoroutineType):
        self.input_hooks.append((hook, func))

    # api for queueing events from tags
    def queue_event(self, event: CoroutineType):
        self.event_queue.append(event)

    # prevents the template from visually updating during 
    # the update loop following the call of this method 
    def suppress_refresh(self):
        self.__suppress_refresh = True

    # split hook and event loops?
    #
    # checks if any of the input hooks matches the passed hook trigger,
    # executes the hook function (if match) and refreshes input hooks
    async def receive_hook_trigger(self, trigger: HookTrigger):

        # deactivate interface if there are no input_hooks
        if not self.input_hooks:
            await self.renderer.deactivate()
            # suppresses HookTrigger cleanup
            return True

        while self.input_hooks:
            # goes through input_hooks backwards, this is to ensure 
            # entry hooks are handled correctly when changing entry mid render
            hook, func = self.input_hooks.pop()

            if hook is None or hook.matches(trigger):
                try:
                    await func(trigger)
                except InvalidEntry:
                    self.renderer.send_error("Invalid data type.")

                break

        # input_hooks and event_queue are purged and refilled here
        self.input_hooks = []
        self.event_queue = []
        
        # repopulates both input_hooks and event_queue
        await self.root.render(self)

        while self.event_queue:
            event = self.event_queue.pop(0)
            try:
                # events which return True terminate event loop 
                # and suppress HookTrigger cleanup
                if await event(): 
                    return True
            # not sure if here is the right place to handle this
            except EmptyEntry as entry_name:
                self.renderer.send_error(f"Field **'{entry_name}'** is required.")
                break

        if not self.__suppress_refresh:
            await self.renderer.update(self.root)
        else:
            self.__suppress_refresh = False
    
    # API FOR ROOT

    # deactivates the template without deleting it,
    # usually used after saving when done creating report
    def clean_up(self):
        async def __clean_up():
            await self.renderer.update(self.root)
            await self.renderer.deactivate()

            self.suppress_refresh()

        self.queue_event(__clean_up)

    # deletes and deactivates the template without saving
    def discard(self):
        async def __discard():
            await self.renderer.discard()
            self.suppress_refresh()

            return True

        self.queue_event(__discard)

    # replaces the current template with a new one
    # using the same renderer to display it
    def swap(self, form):
        async def __swap():
            self.root = parse(form)
            await self.root.render(self)

        self.queue_event(__swap)

    # moves the template to a new channel
    def forward(self, channel_id, mode=None):
        async def __forward():
            self.renderer.swap_channel(channel_id)
            await self.renderer.construct(self.root)

            # needs to be handled more generally elsewhere
            if mode == 'view':
                await self.renderer.deactivate()

            self.suppress_refresh()

        self.queue_event(__forward)