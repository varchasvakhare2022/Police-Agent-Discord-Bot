import inspect

import discord
from discord import app_commands
from discord.ext import commands

MY_GUILD = discord.Object(id=760134264242700320)


class MyClient(discord.Client):
    def __init__(self, *, intents: discord.Intents, application_id: int):
        super().__init__(intents=intents, application_id=application_id)
        self.tree = app_commands.CommandTree(self)
    async def setup_hook(self):
        self.tree.copy_global_to(guild=MY_GUILD)
        await self.tree.sync(guild=MY_GUILD)

intents = discord.Intents.default()

client = MyClient(intents=intents, application_id=919149033820418059)

class Ping_Slash(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @client.tree.command()
    async def ping(self, interaction: discord.Interaction) -> None:
        """Check information about the bot."""
        
        embed = discord.Embed(
            title=f"Bot Statistics",
            description = inspect.cleandoc(
                f"""
                ・Latency - {str(round(self.bot.latency * 1000))}ms
                """
            ),
            color=0x9C84EF
        ).set_thumbnail(
            url='https://cdn.discordapp.com/attachments/870608893334659106/968156284845178901/959729564957958204.png'
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        
async def setup(bot):
    await bot.add_cog(Ping_Slash(bot))

