import discord
from discord.ext import commands

class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(name="prefix", invoke_without_command=True)
    @commands.has_permissions(administrator=True)
    async def prefix(self, ctx: commands.Context, new_prefix: str = None):
        """Manage custom prefixes for this server"""
        if new_prefix is None:
            current_prefix = self.bot.storage.get_prefix(ctx.guild.id)
            embed = discord.Embed(
                title="Prefix Information",
                description=f"Current prefix: `{current_prefix}`\n\nUse `{current_prefix}prefix <new_prefix>` to change it.",
                color=0x00ff00
            )
            await ctx.send(embed=embed)
        else:
            if len(new_prefix) > 10:
                return await ctx.send("Prefix cannot be longer than 10 characters!")
            
            self.bot.storage.set_prefix(ctx.guild.id, new_prefix)
            
            # Log the action
            logging_cog = self.bot.get_cog('LoggingSystem')
            if logging_cog:
                await logging_cog.log_system_event("prefix_change", f"Server prefix changed to: `{new_prefix}`", ctx.guild, ctx.author, f"Old prefix: `{current_prefix}`")
            
            embed = discord.Embed(
                title="Prefix Updated",
                description=f"Server prefix changed to: `{new_prefix}`",
                color=0x00ff00
            )
            await ctx.send(embed=embed)

    @prefix.command(name="reset")
    @commands.has_permissions(administrator=True)
    async def prefix_reset(self, ctx: commands.Context):
        """Reset prefix to default"""
        self.bot.storage.remove_prefix(ctx.guild.id)
        embed = discord.Embed(
            title="Prefix Reset",
            description="Server prefix reset to default: `-`",
            color=0x00ff00
        )
        await ctx.send(embed=embed)

    @commands.group(name="blacklist", invoke_without_command=True)
    @commands.is_owner()
    async def blacklist(self, ctx: commands.Context, user: discord.User = None):
        """Manage user blacklist"""
        if user is None:
            blacklisted_users = self.bot.storage.get_blacklist()
            if not blacklisted_users:
                embed = discord.Embed(
                    title="Blacklist",
                    description="No users are currently blacklisted.",
                    color=0x00ff00
                )
            else:
                embed = discord.Embed(
                    title="Blacklisted Users",
                    description=f"**{len(blacklisted_users)}** users are blacklisted.",
                    color=0xff0000
                )
                # Show first 10 blacklisted users
                user_list = []
                for user_id in blacklisted_users[:10]:
                    try:
                        user_obj = await self.bot.fetch_user(user_id)
                        user_list.append(f"• {user_obj.display_name} (`{user_id}`)")
                    except:
                        user_list.append(f"• Unknown User (`{user_id}`)")
                
                embed.add_field(
                    name="Users",
                    value="\n".join(user_list) + ("\n..." if len(blacklisted_users) > 10 else ""),
                    inline=False
                )
            await ctx.send(embed=embed)
        else:
            if self.bot.storage.is_blacklisted(user.id):
                embed = discord.Embed(
                    title="User Already Blacklisted",
                    description=f"{user.display_name} is already blacklisted.",
                    color=0xff0000
                )
            else:
                self.bot.storage.add_to_blacklist(user.id)
                
                # Log the action
                logging_cog = self.bot.get_cog('LoggingSystem')
                if logging_cog:
                    await logging_cog.log_system_event("blacklist_add", f"{user.display_name} has been blacklisted from using the bot.", ctx.guild, ctx.author, f"User ID: {user.id}")
                
                embed = discord.Embed(
                    title="User Blacklisted",
                    description=f"{user.display_name} has been blacklisted from using the bot.",
                    color=0xff0000
                )
            await ctx.send(embed=embed)

    @blacklist.command(name="remove")
    @commands.is_owner()
    async def blacklist_remove(self, ctx: commands.Context, user: discord.User):
        """Remove user from blacklist"""
        if not self.bot.storage.is_blacklisted(user.id):
            embed = discord.Embed(
                title="User Not Blacklisted",
                description=f"{user.display_name} is not blacklisted.",
                color=0xff0000
            )
        else:
            self.bot.storage.remove_from_blacklist(user.id)
            embed = discord.Embed(
                title="User Removed from Blacklist",
                description=f"{user.display_name} has been removed from the blacklist.",
                color=0x00ff00
            )
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Admin(bot))
