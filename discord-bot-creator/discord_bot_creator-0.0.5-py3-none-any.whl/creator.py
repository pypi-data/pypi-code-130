class create:
    """Create a file"""
    def __init__(self, filename:str) -> None:
        self.filename = filename
        
    def cog(self, type=1):
        """Create a cog(with discord.py v2.0)"""
        if type == 1:
            with open(self.filename) as file:
                code = 'import discord\nfrom discord import app_commands\nfrom discord.ext import commands\n\nclass MyCog(commands.Cog):\n  def __init__(self, bot: commands.Bot) -> None:\n    self.bot = bot\n\n    @app_commands.command(name="command-1")\n    async def my_command(self, interaction: discord.Interaction) -> None:\n      """ /command-1 """\n      await interaction.response.send_message("Hello from command 1!", ephemeral=True)\n\n  @app_commands.command(name="command-2")\n  @app_commands.guilds(discord.Object(id=...), ...)\n  async def my_private_command(self, interaction: discord.Interaction) -> None:\n    """ /command-2 """\n    await interaction.response.send_message("Hello from private command!", ephemeral=True)\n\nasync def setup(bot: commands.Bot) -> None:\n  await bot.add_cog(MyCog(bot))'
                code = bytearray(code.encode())
                file.write(code)
            
        if type == 2:
            with open(self.filename) as file:
                code = '# for simplicity, these commands are all global. You can add `guild=` or `guilds=` to `Bot.add_cog` in `setup` to add them to a guild.\n\nimport discord\nfrom discord import app_commands\nfrom discord.ext import commands\n\nclass MyCog(commands.GroupCog, name="parent"):\n  def __init__(self, bot: commands.Bot) -> None:\n    self.bot = bot\n    super().__init__()  # this is now required in this context.\n\n  @app_commands.command(name="sub-1")\n  async def my_sub_command_1(self, interaction: discord.Interaction) -> None:\n    """ /parent sub-1 """\n    await interaction.response.send_message("Hello from sub command 1", ephemeral=True)\n\n  @app_commands.command(name="sub-2")\n  async def my_sub_command_2(self, interaction: discord.Interaction) -> None:\n    """ /parent sub-2 """\n    await interaction.response.send_message("Hello from sub command 2", ephemeral=True)\n\nasync def setup(bot: commands.Bot) -> None:\n  await bot.add_cog(MyCog(bot))\n  # or if you want guild/guilds only...\n  await bot.add_cog(MyCog(bot), guilds=[discord.Object(id=...)])'
                code=bytearray(code.encode())
                file.write(code)
            
    def bot(self):
        """Create a bot(with discord.py v2.0)"""
        with open(self.filename, 'wb') as file:
            code = "from discord.ext import commands\nimport discord\nimport config\n\nclass Bot(commands.{base}):\n    def __init__(self, intents: discord.Intents, **kwargs):\n        super().__init__(command_prefix=commands.when_mentioned_or('{prefix}'), intents=intents, **kwargs)\n\n    async def setup_hook(self):\n        for cog in config.cogs:\n            try:\n                await self.load_extension(cog)\n            except Exception as exc:\n                print(f'Could not load extension {{cog}} due to {{exc.__class__.__name__}}: {{exc}}')\n\n    async def on_ready(self):\n        print(f'Logged on as {{self.user}} (ID: {{self.user.id}})')\n\n\nintents = discord.Intents.default()\nintents.message_content = True\nbot = Bot(intents=intents)\n\n# write general commands here\n\nbot.run(config.token)"
            code = bytearray(code.encode())
            file.write(code)
        file=open("config.py", "a")