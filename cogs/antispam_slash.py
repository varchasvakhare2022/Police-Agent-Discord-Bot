import discord
from discord import app_commands
from discord.ext import commands

class AntiSpamSlash(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="antispam", description="Configure anti-spam system")
    @app_commands.describe(
        action="Action to perform",
        value="Value for the action"
    )
    @app_commands.choices(action=[
        app_commands.Choice(name="status", value="status"),
        app_commands.Choice(name="enable", value="enable"),
        app_commands.Choice(name="disable", value="disable"),
        app_commands.Choice(name="threshold", value="threshold"),
        app_commands.Choice(name="logchannel", value="logchannel"),
    ])
    @app_commands.default_permissions(administrator=True)
    async def antispam_slash(
        self, 
        interaction: discord.Interaction, 
        action: str, 
        value: str = None
    ):
        """Configure anti-spam system with slash commands"""
        
        # Get anti-spam cog
        antispam_cog = self.bot.get_cog('AntiSpam')
        if not antispam_cog:
            await interaction.response.send_message("❌ Anti-spam system not loaded!", ephemeral=True)
            return
        
        if action == "status":
            embed = discord.Embed(
                title="🛡️ Anti-Spam System Status",
                color=0x00ff00 if antispam_cog.config.get("enabled", False) else 0xff0000
            )
            
            embed.add_field(
                name="Status",
                value="✅ Enabled" if antispam_cog.config.get("enabled", False) else "❌ Disabled",
                inline=True
            )
            
            embed.add_field(
                name="Spam Threshold",
                value=f"{antispam_cog.config.get('spam_threshold', 5)} messages/minute",
                inline=True
            )
            
            embed.add_field(
                name="Scam Detection",
                value="✅ Enabled" if antispam_cog.config.get("scam_detection", True) else "❌ Disabled",
                inline=True
            )
            
            embed.add_field(
                name="Auto Mute",
                value="✅ Enabled" if antispam_cog.config.get("auto_mute", True) else "❌ Disabled",
                inline=True
            )
            
            embed.add_field(
                name="Warning Threshold",
                value=f"{antispam_cog.config.get('warning_threshold', 3)} warnings",
                inline=True
            )
            
            embed.add_field(
                name="Mute Duration",
                value=f"{antispam_cog.config.get('mute_duration', 300)} seconds",
                inline=True
            )
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        elif action == "enable":
            antispam_cog.config["enabled"] = True
            antispam_cog.save_config()
            await interaction.response.send_message("✅ Anti-spam system enabled!", ephemeral=True)
            
        elif action == "disable":
            antispam_cog.config["enabled"] = False
            antispam_cog.save_config()
            await interaction.response.send_message("❌ Anti-spam system disabled!", ephemeral=True)
            
        elif action == "threshold":
            if not value:
                await interaction.response.send_message("❌ Please provide a threshold value!", ephemeral=True)
                return
            
            try:
                threshold = int(value)
                if threshold < 1 or threshold > 20:
                    await interaction.response.send_message("❌ Threshold must be between 1 and 20!", ephemeral=True)
                    return
                
                antispam_cog.config["spam_threshold"] = threshold
                antispam_cog.save_config()
                await interaction.response.send_message(f"✅ Spam threshold set to {threshold} messages per minute!", ephemeral=True)
            except ValueError:
                await interaction.response.send_message("❌ Please provide a valid number!", ephemeral=True)
                
        elif action == "logchannel":
            if not value:
                await interaction.response.send_message("❌ Please mention a channel!", ephemeral=True)
                return
            
            # Extract channel ID from mention
            channel_id = int(value.replace('<#', '').replace('>', ''))
            channel = self.bot.get_channel(channel_id)
            
            if not channel:
                await interaction.response.send_message("❌ Channel not found!", ephemeral=True)
                return
            
            antispam_cog.config["log_channel"] = channel.id
            antispam_cog.save_config()
            await interaction.response.send_message(f"✅ Anti-spam log channel set to {channel.mention}!", ephemeral=True)

    @app_commands.command(name="whitelist", description="Manage anti-spam whitelist")
    @app_commands.describe(
        action="Action to perform",
        role="Role to whitelist/unwhitelist"
    )
    @app_commands.choices(action=[
        app_commands.Choice(name="add", value="add"),
        app_commands.Choice(name="remove", value="remove"),
        app_commands.Choice(name="list", value="list"),
    ])
    @app_commands.default_permissions(administrator=True)
    async def whitelist_slash(
        self, 
        interaction: discord.Interaction, 
        action: str, 
        role: discord.Role = None
    ):
        """Manage anti-spam whitelist with slash commands"""
        
        # Get anti-spam cog
        antispam_cog = self.bot.get_cog('AntiSpam')
        if not antispam_cog:
            await interaction.response.send_message("❌ Anti-spam system not loaded!", ephemeral=True)
            return
        
        if action == "add":
            if not role:
                await interaction.response.send_message("❌ Please specify a role!", ephemeral=True)
                return
            
            if role.id not in antispam_cog.config.get("whitelist_roles", []):
                antispam_cog.config.setdefault("whitelist_roles", []).append(role.id)
                antispam_cog.save_config()
                await interaction.response.send_message(f"✅ {role.mention} added to anti-spam whitelist!", ephemeral=True)
            else:
                await interaction.response.send_message(f"❌ {role.mention} is already whitelisted!", ephemeral=True)
                
        elif action == "remove":
            if not role:
                await interaction.response.send_message("❌ Please specify a role!", ephemeral=True)
                return
            
            if role.id in antispam_cog.config.get("whitelist_roles", []):
                antispam_cog.config["whitelist_roles"].remove(role.id)
                antispam_cog.save_config()
                await interaction.response.send_message(f"✅ {role.mention} removed from anti-spam whitelist!", ephemeral=True)
            else:
                await interaction.response.send_message(f"❌ {role.mention} is not whitelisted!", ephemeral=True)
                
        elif action == "list":
            whitelisted_roles = antispam_cog.config.get("whitelist_roles", [])
            if not whitelisted_roles:
                await interaction.response.send_message("❌ No roles are whitelisted!", ephemeral=True)
                return
            
            embed = discord.Embed(
                title="🛡️ Anti-Spam Whitelist",
                color=0x00ff00
            )
            
            role_list = []
            for role_id in whitelisted_roles:
                role_obj = interaction.guild.get_role(role_id)
                if role_obj:
                    role_list.append(f"• {role_obj.mention}")
                else:
                    role_list.append(f"• Unknown Role (`{role_id}`)")
            
            embed.description = "\n".join(role_list)
            await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="reset-warnings", description="Reset spam warnings for a user")
    @app_commands.describe(member="Member to reset warnings for")
    @app_commands.default_permissions(administrator=True)
    async def reset_warnings_slash(self, interaction: discord.Interaction, member: discord.Member):
        """Reset spam warnings for a user"""
        
        # Get anti-spam cog
        antispam_cog = self.bot.get_cog('AntiSpam')
        if not antispam_cog:
            await interaction.response.send_message("❌ Anti-spam system not loaded!", ephemeral=True)
            return
        
        antispam_cog.user_warnings[member.id] = 0
        await interaction.response.send_message(f"✅ Spam warnings reset for {member.mention}!", ephemeral=True)

async def setup(bot):
    await bot.add_cog(AntiSpamSlash(bot))
