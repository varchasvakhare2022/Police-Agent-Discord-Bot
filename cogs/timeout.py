import inspect
import asyncio
import datetime
import calendar
import discord
from discord.ext import commands

class Timeout(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name="timeout",
        aliases = ['to']
    )
    @commands.has_permissions(moderate_members=True)
    async def timeout(self, ctx: commands.Context, member: discord.Member, time=None, *, reason=None) -> None:
        """Timeout a user"""
        ##log_channel = discord.utils.get(ctx.guild.channels, id=970211808830967879)
        time_convert = {"s":1, "m":60, "h":3600,"d":86400}
        duration= int(time[0]) * time_convert[time[-1]]
        
        year = datetime.datetime.now().year
        month = datetime.datetime.now().month
        day = datetime.datetime.now().day
        hour = datetime.datetime.now().hour
        minute = datetime.datetime.now().minute
        second = datetime.datetime.now().second
        
        until = datetime.timedelta(seconds=duration)
        epoch = datetime.datetime(year=year, month=month, day=day, hour=hour, minute=minute, second=second).timestamp()
        embed = discord.Embed(
            title="Timeout",
            description = inspect.cleandoc(
                f"""
                **Offender:** {member.name}#{member.discriminator}
                **Duration** {time} <t:{round(epoch+duration)}>
                **Reason:** {reason}
                **Responsible moderator:** {ctx.author.name}#{ctx.author.discriminator}
                """
            ),
            color=0xff8b8b
        )
        embed.set_footer(text=f"ID: {member.id}")
        check_if = member.is_timed_out()
        if time == None:
            a = datetime.timedelta(seconds=0)
            await member.timeout(a)
        else:
            if check_if == False:
                await member.timeout(until, reason=reason)
                await ctx.send(embed=embed)
            elif check_if == True:
                await ctx.send("That user is already timed out. Too bad for them")

        
async def setup(bot):
    await bot.add_cog(Timeout(bot))

