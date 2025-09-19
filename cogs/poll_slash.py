import inspect
from typing import Optional

import discord
from discord import app_commands
from discord.ext import commands

class Poll_Slash(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="poll")
    @app_commands.describe(question='enter question for the poll')
    async def poll(self, interaction: discord.Interaction, question: str) -> None:
        """Create a poll with slash command"""
        
        embed = discord.Embed(
            title=f'{interaction.user.name} asks',
            description=f'{question}', color=0x797EF6
        )
        embed.set_footer(text='react with any one option')
        message = await interaction.channel.send(embed=embed)
        await message.add_reaction('<a:yes:969908127145283594>')
        await message.add_reaction('<a:no:969908471451508766>')
        await interaction.response.send_message("Successfully posted your poll", ephemeral=True)
        
        
async def setup(bot):
    await bot.add_cog(Poll_Slash(bot))

