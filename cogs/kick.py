import inspect
import asyncio
import discord
from discord.ext import commands

class Kick(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name="kick"
    )
    @commands. has_permissions(kick_members=True)
    async def kick(self, ctx: commands.Context, member: discord.Member, *, reason=None) -> None:
        """Kick a user"""
        log_channel = discord.utils.get(ctx.guild.channels, id=970211808830967879)
        embed = discord.Embed(
            title="Kick",
            description = inspect.cleandoc(
                f"""
                **Offender:** {member.name}#{member.discriminator}
                **Reason:** {reason}
                **Responsible moderator:** {ctx.author.name}#{ctx.author.discriminator}
                """
            ),
            color=0xff8b8b
        )
        embed.set_footer(text=f"ID: {member.id}")
        if member == ctx.author:
            err1 = await ctx.send("Why are you so dumb?? Imagine kicking yourself")
            await ctx.message.delete()
            await asyncio.sleep(10)
            await err1.delete()
        elif member.top_role >= ctx.author.top_role:
            err2 = await ctx.send("You're not high enough in the role hierarchy to do that.")
            await ctx.message.delete()
            await asyncio.sleep(10)
            await err2.delete()
        elif member == ctx.guild.owner:
            err3 = await ctx.send("Imagine you can kick the owner! LMAO...")
            await ctx.message.delete()
            await asyncio.sleep(10)
            await err3.delete()
        else:
            if reason==None:
                reason="No reason provided"
                await ctx.guild.kick(member)
                await ctx.send(f"Successfully kicked {member.name}#{member.discriminator}")
                await log_channel.send(embed=embed)
                await ctx.message.delete()
            else:
                await ctx.guild.kick(member, reason=reason)
                await ctx.send(f"Successfully kicked {member.name}#{member.discriminator}")
                await log_channel.send(embed=embed)
                await ctx.message.delete()

        
async def setup(bot):
    await bot.add_cog(Kick(bot))

