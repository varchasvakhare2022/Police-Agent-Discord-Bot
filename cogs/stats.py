import inspect

import discord
from discord.ext import commands

class Stats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name="stats", aliases = ["statistics", "ping", "botinfo"]
    )
    async def stats(self, ctx: commands.Context) -> None:
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
        await ctx.send(embed=embed)
        
async def setup(bot):
    await bot.add_cog(Stats(bot))

