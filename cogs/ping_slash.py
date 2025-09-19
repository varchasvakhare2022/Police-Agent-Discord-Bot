import inspect

import discord
from discord import app_commands
from discord.ext import commands

class Ping_Slash(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="ping")
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

