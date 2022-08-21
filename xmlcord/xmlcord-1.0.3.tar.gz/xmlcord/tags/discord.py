import discord

from discord import Embed
from datetime import datetime

from .base import Tag, on_render, TagConfig, Optional

from ..hooks import ReactionHook, HookTrigger


EMOJIS = {
    'up': "⬆",
    'down': "⬇",
    'checkmark': "✅",
    'cross': "<:red_cross_5:744249221011472444>",
    'file': "📁"
}


class Message(Tag):

    _config = TagConfig(name="message")

    def add_reaction(self, emoji, event=None):
        self.reactions.append(emoji)

    @on_render()
    async def render(self, args):
        self.embed = None
        self.reactions = []
        self.message = await self.render_content()


class EmbedTag(Tag):

    _config = TagConfig(
        name="embed",
        content=False
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # this might eventually cause issues,
        # might be best to create separate API for managing embeds
        self.embed = discord.Embed()

    @on_render()
    async def render(self, args):
        self.embed.clear_fields()
        self.reactions = []
        await self.render_children()
        
        self.first_ancestor('message').embed = self.embed

        return ""


class DescriptionTag(Tag):

    _config = TagConfig(name="description", content=False)

    @on_render()
    async def render(self, args):
        descption = await self.render_content()
        self.first_ancestor("embed").embed.description = descption 


class TitleTag(Tag):

    _config = TagConfig(name="title", content=False)

    @on_render()
    async def render(self, args):
        title = await self.render_content()  
        self.first_ancestor("embed").embed.title = title
        

class ColorTag(Tag):

    _config = TagConfig(
        name="color",
        args={
            "value": str
        }
    )

    @on_render()
    async def render(self, args):
        self.first_ancestor("embed").embed.color = int(args.value, 16)


class FieldTag(Tag):

    _config = TagConfig(
        name="field",
        args={
            "name":   str,
            "inline": Optional(bool, False)
        }
    )

    @on_render()
    async def render(self, args):
        self.first_ancestor("embed").embed.add_field(
            name=args.name, 
            inline=args.inline, 
            value=await self.render_content()
        )


class ImageTag(Tag):

    _config = TagConfig(
        name="image",
        args={
            "url":   str,
        }
    )

    @on_render()
    async def render(self, args):
        self.first_ancestor("embed").embed.set_image(url=args.url)


class ThumbnailTag(Tag):

    _config = TagConfig(
        name="thumbnail",
        args={
            "url":   str,
        }
    )

    @on_render()
    async def render(self, args):
        self.first_ancestor("embed").embed.set_thumbnail(url=args.url)


class FooterTag(Tag):

    _config = TagConfig(
        name="footer",
        args={
            "url": Optional(str, ""),
        }
    )

    @on_render()
    async def render(self, args):
        self.first_ancestor("embed").embed.set_footer(
            icon_url=args.url, 
            text=await self.render_content()
        )


class TimestampTag(Tag):

    _config = TagConfig(
        name="timestamp",
        args={
            "value": int
        }
    )

    @on_render()
    async def render(self, args):
        ts = datetime.fromtimestamp(args.value)
        self.first_ancestor("embed").embed.timestamp = ts


class CodeTag(Tag):

    _config = TagConfig(
        name="code", 
        args={
            "lang": Optional(str, "")
        }
    )

    @on_render()
    async def render(self, args):
        content = await self.render_content()
        return f"```{args.lang}\n{content}```"


class ReactionTag(Tag):

    _config = TagConfig(
        name="r",
        args={
            "emoji": str
        }
    )
    
    async def on_reaction(self, trigger: HookTrigger):
        self.update_state({
            'value': 1,
            'user': trigger.user.id
        })
        trigger.resolve()

    @on_render()
    async def render(self, args):

        emoji = EMOJIS[args.emoji]
        
        self.first_ancestor('message').add_reaction(emoji)

        self.ui.register_hook(
            ReactionHook(
                emoji,
                checks=[lambda t: t.user.id == self.ui.renderer.author.id]
            ), 
            func=self.on_reaction
        )

        if self.get_state('value') == 1:
            self.update_state(value=0)

            await self.render_children()


class UserContextTag(Tag):

    _config = TagConfig(
        name="userContext",
        args={
            "id": int
        }
    )

    @on_render()
    async def render(self, args):
        context = self.ui.renderer.context

        member = await context.guild.fetch_member(args.id)

        self.update_state({
            'name':       member.name,
            'nick':       member.nick,
            'roles':      [r.id for r in member.roles],
            'avatar_url': member.avatar_url
        })
        return await self.render_content()


class ClassifiedTag(Tag):

    _config = TagConfig(
        name="c",
        args={
            "role": str
        }
    )

    @on_render()
    async def render(self, args):
        context = self.ui.renderer.context
        member = context.author

        if int(args.role) in [r.id for r in member.roles]:
            return await self.render_content()
        else:
            return '\n[ REDACTED ]'
