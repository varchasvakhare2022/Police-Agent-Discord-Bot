import inspect
import asyncio
import discord
from discord.ext import commands

class Ban(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name="ban",
        aliases=["b"]
    )
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx: commands.Context, member: discord.Member, *, reason: str = "No reason provided") -> None:
        """Ban a user from the server"""
        
        # Check if trying to ban self
        if member == ctx.author:
            await ctx.reply("You can't ban yourself!")
            return
        
        # Check role hierarchy
        if member.top_role >= ctx.author.top_role:
            await ctx.reply("You're not high enough in the role hierarchy to do that.")
            return
        
        # Check if trying to ban server owner
        if member == ctx.guild.owner:
            await ctx.reply("You can't ban the server owner!")
            return
        
        try:
            # Ban the member
            await member.ban(reason=reason)
            
            # Log the action
            logging_cog = self.bot.get_cog('LoggingSystem')
            if logging_cog:
                await logging_cog.log_action("ban", ctx.author, member, reason, guild=ctx.guild)
            
            # Create embed
            embed = discord.Embed(
                title="User Banned",
                description=inspect.cleandoc(
                    f"""
                    **Offender:** {member.display_name}
                    **Reason:** {reason}
                    **Responsible moderator:** {ctx.author.display_name}
                    """
                ),
                color=0xff0000
            )
            embed.set_footer(text=f"ID: {member.id}")
            
            await ctx.send(f"Successfully banned {member.display_name}")
            await ctx.send(embed=embed)
            
        except discord.Forbidden:
            await ctx.reply("I don't have permission to ban this user!")
        except Exception as e:
            await ctx.reply(f"An error occurred while banning the user: {str(e)}")
    
    @commands.command(
        name="unban",
        aliases=["ub"]
    )
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx: commands.Context, user_id: int, *, reason: str = "No reason provided") -> None:
        """Unban a user from the server"""
        
        try:
            # Get banned user
            banned_user = await ctx.guild.fetch_ban(discord.Object(id=user_id))
            user = banned_user.user
            
            # Unban the user
            await ctx.guild.unban(user, reason=reason)
            
            # Log the action
            logging_cog = self.bot.get_cog('LoggingSystem')
            if logging_cog:
                await logging_cog.log_action("unban", ctx.author, user, reason, guild=ctx.guild)
            
            # Create embed
            embed = discord.Embed(
                title="User Unbanned",
                description=inspect.cleandoc(
                    f"""
                    **User:** {user.display_name}
                    **Reason:** {reason}
                    **Responsible moderator:** {ctx.author.display_name}
                    """
                ),
                color=0x00ff00
            )
            embed.set_footer(text=f"ID: {user.id}")
            
            await ctx.send(f"Successfully unbanned {user.display_name}")
            await ctx.send(embed=embed)
            
        except discord.NotFound:
            await ctx.reply("User is not banned or doesn't exist!")
        except discord.Forbidden:
            await ctx.reply("I don't have permission to unban this user!")
        except Exception as e:
            await ctx.reply(f"An error occurred while unbanning the user: {str(e)}")
    
    @commands.command(
        name="banlist",
        aliases=["bans"]
    )
    @commands.has_permissions(ban_members=True)
    async def banlist(self, ctx: commands.Context):
        """Show list of banned users"""
        
        try:
            bans = await ctx.guild.bans()
            
            if not bans:
                await ctx.reply("No users are currently banned.")
                return
            
            embed = discord.Embed(
                title="Banned Users",
                description=f"**{len(bans)}** users are banned from this server.",
                color=0xff0000
            )
            
            # Show first 10 banned users
            ban_list = []
            for ban_entry in bans[:10]:
                user = ban_entry.user
                reason = ban_entry.reason or "No reason provided"
                ban_list.append(f"• **{user.display_name}** (`{user.id}`)\n  Reason: {reason}")
            
            embed.add_field(
                name="Banned Users",
                value="\n".join(ban_list) + ("\n..." if len(bans) > 10 else ""),
                inline=False
            )
            
            await ctx.send(embed=embed)
            
        except discord.Forbidden:
            await ctx.reply("I don't have permission to view the ban list!")
        except Exception as e:
            await ctx.reply(f"An error occurred while fetching the ban list: {str(e)}")

async def setup(bot):
    await bot.add_cog(Ban(bot))
