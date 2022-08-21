import yaml
import re

from yaml import Loader

from src.hooks import HookTrigger, MessageHook, ReactionHook
from src.utils import find_item_in_array

from .base import Tag, on_render, TagConfig, Optional, Union


class ConfigTag(Tag):

    _config = TagConfig(name="config")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.config = {}

    @on_render()
    async def render(self, args):
        self.config = yaml.load(self.content, Loader=Loader)
        self.root.config = self.config


class ForTag(Tag):

    _config = TagConfig(
        name="for",
        args={
            "in":     list,
            "var":    Optional(str, "item"),
            "start":  Optional(int, None),
            "end":    Optional(int, None),
            "inline": Optional(bool, False)
        }
    )

    @on_render()
    async def render(self, args):
        out = []
        items = args['in'] or []
        
        for index, item in enumerate(items[args.start:args.end]):
            self.update_state({
                args.var: item,
                'index': index + 1
            })
            if to_add := await self.render_content():
                out.append(to_add)

        return (' ' if args.inline else '\n').join(out)


class IfTag(Tag):

    _config = TagConfig(
        name="if",
        args={
            "exp": bool
        }
    )

    @on_render()
    async def render(self, args):
        if args.exp and (content := await self.render_content()):
            return content
            
        return ""


class EmptyEntry(Exception):
    pass


# might be best to create an action for this
class CheckTag(Tag):

    _config = TagConfig(name="check")

    @on_render()
    async def render(self, args):
        async def event(*_):
            if entry := self.root.empty_entry:
                raise EmptyEntry(entry.get_arg('name'))

        self.ui.queue_event(event)


class InvalidEntry(Exception):
    pass


# # significant clean-up needed
class EntryTag(Tag):

