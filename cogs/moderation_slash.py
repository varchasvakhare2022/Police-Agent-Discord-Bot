import discord
from discord import app_commands
from discord.ext import commands
import inspect
import datetime

class ModerationSlash(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="kick", description="Kick a user from the server")
    @app_commands.describe(
        member="The member to kick",
        reason="Reason for the kick"
    )
    @app_commands.default_permissions(kick_members=True)
    async def kick_slash(
        self, 
        interaction: discord.Interaction, 
        member: discord.Member, 
        reason: str = "No reason provided"
    ) -> None:
        """Kick a user with slash command"""
        
        # Check command scope
        scopes_cog = self.bot.get_cog('CommandScopes')
        if scopes_cog:
            allowed_roles = scopes_cog.get_command_scope(interaction.guild.id, 'kick')
            if allowed_roles:
                user_roles = [role.id for role in interaction.user.roles]
                if not any(role_id in user_roles for role_id in allowed_roles):
                    await interaction.response.send_message("❌ You don't have permission to use this command!", ephemeral=True)
                    return
        
        # Check if trying to kick self
        if member == interaction.user:
            await interaction.response.send_message("You can't kick yourself!", ephemeral=True)
            return
        
        # Check role hierarchy
        if member.top_role >= interaction.user.top_role:
            await interaction.response.send_message("You're not high enough in the role hierarchy to do that.", ephemeral=True)
            return
        
        # Check if trying to kick server owner
        if member == interaction.guild.owner:
            await interaction.response.send_message("You can't kick the server owner!", ephemeral=True)
            return
        
        try:
            # Kick the member
            await member.kick(reason=reason)
            
            # Log the action
            logging_cog = self.bot.get_cog('LoggingSystem')
            if logging_cog:
                await logging_cog.log_action("kick", interaction.user, member, reason, guild=interaction.guild)
            
            # Create embed
            embed = discord.Embed(
                title="User Kicked",
                description=inspect.cleandoc(
                    f"""
                    **Offender:** {member.display_name}
                    **Reason:** {reason}
                    **Responsible moderator:** {interaction.user.display_name}
                    """
                ),
                color=0xff8b8b
            )
            embed.set_footer(text=f"ID: {member.id}")
            
            await interaction.response.send_message(embed=embed)
            
        except discord.Forbidden:
            await interaction.response.send_message("I don't have permission to kick this user!", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"An error occurred while kicking the user: {str(e)}", ephemeral=True)

    @app_commands.command(name="ban", description="Ban a user from the server")
    @app_commands.describe(
        member="The member to ban",
        reason="Reason for the ban"
    )
    @app_commands.default_permissions(ban_members=True)
    async def ban_slash(
        self, 
        interaction: discord.Interaction, 
        member: discord.Member, 
        reason: str = "No reason provided"
    ) -> None:
        """Ban a user with slash command"""
        
        # Check command scope
        scopes_cog = self.bot.get_cog('CommandScopes')
        if scopes_cog:
            allowed_roles = scopes_cog.get_command_scope(interaction.guild.id, 'ban')
            if allowed_roles:
                user_roles = [role.id for role in interaction.user.roles]
                if not any(role_id in user_roles for role_id in allowed_roles):
                    await interaction.response.send_message("❌ You don't have permission to use this command!", ephemeral=True)
                    return
        
        # Check if trying to ban self
        if member == interaction.user:
            await interaction.response.send_message("You can't ban yourself!", ephemeral=True)
            return
        
        # Check role hierarchy
        if member.top_role >= interaction.user.top_role:
            await interaction.response.send_message("You're not high enough in the role hierarchy to do that.", ephemeral=True)
            return
        
        # Check if trying to ban server owner
        if member == interaction.guild.owner:
            await interaction.response.send_message("You can't ban the server owner!", ephemeral=True)
            return
        
        try:
            # Ban the member
            await member.ban(reason=reason)
            
            # Log the action
            logging_cog = self.bot.get_cog('LoggingSystem')
            if logging_cog:
                await logging_cog.log_action("ban", interaction.user, member, reason, guild=interaction.guild)
            
            # Create embed
            embed = discord.Embed(
                title="User Banned",
                description=inspect.cleandoc(
                    f"""
                    **Offender:** {member.display_name}
                    **Reason:** {reason}
                    **Responsible moderator:** {interaction.user.display_name}
                    """
                ),
                color=0xff0000
            )
            embed.set_footer(text=f"ID: {member.id}")
            
            await interaction.response.send_message(embed=embed)
            
        except discord.Forbidden:
            await interaction.response.send_message("I don't have permission to ban this user!", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"An error occurred while banning the user: {str(e)}", ephemeral=True)

    @app_commands.command(name="timeout", description="Timeout a user")
    @app_commands.describe(
        member="The member to timeout",
        duration="Duration (e.g., 5m, 1h, 2d)",
        reason="Reason for the timeout"
    )
    @app_commands.default_permissions(moderate_members=True)
    async def timeout_slash(
        self, 
        interaction: discord.Interaction, 
        member: discord.Member, 
        duration: str, 
        reason: str = "No reason provided"
    ) -> None:
        """Timeout a user with slash command"""
        
        # Check if trying to timeout self
        if member == interaction.user:
            await interaction.response.send_message("You can't timeout yourself!", ephemeral=True)
            return
        
        # Check role hierarchy
        if member.top_role >= interaction.user.top_role:
            await interaction.response.send_message("You're not high enough in the role hierarchy to do that.", ephemeral=True)
            return
        
        # Check if trying to timeout server owner
        if member == interaction.guild.owner:
            await interaction.response.send_message("You can't timeout the server owner!", ephemeral=True)
            return
        
        # Check if user is already timed out
        if member.is_timed_out():
            await interaction.response.send_message("That user is already timed out.", ephemeral=True)
            return
        
        try:
            # Parse duration
            time_convert = {"s": 1, "m": 60, "h": 3600, "d": 86400}
            
            if len(duration) < 2:
                await interaction.response.send_message("Invalid duration format! Use: 5s, 5m, 5h, or 5d", ephemeral=True)
                return
            
            duration_seconds = int(duration[:-1]) * time_convert.get(duration[-1], 1)
            
            if duration_seconds > 2419200:  # 28 days max
                await interaction.response.send_message("Timeout duration cannot exceed 28 days!", ephemeral=True)
                return
            
            # Apply timeout
            until = datetime.timedelta(seconds=duration_seconds)
            await member.timeout(until, reason=reason)
            
            # Log the action
            logging_cog = self.bot.get_cog('LoggingSystem')
            if logging_cog:
                await logging_cog.log_action("timeout", interaction.user, member, reason, duration, guild=interaction.guild)
            
            # Create embed
            embed = discord.Embed(
                title="User Timed Out",
                description=inspect.cleandoc(
                    f"""
                    **Offender:** {member.display_name}
                    **Duration:** {duration} (<t:{round(datetime.datetime.now().timestamp() + duration_seconds)}:R>)
                    **Reason:** {reason}
                    **Responsible moderator:** {interaction.user.display_name}
                    """
                ),
                color=0xff8b8b
            )
            embed.set_footer(text=f"ID: {member.id}")
            
            await interaction.response.send_message(embed=embed)
            
        except ValueError:
            await interaction.response.send_message("Invalid duration format! Use: 5s, 5m, 5h, or 5d", ephemeral=True)
        except discord.Forbidden:
            await interaction.response.send_message("I don't have permission to timeout this user!", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"An error occurred while timing out the user: {str(e)}", ephemeral=True)

    @app_commands.command(name="untimeout", description="Remove timeout from a user")
    @app_commands.describe(
        member="The member to remove timeout from",
        reason="Reason for removing timeout"
    )
    @app_commands.default_permissions(moderate_members=True)
    async def untimeout_slash(
        self, 
        interaction: discord.Interaction, 
        member: discord.Member, 
        reason: str = "No reason provided"
    ) -> None:
        """Remove timeout from a user with slash command"""
        
        # Check if user is not timed out
        if not member.is_timed_out():
            await interaction.response.send_message("That user is not timed out!", ephemeral=True)
            return
        
        try:
            # Remove timeout
            await member.timeout(None, reason=reason)
            
            # Log the action
            logging_cog = self.bot.get_cog('LoggingSystem')
            if logging_cog:
                await logging_cog.log_action("untimeout", interaction.user, member, reason, guild=interaction.guild)
            
            # Create embed
            embed = discord.Embed(
                title="Timeout Removed",
                description=inspect.cleandoc(
                    f"""
                    **User:** {member.display_name}
                    **Reason:** {reason}
                    **Responsible moderator:** {interaction.user.display_name}
                    """
                ),
                color=0x00ff00
            )
            embed.set_footer(text=f"ID: {member.id}")
            
            await interaction.response.send_message(embed=embed)
            
        except discord.Forbidden:
            await interaction.response.send_message("I don't have permission to remove timeout from this user!", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"An error occurred while removing timeout: {str(e)}", ephemeral=True)

    @app_commands.command(name="unban", description="Unban a user from the server")
    @app_commands.describe(
        user_id="The user ID to unban",
        reason="Reason for the unban"
    )
    @app_commands.default_permissions(ban_members=True)
    async def unban_slash(
        self, 
        interaction: discord.Interaction, 
        user_id: str, 
        reason: str = "No reason provided"
    ) -> None:
        """Unban a user with slash command"""
        
        try:
            user_id = int(user_id)
            
            # Get banned user
            banned_user = await interaction.guild.fetch_ban(discord.Object(id=user_id))
            user = banned_user.user
            
            # Unban the user
            await interaction.guild.unban(user, reason=reason)
            
            # Log the action
            logging_cog = self.bot.get_cog('LoggingSystem')
            if logging_cog:
                await logging_cog.log_action("unban", interaction.user, user, reason, guild=interaction.guild)
            
            # Create embed
            embed = discord.Embed(
                title="User Unbanned",
                description=inspect.cleandoc(
                    f"""
                    **User:** {user.display_name}
                    **Reason:** {reason}
                    **Responsible moderator:** {interaction.user.display_name}
                    """
                ),
                color=0x00ff00
            )
            embed.set_footer(text=f"ID: {user.id}")
            
            await interaction.response.send_message(embed=embed)
            
        except ValueError:
            await interaction.response.send_message("Invalid user ID! Please provide a valid user ID.", ephemeral=True)
        except discord.NotFound:
            await interaction.response.send_message("User is not banned or doesn't exist!", ephemeral=True)
        except discord.Forbidden:
            await interaction.response.send_message("I don't have permission to unban this user!", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"An error occurred while unbanning the user: {str(e)}", ephemeral=True)

    @app_commands.command(name="banlist", description="Show list of banned users")
    @app_commands.default_permissions(ban_members=True)
    async def banlist_slash(self, interaction: discord.Interaction):
        """Show banned users with slash command"""
        
        try:
            bans = await interaction.guild.bans()
            
            if not bans:
                await interaction.response.send_message("No users are currently banned.", ephemeral=True)
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
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except discord.Forbidden:
            await interaction.response.send_message("I don't have permission to view the ban list!", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"An error occurred while fetching the ban list: {str(e)}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(ModerationSlash(bot))
