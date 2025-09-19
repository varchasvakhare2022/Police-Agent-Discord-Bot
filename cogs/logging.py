import discord
from discord.ext import commands
import json
import os
from datetime import datetime

class LoggingSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.log_channels_file = "data/log_channels.json"
        self.load_log_channels()
    
    def load_log_channels(self):
        """Load log channel IDs from JSON file"""
        try:
            if os.path.exists(self.log_channels_file):
                with open(self.log_channels_file, 'r') as f:
                    self.log_channels = json.load(f)
            else:
                self.log_channels = {}
                self.save_log_channels()
        except Exception as e:
            print(f"Error loading log channels: {e}")
            self.log_channels = {}
    
    def save_log_channels(self):
        """Save log channel IDs to JSON file"""
        try:
            os.makedirs("data", exist_ok=True)
            with open(self.log_channels_file, 'w') as f:
                json.dump(self.log_channels, f, indent=2)
        except Exception as e:
            print(f"Error saving log channels: {e}")
    
    async def get_or_create_log_channel(self, guild: discord.Guild) -> discord.TextChannel:
        """Get existing log channel or create a new one"""
        guild_id = str(guild.id)
        
        # Check if we have a stored log channel ID
        if guild_id in self.log_channels:
            channel_id = self.log_channels[guild_id]
            channel = guild.get_channel(channel_id)
            
            # If channel exists, return it
            if channel:
                return channel
            
            # If channel doesn't exist (deleted), remove from storage
            del self.log_channels[guild_id]
            self.save_log_channels()
        
        # Create new log channel
        try:
            # Check if bot has permission to create channels
            if not guild.me.guild_permissions.manage_channels:
                return None
            
            # Create the log channel
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(read_messages=False),
                guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
            }
            
            channel = await guild.create_text_channel(
                name="police-agent-logs",
                overwrites=overwrites,
                topic="Police Agent Bot - Moderation Logs",
                reason="Auto-created log channel for Police Agent bot"
            )
            
            # Store the channel ID
            self.log_channels[guild_id] = channel.id
            self.save_log_channels()
            
            # Send welcome message
            embed = discord.Embed(
                title="🛡️ Police Agent Logging System",
                description="This channel will log all moderation actions performed by Police Agent bot.",
                color=0x00ff00,
                timestamp=datetime.now()
            )
            embed.add_field(
                name="Logged Actions",
                value="• Kicks\n• Bans\n• Timeouts\n• Anti-spam actions\n• Scam detection\n• Prefix changes\n• Blacklist management",
                inline=False
            )
            embed.set_footer(text="Police Agent Bot")
            
            await channel.send(embed=embed)
            
            return channel
            
        except Exception as e:
            print(f"Error creating log channel: {e}")
            return None
    
    async def log_action(self, action_type: str, moderator: discord.Member, target: discord.Member = None, 
                        reason: str = "No reason provided", duration: str = None, guild: discord.Guild = None):
        """Log a moderation action"""
        if not guild:
            guild = moderator.guild
        
        log_channel = await self.get_or_create_log_channel(guild)
        if not log_channel:
            return
        
        # Define colors for different action types
        colors = {
            "kick": 0xff8b8b,
            "ban": 0xff0000,
            "timeout": 0xffa500,
            "unban": 0x00ff00,
            "antispam": 0xff6b6b,
            "scam": 0x8b0000,
            "prefix": 0x9c84ef,
            "blacklist": 0x9932cc,
            "unblacklist": 0x00ff00,
            "verify": 0x00ff00,
            "ticket": 0x4169e1,
            "selfrole": 0x32cd32
        }
        
        color = colors.get(action_type.lower(), 0x808080)
        
        # Create embed
        embed = discord.Embed(
            title=f"🛡️ {action_type.title()} Action",
            color=color,
            timestamp=datetime.now()
        )
        
        # Add moderator info
        embed.add_field(
            name="Moderator",
            value=f"{moderator.mention} (`{moderator.id}`)",
            inline=True
        )
        
        # Add target info if applicable
        if target:
            embed.add_field(
                name="Target",
                value=f"{target.mention} (`{target.id}`)",
                inline=True
            )
        
        # Add reason
        embed.add_field(
            name="Reason",
            value=reason,
            inline=False
        )
        
        # Add duration if applicable
        if duration:
            embed.add_field(
                name="Duration",
                value=duration,
                inline=True
            )
        
        # Add guild info
        embed.add_field(
            name="Server",
            value=guild.name,
            inline=True
        )
        
        embed.set_footer(text="Police Agent Bot")
        
        try:
            await log_channel.send(embed=embed)
        except Exception as e:
            print(f"Error sending log message: {e}")
    
    async def log_system_event(self, event_type: str, description: str, guild: discord.Guild, 
                              user: discord.Member = None, details: str = None):
        """Log system events (prefix changes, blacklist, etc.)"""
        log_channel = await self.get_or_create_log_channel(guild)
        if not log_channel:
            return
        
        embed = discord.Embed(
            title=f"⚙️ {event_type.title()} Event",
            description=description,
            color=0x4169e1,
            timestamp=datetime.now()
        )
        
        if user:
            embed.add_field(
                name="User",
                value=f"{user.mention} (`{user.id}`)",
                inline=True
            )
        
        if details:
            embed.add_field(
                name="Details",
                value=details,
                inline=False
            )
        
        embed.add_field(
            name="Server",
            value=guild.name,
            inline=True
        )
        
        embed.set_footer(text="Police Agent Bot")
        
        try:
            await log_channel.send(embed=embed)
        except Exception as e:
            print(f"Error sending system log: {e}")

async def setup(bot):
    await bot.add_cog(LoggingSystem(bot))
