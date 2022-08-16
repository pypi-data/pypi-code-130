class create:
    """Create a file"""
    def __init__(self, filename:str) -> None:
        self.filename = filename
        
    def cog(self, type=1):
        """Create a cog(with discord.py v2.0)"""
        if type == 1:
            file=open(self.filename, 'wb')
            code = 'import discord\nfrom discord import app_commands\nfrom discord.ext import commands\n\nclass MyCog(commands.Cog):\n  def __init__(self, bot: commands.Bot) -> None:\n    self.bot = bot\n\n    @app_commands.command(name="command-1")\n    async def my_command(self, interaction: discord.Interaction) -> None:\n      """ /command-1 """\n      await interaction.response.send_message("Hello from command 1!", ephemeral=True)\n\n  @app_commands.command(name="command-2")\n  @app_commands.guilds(discord.Object(id=...), ...)\n  async def my_private_command(self, interaction: discord.Interaction) -> None:\n    """ /command-2 """\n    await interaction.response.send_message("Hello from private command!", ephemeral=True)\n\nasync def setup(bot: commands.Bot) -> None:\n  await bot.add_cog(MyCog(bot))'
            code = bytearray(code.encode())
            file.write(code)
            
        if type == 2:
            file = open(self.filename, 'wb')
            code = '# for simplicity, these commands are all global. You can add `guild=` or `guilds=` to `Bot.add_cog` in `setup` to add them to a guild.\n\nimport discord\nfrom discord import app_commands\nfrom discord.ext import commands\n\nclass MyCog(commands.GroupCog, name="parent"):\n  def __init__(self, bot: commands.Bot) -> None:\n    self.bot = bot\n    super().__init__()  # this is now required in this context.\n\n  @app_commands.command(name="sub-1")\n  async def my_sub_command_1(self, interaction: discord.Interaction) -> None:\n    """ /parent sub-1 """\n    await interaction.response.send_message("Hello from sub command 1", ephemeral=True)\n\n  @app_commands.command(name="sub-2")\n  async def my_sub_command_2(self, interaction: discord.Interaction) -> None:\n    """ /parent sub-2 """\n    await interaction.response.send_message("Hello from sub command 2", ephemeral=True)\n\nasync def setup(bot: commands.Bot) -> None:\n  await bot.add_cog(MyCog(bot))\n  # or if you want guild/guilds only...\n  await bot.add_cog(MyCog(bot), guilds=[discord.Object(id=...)])'
            code=bytearray(code.encode())
            file.write(code)
            
    def bot():
        """Create a bot(with discord.py v2.0)"""
        pass