from .base import Tag, on_render, TagConfig


# suppresses registering of hooks
class BlankUi:

    def __getattribute__(self, name):
        return lambda *_, **__: None


class RootTag(Tag):

    _config = TagConfig(name="root")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._ui = None

        self.entry_index = 0
        self.current_entry = None
        self.used_entry_chars = []
        
        self.rerender = False
        self.config = {}
        self.empty_entry = None

    def double_render(self):
        self.rerender = True

    # special case, doesn't need decorator
    async def render(self, ui = None):
        self._ui = ui

        self.entry_count = 0
        self.used_entry_chars = []
        self.moved_up = False

        await self.render_children()
        
        # this could get dangerous
        if self.rerender:
            self.rerender = False
            await self.render(ui)
        
        return self

    def next_entry(self):
        if self.entry_count > self.entry_index + 1:
            self.entry_index += 1
            self.moved_up = True

    def previous_entry(self):
        if self.entry_index > 0:
            self.entry_index -= 1