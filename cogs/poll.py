from ast import Or
import inspect

import discord
from discord.ext import commands

class Poll(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name="poll"
    )
    @commands.check_any(
        commands.has_any_role(917120712840462416),
        commands.has_permissions(administrator=True)
    )
    async def poll(self, ctx: commands.Context, *, message) -> None:
        """Allows you to make a poll"""
        
        embed = discord.Embed(
            title=f'{ctx.message.author.name} asks',
            description=f'{message}', color=0x797EF6
        )
        embed.set_footer(text='react with any one option')
        message = await ctx.channel.send(embed=embed)
        await message.add_reaction('<a:yes:969908127145283594>')
        await message.add_reaction('<a:no:969908471451508766>')
        
async def setup(bot):
    await bot.add_cog(Poll(bot))

