import inspect
import asyncio
import discord
from discord.ext import commands

class Kick(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name="kick",
        aliases=["k"]
    )
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx: commands.Context, member: discord.Member, *, reason: str = "No reason provided") -> None:
        """Kick a user from the server"""
        
        # Check if trying to kick self
        if member == ctx.author:
            err1 = await ctx.send("Why are you so dumb?? Imagine kicking yourself")
            await ctx.message.delete()
            await asyncio.sleep(10)
            await err1.delete()
            return
        
        # Check role hierarchy
        if member.top_role >= ctx.author.top_role:
            err2 = await ctx.send("You're not high enough in the role hierarchy to do that.")
            await ctx.message.delete()
            await asyncio.sleep(10)
            await err2.delete()
            return
        
        # Check if trying to kick server owner
        if member == ctx.guild.owner:
            err3 = await ctx.send("Imagine you can kick the owner! LMAO...")
            await ctx.message.delete()
            await asyncio.sleep(10)
            await err3.delete()
            return
        
        try:
            # Kick the member
            await member.kick(reason=reason)
            
            # Log the action
            logging_cog = self.bot.get_cog('LoggingSystem')
            if logging_cog:
                await logging_cog.log_action("kick", ctx.author, member, reason, guild=ctx.guild)
            
            # Create embed
            embed = discord.Embed(
                title="User Kicked",
                description=inspect.cleandoc(
                    f"""
                    **Offender:** {member.display_name}
                    **Reason:** {reason}
                    **Responsible moderator:** {ctx.author.display_name}
                    """
                ),
                color=0xff8b8b
            )
            embed.set_footer(text=f"ID: {member.id}")
            
            await ctx.send(f"Successfully kicked {member.display_name}")
            await ctx.send(embed=embed)
            await ctx.message.delete()
            
        except discord.Forbidden:
            await ctx.reply("I don't have permission to kick this user!")
        except Exception as e:
            await ctx.reply(f"An error occurred while kicking the user: {str(e)}")

        
async def setup(bot):
    await bot.add_cog(Kick(bot))

