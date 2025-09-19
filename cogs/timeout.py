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
        aliases=['to']
    )
    @commands.has_permissions(moderate_members=True)
    async def timeout(self, ctx: commands.Context, member: discord.Member, time: str, *, reason: str = "No reason provided") -> None:
        """Timeout a user for a specified duration"""
        
        # Check if trying to timeout self
        if member == ctx.author:
            await ctx.reply("You can't timeout yourself!")
            return
        
        # Check role hierarchy
        if member.top_role >= ctx.author.top_role:
            await ctx.reply("You're not high enough in the role hierarchy to do that.")
            return
        
        # Check if trying to timeout server owner
        if member == ctx.guild.owner:
            await ctx.reply("You can't timeout the server owner!")
            return
        
        # Check if user is already timed out
        if member.is_timed_out():
            await ctx.reply("That user is already timed out. Too bad for them")
            return
        
        try:
            # Parse time duration
            time_convert = {"s": 1, "m": 60, "h": 3600, "d": 86400}
            
            if not time or len(time) < 2:
                await ctx.reply("Invalid time format! Use: 5s, 5m, 5h, or 5d")
                return
            
            duration = int(time[:-1]) * time_convert.get(time[-1], 1)
            
            if duration > 2419200:  # 28 days max
                await ctx.reply("Timeout duration cannot exceed 28 days!")
                return
            
            until = datetime.timedelta(seconds=duration)
            
            # Apply timeout
            await member.timeout(until, reason=reason)
            
            # Log the action
            logging_cog = self.bot.get_cog('LoggingSystem')
            if logging_cog:
                await logging_cog.log_action("timeout", ctx.author, member, reason, time, guild=ctx.guild)
            
            # Create embed
            embed = discord.Embed(
                title="User Timed Out",
                description=inspect.cleandoc(
                    f"""
                    **Offender:** {member.display_name}
                    **Duration:** {time} (<t:{round(datetime.datetime.now().timestamp() + duration)}:R>)
                    **Reason:** {reason}
                    **Responsible moderator:** {ctx.author.display_name}
                    """
                ),
                color=0xff8b8b
            )
            embed.set_footer(text=f"ID: {member.id}")
            
            await ctx.send(embed=embed)
            
        except ValueError:
            await ctx.reply("Invalid time format! Use: 5s, 5m, 5h, or 5d")
        except discord.Forbidden:
            await ctx.reply("I don't have permission to timeout this user!")
        except Exception as e:
            await ctx.reply(f"An error occurred while timing out the user: {str(e)}")
    
    @commands.command(
        name="untimeout",
        aliases=['unto']
    )
    @commands.has_permissions(moderate_members=True)
    async def untimeout(self, ctx: commands.Context, member: discord.Member, *, reason: str = "No reason provided") -> None:
        """Remove timeout from a user"""
        
        # Check if user is not timed out
        if not member.is_timed_out():
            await ctx.reply("That user is not timed out!")
            return
        
        try:
            # Remove timeout
            await member.timeout(None, reason=reason)
            
            # Log the action
            logging_cog = self.bot.get_cog('LoggingSystem')
            if logging_cog:
                await logging_cog.log_action("untimeout", ctx.author, member, reason, guild=ctx.guild)
            
            # Create embed
            embed = discord.Embed(
                title="Timeout Removed",
                description=inspect.cleandoc(
                    f"""
                    **User:** {member.display_name}
                    **Reason:** {reason}
                    **Responsible moderator:** {ctx.author.display_name}
                    """
                ),
                color=0x00ff00
            )
            embed.set_footer(text=f"ID: {member.id}")
            
            await ctx.send(embed=embed)
            
        except discord.Forbidden:
            await ctx.reply("I don't have permission to remove timeout from this user!")
        except Exception as e:
            await ctx.reply(f"An error occurred while removing timeout: {str(e)}")

        
async def setup(bot):
    await bot.add_cog(Timeout(bot))