#     name = "e"
#     args = {
#         'name':    (str,),
#         'dname':   (str, name),
#         'as':      (str, 'value'),
#         'require': (bool, False),
#         'type':    (str, 'none'),
#         'value':   (str, ''),
#         'options': (str, ''),
#         'show':    (bool, True),
#         'match':   (str, ''),
#         'repeat':  (bool, True),
#         'move':    (str, 'none')
#     }
    _config = TagConfig(
        name="entry",
        args={
            "name":    str,
            "var":     Optional(str),
            "require": Optional(bool, False),
            # this might be wrong
            "type":    Optional(str, "none"),
            "options": Optional(list),
            "show":    Optional(bool, True),
            "match":   Optional(str),
            "repeat":  Optional(bool, True),
            "move":    Optional(str, "none")
        }
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # there is no guaratnee 'name' will exist during init
        self.update_state(dname=self._static_kwargs.get('name'))

    @on_render()
    async def render(self, args):
        # declares 'value' and 'name' variables for local use
        name = self.parse_text(args.name)
        decor_name = str() 

        value = self.root.get_state(name)

        # print(f'setting val: {name} => {value}')
        self.update_state({
            (args.var or 'value'): value,
            'name': name,
        })

        if not value and not self.root.empty_entry:
            if self.root.config.get('entries') == 'required' or args.require is True:
                if args.require != False:
                    self.root.empty_entry = self
        elif value and self.root.empty_entry == self:
            self.root.empty_entry = None

        for i, ch in enumerate(name):
            ch = ch.lower()
            if ch not in self.root.used_entry_chars:
                decor_name = f"{name[:i]}__{name[i]}__{name[i+1:]}"
                self.update_state(dname=decor_name)

                def nav_wrapper(count):
                    # there might be a way to handle qck nav at render time
                    # if we know the letter beforehand
                    async def navigate(trigger: HookTrigger):
                        self.root.entry_index = count
                        trigger.resolve()
                        return True
                    return navigate

                self.ui.register_hook(
                    MessageHook(
                        f"({ch}|{ch.upper()})", 
                        checks=[lambda t: t.user.id == self.ui.renderer.author.id]
                    ),
                    func=nav_wrapper(self.root.entry_count)
                )

                self.root.used_entry_chars.append(ch)
                break
        
        if self.root.entry_index == self.root.entry_count:

            # sets the current entry as active
            self.root.current_entry = self

            self.root.update_state(
                {
                    'entryName': name, 
                    'entryType': args.type,
                    'entryValue': args.value
                }
            )
            self.update_state(
                {
                    'dname': '[ ' + decor_name + ' ]',
                    'active': 1
                }
            )

            async def del_all(trigger: HookTrigger):
                self.root.update_state({name: None})
                trigger.resolve()

            self.ui.register_hook(
                MessageHook(
                    r"(-d)",
                    checks=[lambda t: t.user.id == self.ui.renderer.author.id]
                ),
                func=del_all
            )

            if args.type == 'list' and value:

                async def del_last(trigger: HookTrigger):
                    if new_data := self.root.get_state(name, []):
                        new_data.pop()

                    self.root.update_state({name: new_data})

                    trigger.resolve()

                self.ui.register_hook(
                    MessageHook(
                        r"(-)",
                        checks=[lambda t: t.user.id == self.ui.renderer.author.id]
                    ), 
                    func=del_last
                )

            async def set_data(trigger: HookTrigger):
                data = trigger.data
                
                self.update_state(user=trigger.user.id)
                # this should be moved to self.set_data
                # to allow for combined use with list
                if options := args.options:
                    if data := find_item_in_array(
                        data, options.split(','), threshold=0.05
                    ):
                        self.set_data(trigger, name, data)
                    else:
                        raise InvalidEntry()
                else:
                    self.set_data(trigger, name, data, args)

                return True

                # trigger.resolve()
                
            self.ui.register_hook(
                MessageHook(
                    r"([^\-].+)",
                    checks=[lambda t: t.user.id == self.ui.renderer.author.id]
                ), 
                func=set_data
            )
        else:
            self.update_state(
                {
                    'active': 0
                }
            )
        self.root.entry_count += 1
        
        # this might not be 100% reliable
        if (args.show == 'active'
            ) and self.root.config.get('show') != 'always' and (
            self.root.entry_index != self.root.entry_count - 1
        ):
            return ""

        return self.content.format(
            *(await self.render_children())
        )

    def set_data(self, trigger, name, data, args):
        matches = {
            'tag': r"\<@!?([0-9]+?)\>",
            'role': r"<@&([0-9]+?)>",
            'channel': r"<#([0-9]+?)>",
        }
        ex = matches.get(args.match)

        if args.type == 'list':
            if ex:
                data = re.findall(ex, data)
            else:
                data = [data]

            new_data = self.root.get_state(name) or []
            # ensures cursor only moves if data has actually been added
            added = False
            for item in data:
                if args.repeat == 'none' and item in new_data:
                    continue
                new_data.append(item)
                added = True
                trigger.resolve()

            self.root.update_state({name: new_data})

            if not args.move == 'suppress' and added:
                self.root.next_entry()
        else:
            if not ex:
                self.root.update_state({name: data})

            elif match := re.fullmatch(ex, data, re.DOTALL):
                self.root.update_state({name: match[1]})

            else:
                trigger.resolve({'delete_input': False})
                return

            self.root.next_entry()
            trigger.resolve()



# sets/changes a root state variable
class SetTag(Tag):

    _config = TagConfig(
        name="set",
        args={
            "var": str,
            "value": Union(str, int, list)
        }
    )

    @on_render()
    async def render(self, args):
        self.root.update_state(
            {args.var: args.value}
        )
        # page flipping needs this to work but 
        # when outside conditional it causes infinte loop
        # self.root.double_render()


class DecorTag(Tag):

    _config = TagConfig(
        name="decor",
        args={
            "exp": Optional(bool, False),
            "op":  str,
            "ed":  str
        }
    )

    @on_render()
    async def render(self, args):
        out = await self.render_content()

        if args.exp:
            out = args.op + out + (args.cl or args.op[::-1])
        
        return out


        