import inspect
import asyncio
import datetime
import calendar
import discord
import pytz
from discord.ext import commands

class Time(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name="time"
    )
    async def timeout(self, ctx: commands.Context) -> None:
        """Check the time"""
        
        year = datetime.datetime.now(tz=pytz.timezone('Asia/Kolkata')).year
        month = datetime.datetime.now(tz=pytz.timezone('Asia/Kolkata')).month
        day = datetime.datetime.now(tz=pytz.timezone('Asia/Kolkata')).day
        hour = datetime.datetime.now(tz=pytz.timezone('Asia/Kolkata')).hour
        minute = datetime.datetime.now(tz=pytz.timezone('Asia/Kolkata')).minute
        second = datetime.datetime.now(tz=pytz.timezone('Asia/Kolkata')).second
        
        epoch = datetime.datetime(year=year, month=month, day=day, hour=hour, minute=minute, second=second).timestamp()
        await ctx.reply(
            inspect.cleandoc(
                f"""
                Bot's current timezone is **IST.**
                The current time is: **{hour}:{minute}:{second}** {day}-{month}-{year} *Asia/Kolkata (UTC+05:30)**
                <t:{round(epoch)}>
                """
            )
        )

        
async def setup(bot):
    await bot.add_cog(Time(bot))

