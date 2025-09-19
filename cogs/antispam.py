import discord
from discord.ext import commands
import re
import asyncio
from datetime import datetime, timedelta
from collections import defaultdict
import json
import os

class AntiSpam(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.user_message_counts = defaultdict(list)
        self.user_warnings = defaultdict(int)
        self.scam_patterns = [
            # Fake Nitro links
            r'discord\.gift\/[a-zA-Z0-9]+',
            r'discord\.com\/gifts\/[a-zA-Z0-9]+',
            r'discordapp\.com\/gifts\/[a-zA-Z0-9]+',
            r'discord\.gg\/[a-zA-Z0-9]+.*nitro',
            r'discord\.com\/nitro\/[a-zA-Z0-9]+',
            
            # Common scam patterns
            r'free.*nitro',
            r'claim.*nitro',
            r'get.*nitro.*free',
            r'steam.*gift.*card',
            r'free.*steam.*wallet',
            r'roblox.*robux.*free',
            r'free.*robux',
            r'claim.*robux',
            
            # Phishing patterns
            r'verify.*account',
            r'account.*suspended',
            r'click.*here.*verify',
            r'login.*discord\.com',
            r'discord.*security',
            
            # Crypto scams
            r'bitcoin.*investment',
            r'crypto.*investment',
            r'free.*bitcoin',
            r'earn.*money.*online',
            
            # Generic scam words
            r'limited.*time',
            r'act.*now',
            r'click.*fast',
            r'expires.*soon',
        ]
        
        # Load configuration
        self.config_file = "data/antispam_config.json"
        self.load_config()
    
    def load_config(self):
        """Load anti-spam configuration from JSON file"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    self.config = json.load(f)
            else:
                # Default configuration
                self.config = {
                    "enabled": True,
                    "spam_threshold": 5,  # Messages per minute
                    "spam_window": 60,     # Seconds
                    "warning_threshold": 3, # Warnings before action
                    "auto_mute": True,
                    "mute_duration": 300,  # 5 minutes
                    "log_channel": None,
                    "scam_detection": True,
                    "scam_action": "delete",  # delete, mute, ban
                    "whitelist_roles": [],
                    "whitelist_channels": []
                }
                self.save_config()
        except Exception as e:
            print(f"Error loading anti-spam config: {e}")
            self.config = {"enabled": False}
    
    def save_config(self):
        """Save anti-spam configuration to JSON file"""
        try:
            os.makedirs("data", exist_ok=True)
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"Error saving anti-spam config: {e}")
    
    def is_whitelisted(self, member: discord.Member, channel: discord.TextChannel) -> bool:
        """Check if user or channel is whitelisted"""
        # Check if user has whitelisted role
        for role_id in self.config.get("whitelist_roles", []):
            if discord.utils.get(member.roles, id=role_id):
                return True
        
        # Check if channel is whitelisted
        if channel.id in self.config.get("whitelist_channels", []):
            return True
        
        return False
    
    def detect_scam(self, content: str) -> bool:
        """Detect scam patterns in message content"""
        if not self.config.get("scam_detection", True):
            return False
        
        content_lower = content.lower()
        
        # Check for scam patterns
        for pattern in self.scam_patterns:
            if re.search(pattern, content_lower, re.IGNORECASE):
                return True
        
        # Check for suspicious URLs
        url_pattern = r'https?://[^\s]+'
        urls = re.findall(url_pattern, content)
        
        for url in urls:
            # Check for suspicious domains
            suspicious_domains = [
                'discord-gift.com',
                'discord-nitro.com',
                'discordapp-gift.com',
                'steam-gift.com',
                'roblox-robux.com'
            ]
            
            for domain in suspicious_domains:
                if domain in url.lower():
                    return True
        
        return False
    
    def is_spam(self, user_id: int, content: str) -> bool:
        """Check if message is spam based on rate limiting"""
        if not self.config.get("enabled", True):
            return False
        
        current_time = datetime.now()
        user_messages = self.user_message_counts[user_id]
        
        # Remove old messages outside the window
        window_start = current_time - timedelta(seconds=self.config.get("spam_window", 60))
        user_messages = [msg_time for msg_time in user_messages if msg_time > window_start]
        self.user_message_counts[user_id] = user_messages
        
        # Add current message
        user_messages.append(current_time)
        
        # Check if exceeds threshold
        threshold = self.config.get("spam_threshold", 5)
        return len(user_messages) > threshold
    
    async def log_action(self, action: str, member: discord.Member, reason: str, channel: discord.TextChannel = None):
        """Log moderation action using the logging system"""
        logging_cog = self.bot.get_cog('LoggingSystem')
        if logging_cog:
            await logging_cog.log_action("antispam", member, member, reason, guild=member.guild)
    
    @commands.Cog.listener()
    async def on_message(self, message):
        """Monitor messages for spam and scams"""
        if message.author.bot or not message.guild:
            return
        
        if not self.config.get("enabled", True):
            return
        
        # Check admin bypass
        admin_bypass = self.bot.get_cog('AdminBypass')
        if admin_bypass and admin_bypass.is_admin_or_owner(message.author):
            return
        
        # Check if user/channel is whitelisted
        if self.is_whitelisted(message.author, message.channel):
            return
        
        # Check for scams
        if self.detect_scam(message.content):
            await self.handle_scam(message)
            return
        
        # Check for spam
        if self.is_spam(message.author.id, message.content):
            await self.handle_spam(message)
    
    async def handle_scam(self, message: discord.Message):
        """Handle scam message detection"""
        action = self.config.get("scam_action", "delete")
        
        # Update behavior score
        behavior_cog = self.bot.get_cog('BehaviorScoring')
        if behavior_cog:
            behavior_cog.modify_score(
                message.author.id, 
                message.guild.id, 
                -300,  # Severe penalty for scam attempts
                "Scam content detected by anti-spam system"
            )
        
        try:
            if action == "delete":
                await message.delete()
                await self.log_action("Message Deleted", message.author, "Scam detected", message.channel)
                
            elif action == "mute":
                await message.delete()
                await self.mute_user(message.author, "Scam detected")
                await self.log_action("User Muted", message.author, "Scam detected", message.channel)
                
            elif action == "ban":
                await message.delete()
                await message.author.ban(reason="Scam detected")
                await self.log_action("User Banned", message.author, "Scam detected", message.channel)
                
        except discord.Forbidden:
            await self.log_action("Action Failed", message.author, "Insufficient permissions", message.channel)
        except Exception as e:
            await self.log_action("Error", message.author, f"Error: {str(e)}", message.channel)
    
    async def handle_spam(self, message: discord.Message):
        """Handle spam message detection"""
        user_id = message.author.id
        self.user_warnings[user_id] += 1
        
        # Update behavior score
        behavior_cog = self.bot.get_cog('BehaviorScoring')
        if behavior_cog:
            score_penalty = -50 - (self.user_warnings[user_id] * 10)  # Increasing penalty
            behavior_cog.modify_score(
                message.author.id, 
                message.guild.id, 
                score_penalty,
                f"Spam detected (Warning #{self.user_warnings[user_id]})"
            )
        
        try:
            # Delete the spam message
            await message.delete()
            
            # Check warning threshold
            warning_threshold = self.config.get("warning_threshold", 3)
            
            if self.user_warnings[user_id] >= warning_threshold:
                if self.config.get("auto_mute", True):
                    await self.mute_user(message.author, "Spam detected")
                    await self.log_action("User Muted", message.author, f"Spam detected (Warning {self.user_warnings[user_id]})", message.channel)
                else:
                    await self.log_action("Spam Warning", message.author, f"Spam detected (Warning {self.user_warnings[user_id]})", message.channel)
            else:
                await self.log_action("Spam Detected", message.author, f"Spam detected (Warning {self.user_warnings[user_id]})", message.channel)
                
        except discord.Forbidden:
            await self.log_action("Action Failed", message.author, "Insufficient permissions", message.channel)
        except Exception as e:
            await self.log_action("Error", message.author, f"Error: {str(e)}", message.channel)
    
    async def mute_user(self, member: discord.Member, reason: str):
        """Mute a user for spam/scam"""
        mute_duration = self.config.get("mute_duration", 300)  # 5 minutes
        
        # Find mute role or create one
        mute_role = discord.utils.get(member.guild.roles, name="Muted")
        if not mute_role:
            mute_role = await member.guild.create_role(
                name="Muted",
                color=discord.Color.red(),
                permissions=discord.Permissions.none()
            )
            
            # Set channel permissions
            for channel in member.guild.channels:
                try:
                    await channel.set_permissions(mute_role, send_messages=False, speak=False)
                except:
                    pass
        
        # Add mute role
        await member.add_roles(mute_role, reason=reason)
        
        # Remove mute role after duration
        await asyncio.sleep(mute_duration)
        try:
            await member.remove_roles(mute_role, reason="Mute duration expired")
        except:
            pass
    
    @commands.group(name="antispam", invoke_without_command=True)
    @commands.has_permissions(administrator=True)
    async def antispam(self, ctx: commands.Context):
        """Anti-spam system configuration"""
        embed = discord.Embed(
            title="🛡️ Anti-Spam System Status",
            color=0x00ff00 if self.config.get("enabled", False) else 0xff0000
        )
        
        embed.add_field(
            name="Status",
            value="✅ Enabled" if self.config.get("enabled", False) else "❌ Disabled",
            inline=True
        )
        
        embed.add_field(
            name="Spam Threshold",
            value=f"{self.config.get('spam_threshold', 5)} messages/minute",
            inline=True
        )
        
        embed.add_field(
            name="Scam Detection",
            value="✅ Enabled" if self.config.get("scam_detection", True) else "❌ Disabled",
            inline=True
        )
        
        embed.add_field(
            name="Auto Mute",
            value="✅ Enabled" if self.config.get("auto_mute", True) else "❌ Disabled",
            inline=True
        )
        
        embed.add_field(
            name="Warning Threshold",
            value=f"{self.config.get('warning_threshold', 3)} warnings",
            inline=True
        )
        
        embed.add_field(
            name="Mute Duration",
            value=f"{self.config.get('mute_duration', 300)} seconds",
            inline=True
        )
        
        await ctx.send(embed=embed)
    
    @antispam.command(name="enable")
    @commands.has_permissions(administrator=True)
    async def enable_antispam(self, ctx: commands.Context):
        """Enable anti-spam system"""
        self.config["enabled"] = True
        self.save_config()
        await ctx.send("✅ Anti-spam system enabled!")
    
    @antispam.command(name="disable")
    @commands.has_permissions(administrator=True)
    async def disable_antispam(self, ctx: commands.Context):
        """Disable anti-spam system"""
        self.config["enabled"] = False
        self.save_config()
        await ctx.send("❌ Anti-spam system disabled!")
    
    @antispam.command(name="threshold")
    @commands.has_permissions(administrator=True)
    async def set_threshold(self, ctx: commands.Context, threshold: int):
        """Set spam threshold (messages per minute)"""
        if threshold < 1 or threshold > 20:
            await ctx.send("❌ Threshold must be between 1 and 20!")
            return
        
        self.config["spam_threshold"] = threshold
        self.save_config()
        await ctx.send(f"✅ Spam threshold set to {threshold} messages per minute!")
    
    @antispam.command(name="logchannel")
    @commands.has_permissions(administrator=True)
    async def set_log_channel(self, ctx: commands.Context, channel: discord.TextChannel):
        """Set log channel for anti-spam actions"""
        self.config["log_channel"] = channel.id
        self.save_config()
        await ctx.send(f"✅ Anti-spam log channel set to {channel.mention}!")
    
    @antispam.command(name="whitelist")
    @commands.has_permissions(administrator=True)
    async def whitelist_role(self, ctx: commands.Context, role: discord.Role):
        """Add role to anti-spam whitelist"""
        if role.id not in self.config.get("whitelist_roles", []):
            self.config.setdefault("whitelist_roles", []).append(role.id)
            self.save_config()
            await ctx.send(f"✅ {role.mention} added to anti-spam whitelist!")
        else:
            await ctx.send(f"❌ {role.mention} is already whitelisted!")
    
    @antispam.command(name="unwhitelist")
    @commands.has_permissions(administrator=True)
    async def unwhitelist_role(self, ctx: commands.Context, role: discord.Role):
        """Remove role from anti-spam whitelist"""
        if role.id in self.config.get("whitelist_roles", []):
            self.config["whitelist_roles"].remove(role.id)
            self.save_config()
            await ctx.send(f"✅ {role.mention} removed from anti-spam whitelist!")
        else:
            await ctx.send(f"❌ {role.mention} is not whitelisted!")
    
    @antispam.command(name="reset")
    @commands.has_permissions(administrator=True)
    async def reset_warnings(self, ctx: commands.Context, member: discord.Member):
        """Reset spam warnings for a user"""
        self.user_warnings[member.id] = 0
        await ctx.send(f"✅ Spam warnings reset for {member.mention}!")

async def setup(bot):
    await bot.add_cog(AntiSpam(bot))
