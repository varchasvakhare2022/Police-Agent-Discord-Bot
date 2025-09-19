import discord
from discord.ext import commands
import json
import os
import time
from datetime import datetime, timedelta
import inspect

class ServerSecurity(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.security_file = "data/server_security.json"
        self.scam_domains_file = "data/scam_domains.json"
        self.load_data()

    def load_data(self):
        """Load security configuration and scam domains"""
        try:
            if os.path.exists(self.security_file):
                with open(self.security_file, 'r') as f:
                    self.security_config = json.load(f)
            else:
                self.security_config = {}
                self.save_security_config()
        except Exception as e:
            print(f"Error loading security config: {e}")
            self.security_config = {}

        try:
            if os.path.exists(self.scam_domains_file):
                with open(self.scam_domains_file, 'r') as f:
                    self.scam_domains = json.load(f)
            else:
                self.scam_domains = {
                    "domains": [
                        "discord-nitro.com",
                        "discord-gift.com",
                        "discordapp.com-gift.com",
                        "discord-gifts.com",
                        "discord-nitro-gift.com",
                        "discord-steam.com",
                        "discord-roblox.com",
                        "discord-minecraft.com",
                        "discord-free.com",
                        "discord-premium.com"
                    ],
                    "enabled": True
                }
                self.save_scam_domains()
        except Exception as e:
            print(f"Error loading scam domains: {e}")
            self.scam_domains = {"domains": [], "enabled": True}

    def save_security_config(self):
        """Save security configuration"""
        try:
            os.makedirs("data", exist_ok=True)
            with open(self.security_file, 'w') as f:
                json.dump(self.security_config, f, indent=2)
        except Exception as e:
            print(f"Error saving security config: {e}")

    def save_scam_domains(self):
        """Save scam domains list"""
        try:
            os.makedirs("data", exist_ok=True)
            with open(self.scam_domains_file, 'w') as f:
                json.dump(self.scam_domains, f, indent=2)
        except Exception as e:
            print(f"Error saving scam domains: {e}")

    @commands.command(name="lockdown")
    @commands.has_permissions(administrator=True)
    async def lockdown(self, ctx: commands.Context, *, reason: str = "Server lockdown"):
        """Lock all channels instantly during a raid"""
        
        # Check if user has high enough permissions
        if not ctx.author.guild_permissions.administrator:
            await ctx.reply("❌ This command requires Administrator permissions!")
            return
        
        # Create confirmation embed
        embed = discord.Embed(
            title="🚨 Server Lockdown Confirmation",
            description="Are you sure you want to lock down the entire server?",
            color=0xff0000
        )
        embed.add_field(
            name="📋 Details",
            value=f"**Reason:** {reason}\n**Channels:** All text channels\n**Effect:** No one can send messages",
            inline=False
        )
        embed.add_field(
            name="⚠️ Warning",
            value="This will lock ALL channels! Use `-unlockdown` to reverse.",
            inline=False
        )
        
        # Create confirmation view
        view = LockdownConfirmView(ctx, reason)
        await ctx.send(embed=embed, view=view)

    @commands.command(name="unlockdown")
    @commands.has_permissions(administrator=True)
    async def unlockdown(self, ctx: commands.Context):
        """Unlock all channels after lockdown"""
        
        # Check if user has high enough permissions
        if not ctx.author.guild_permissions.administrator:
            await ctx.reply("❌ This command requires Administrator permissions!")
            return
        
        # Create confirmation embed
        embed = discord.Embed(
            title="🔓 Server Unlockdown Confirmation",
            description="Are you sure you want to unlock the entire server?",
            color=0x00ff00
        )
        embed.add_field(
            name="📋 Details",
            value="**Channels:** All text channels\n**Effect:** Everyone can send messages again",
            inline=False
        )
        
        # Create confirmation view
        view = UnlockdownConfirmView(ctx)
        await ctx.send(embed=embed, view=view)

    @commands.command(name="scam-domains")
    @commands.has_permissions(administrator=True)
    async def scam_domains(self, ctx: commands.Context, action: str = None, *, domain: str = None):
        """Manage scam domain blocking"""
        
        if not action:
            # Show current domains
            embed = discord.Embed(
                title="🚫 Scam Domain Blocking",
                color=0x9C84EF
            )
            embed.add_field(
                name="Status",
                value="✅ Enabled" if self.scam_domains["enabled"] else "❌ Disabled",
                inline=True
            )
            embed.add_field(
                name="Total Domains",
                value=str(len(self.scam_domains["domains"])),
                inline=True
            )
            
            if self.scam_domains["domains"]:
                embed.add_field(
                    name="Blocked Domains",
                    value="\n".join([f"• {d}" for d in self.scam_domains["domains"][:10]]) + 
                          (f"\n... and {len(self.scam_domains['domains']) - 10} more" if len(self.scam_domains["domains"]) > 10 else ""),
                    inline=False
                )
            
            await ctx.send(embed=embed)
            return
        
        if action == "add":
            if not domain:
                await ctx.reply("❌ Please provide a domain to add!")
                return
            
            if domain in self.scam_domains["domains"]:
                await ctx.reply(f"❌ Domain `{domain}` is already blocked!")
                return
            
            self.scam_domains["domains"].append(domain)
            self.save_scam_domains()
            
            embed = discord.Embed(
                title="✅ Domain Added",
                description=f"`{domain}` has been added to the scam domain list",
                color=0x00ff00
            )
            await ctx.send(embed=embed)
        
        elif action == "remove":
            if not domain:
                await ctx.reply("❌ Please provide a domain to remove!")
                return
            
            if domain not in self.scam_domains["domains"]:
                await ctx.reply(f"❌ Domain `{domain}` is not in the blocked list!")
                return
            
            self.scam_domains["domains"].remove(domain)
            self.save_scam_domains()
            
            embed = discord.Embed(
                title="✅ Domain Removed",
                description=f"`{domain}` has been removed from the scam domain list",
                color=0x00ff00
            )
            await ctx.send(embed=embed)
        
        elif action == "enable":
            self.scam_domains["enabled"] = True
            self.save_scam_domains()
            
            embed = discord.Embed(
                title="✅ Scam Domain Blocking Enabled",
                description="Scam domain blocking is now active",
                color=0x00ff00
            )
            await ctx.send(embed=embed)
        
        elif action == "disable":
            self.scam_domains["enabled"] = False
            self.save_scam_domains()
            
            embed = discord.Embed(
                title="❌ Scam Domain Blocking Disabled",
                description="Scam domain blocking is now inactive",
                color=0xff0000
            )
            await ctx.send(embed=embed)
        
        else:
            await ctx.reply("❌ Valid actions: add, remove, enable, disable")

    @commands.command(name="anti-alt")
    @commands.has_permissions(administrator=True)
    async def anti_alt(self, ctx: commands.Context, action: str = None, *, value: str = None):
        """Configure anti-alt detection"""
        
        if not action:
            # Show current configuration
            embed = discord.Embed(
                title="🔍 Anti-Alt Detection",
                color=0x9C84EF
            )
            embed.add_field(
                name="Status",
                value="✅ Enabled" if self.security_config.get("anti_alt_enabled", False) else "❌ Disabled",
                inline=True
            )
            embed.add_field(
                name="Detection Method",
                value=self.security_config.get("anti_alt_method", "Username similarity"),
                inline=True
            )
            embed.add_field(
                name="Action",
                value=self.security_config.get("anti_alt_action", "kick"),
                inline=True
            )
            
            await ctx.send(embed=embed)
            return
        
        if action == "enable":
            self.security_config["anti_alt_enabled"] = True
            self.save_security_config()
            
            embed = discord.Embed(
                title="✅ Anti-Alt Detection Enabled",
                description="Anti-alt detection is now active",
                color=0x00ff00
            )
            await ctx.send(embed=embed)
        
        elif action == "disable":
            self.security_config["anti_alt_enabled"] = False
            self.save_security_config()
            
            embed = discord.Embed(
                title="❌ Anti-Alt Detection Disabled",
                description="Anti-alt detection is now inactive",
                color=0xff0000
            )
            await ctx.send(embed=embed)
        
        elif action == "action":
            if value in ["kick", "ban", "timeout"]:
                self.security_config["anti_alt_action"] = value
                self.save_security_config()
                
                embed = discord.Embed(
                    title="✅ Anti-Alt Action Updated",
                    description=f"Anti-alt action set to: {value}",
                    color=0x00ff00
                )
                await ctx.send(embed=embed)
            else:
                await ctx.reply("❌ Valid actions: kick, ban, timeout")
        
        else:
            await ctx.reply("❌ Valid actions: enable, disable, action")

    @commands.Cog.listener()
    async def on_message(self, message):
        """Check messages for scam domains"""
        if message.author.bot or not message.guild:
            return
        
        if not self.scam_domains["enabled"]:
            return
        
        # Check for scam domains
        content = message.content.lower()
        for domain in self.scam_domains["domains"]:
            if domain in content:
                await self.handle_scam_domain(message, domain)

    async def handle_scam_domain(self, message, domain):
        """Handle detected scam domain"""
        # Delete the message
        try:
            await message.delete()
        except:
            pass
        
        # Timeout the user
        try:
            until = timedelta(minutes=10)
            await message.author.timeout(until, reason=f"Scam domain detected: {domain}")
        except:
            pass
        
        # Log the action
        logging_cog = self.bot.get_cog('DetailedModLogs')
        if logging_cog:
            await logging_cog.log_mod_action(
                message.guild,
                "scam_domain",
                message.guild.me,
                message.author,
                f"Scam domain detected: {domain}",
                "10m"
            )
        
        # Send alert
        embed = discord.Embed(
            title="🚫 Scam Domain Detected",
            description=f"{message.author.mention} was timed out for posting a scam domain",
            color=0xff0000
        )
        embed.add_field(
            name="Domain",
            value=domain,
            inline=True
        )
        embed.add_field(
            name="Action",
            value="Message deleted + 10m timeout",
            inline=True
        )
        
        try:
            await message.channel.send(embed=embed, delete_after=10)
        except:
            pass

class LockdownConfirmView(discord.ui.View):
    def __init__(self, ctx, reason):
        super().__init__(timeout=60)
        self.ctx = ctx
        self.reason = reason

    @discord.ui.button(label="✅ Confirm", style=discord.ButtonStyle.danger)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.ctx.author:
            await interaction.response.send_message("❌ Only the command author can confirm!", ephemeral=True)
            return
        
        await interaction.response.defer()
        
        # Start lockdown
        embed = discord.Embed(
            title="🚨 Locking Down Server...",
            description="Locking all channels...",
            color=0xff0000
        )
        await interaction.followup.send(embed=embed)
        
        locked_count = 0
        failed_count = 0
        
        for channel in self.ctx.guild.text_channels:
            try:
                await channel.set_permissions(
                    self.ctx.guild.default_role,
                    send_messages=False,
                    reason=self.reason
                )
                locked_count += 1
            except:
                failed_count += 1
        
        # Update embed
        embed.title = "✅ Lockdown Complete"
        embed.description = f"**Locked:** {locked_count} channels\n**Failed:** {failed_count}"
        embed.color = 0x00ff00
        
        await interaction.edit_original_response(embed=embed)
        
        # Log the action
        logging_cog = self.ctx.bot.get_cog('DetailedModLogs')
        if logging_cog:
            await logging_cog.log_mod_action(
                self.ctx.guild,
                "lockdown",
                self.ctx.author,
                None,
                self.reason,
                f"{locked_count} channels"
            )

    @discord.ui.button(label="❌ Cancel", style=discord.ButtonStyle.secondary)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.ctx.author:
            await interaction.response.send_message("❌ Only the command author can cancel!", ephemeral=True)
            return
        
        await interaction.response.send_message("❌ Lockdown cancelled.", ephemeral=True)

class UnlockdownConfirmView(discord.ui.View):
    def __init__(self, ctx):
        super().__init__(timeout=60)
        self.ctx = ctx

    @discord.ui.button(label="✅ Confirm", style=discord.ButtonStyle.success)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.ctx.author:
            await interaction.response.send_message("❌ Only the command author can confirm!", ephemeral=True)
            return
        
        await interaction.response.defer()
        
        # Start unlockdown
        embed = discord.Embed(
            title="🔓 Unlocking Server...",
            description="Unlocking all channels...",
            color=0x00ff00
        )
        await interaction.followup.send(embed=embed)
        
        unlocked_count = 0
        failed_count = 0
        
        for channel in self.ctx.guild.text_channels:
            try:
                await channel.set_permissions(
                    self.ctx.guild.default_role,
                    send_messages=True,
                    reason="Server unlockdown"
                )
                unlocked_count += 1
            except:
                failed_count += 1
        
        # Update embed
        embed.title = "✅ Unlockdown Complete"
        embed.description = f"**Unlocked:** {unlocked_count} channels\n**Failed:** {failed_count}"
        embed.color = 0x00ff00
        
        await interaction.edit_original_response(embed=embed)
        
        # Log the action
        logging_cog = self.ctx.bot.get_cog('DetailedModLogs')
        if logging_cog:
            await logging_cog.log_mod_action(
                self.ctx.guild,
                "unlockdown",
                self.ctx.author,
                None,
                "Server unlockdown",
                f"{unlocked_count} channels"
            )

    @discord.ui.button(label="❌ Cancel", style=discord.ButtonStyle.secondary)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.ctx.author:
            await interaction.response.send_message("❌ Only the command author can cancel!", ephemeral=True)
            return
        
        await interaction.response.send_message("❌ Unlockdown cancelled.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(ServerSecurity(bot))
