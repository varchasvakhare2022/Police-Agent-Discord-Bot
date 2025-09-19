import discord
from discord.ext import commands
import time
import re
from collections import defaultdict, deque
import json
import os
from datetime import datetime, timedelta

class AdvancedAutoMod(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config_file = "data/advanced_automod.json"
        self.load_config()
        
        # Anti-raid tracking
        self.new_members = defaultdict(list)  # guild_id -> [(user_id, timestamp)]
        self.member_messages = defaultdict(list)  # guild_id -> [(user_id, timestamp)]
        
        # Spam detection
        self.user_messages = defaultdict(lambda: deque(maxlen=10))  # user_id -> [messages]
        self.duplicate_messages = defaultdict(int)  # message_content -> count
        
        # Ghost ping detection
        self.ghost_pings = defaultdict(list)  # channel_id -> [(author_id, timestamp)]

    def load_config(self):
        """Load auto-moderation configuration"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    self.config = json.load(f)
            else:
                self.config = {
                    "mention_limit": 5,
                    "mention_action": "timeout",
                    "mention_duration": "10m",
                    "duplicate_threshold": 3,
                    "duplicate_action": "delete",
                    "anti_raid_enabled": True,
                    "anti_raid_threshold": 5,
                    "anti_raid_timeframe": 60,
                    "anti_raid_action": "kick",
                    "ghost_ping_enabled": True,
                    "ghost_ping_action": "warn"
                }
                self.save_config()
        except Exception as e:
            print(f"Error loading auto-moderation config: {e}")
            self.config = {}

    def save_config(self):
        """Save auto-moderation configuration"""
        try:
            os.makedirs("data", exist_ok=True)
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"Error saving auto-moderation config: {e}")

    @commands.Cog.listener()
    async def on_member_join(self, member):
        """Track new members for anti-raid detection"""
        if not self.config.get("anti_raid_enabled", True):
            return
        
        guild_id = member.guild.id
        current_time = time.time()
        
        # Add new member to tracking
        self.new_members[guild_id].append((member.id, current_time))
        
        # Clean old entries (older than 5 minutes)
        self.new_members[guild_id] = [
            (user_id, timestamp) for user_id, timestamp in self.new_members[guild_id]
            if current_time - timestamp < 300
        ]
        
        # Check for raid
        await self.check_raid(member.guild)

    @commands.Cog.listener()
    async def on_message(self, message):
        """Monitor messages for various spam patterns"""
        if message.author.bot or not message.guild:
            return
        
        # Check for excessive mentions
        await self.check_excessive_mentions(message)
        
        # Check for duplicate spam
        await self.check_duplicate_spam(message)
        
        # Track member messages for anti-raid
        await self.track_member_messages(message)
        
        # Check for ghost pings
        await self.check_ghost_pings(message)

    async def check_excessive_mentions(self, message):
        """Check for excessive mentions in a message"""
        mention_count = len(message.mentions) + len(message.role_mentions)
        mention_limit = self.config.get("mention_limit", 5)
        
        if mention_count > mention_limit:
            await self.handle_excessive_mentions(message, mention_count)

    async def handle_excessive_mentions(self, message, mention_count):
        """Handle excessive mentions"""
        action = self.config.get("mention_action", "timeout")
        duration = self.config.get("mention_duration", "10m")
        
        # Log the action
        logging_cog = self.bot.get_cog('LoggingSystem')
        if logging_cog:
            await logging_cog.log_action(
                "antispam",
                message.author,
                message.author,
                f"Excessive mentions ({mention_count})",
                guild=message.guild
            )
        
        # Delete the message
        try:
            await message.delete()
        except:
            pass
        
        # Take action
        if action == "timeout":
            try:
                time_convert = {"s": 1, "m": 60, "h": 3600, "d": 86400}
                duration_seconds = int(duration[:-1]) * time_convert.get(duration[-1], 60)
                until = timedelta(seconds=duration_seconds)
                await message.author.timeout(until, reason="Excessive mentions")
                
                embed = discord.Embed(
                    title="🚫 Excessive Mentions Detected",
                    description=f"{message.author.mention} was timed out for {duration} due to excessive mentions ({mention_count})",
                    color=0xff0000
                )
                await message.channel.send(embed=embed, delete_after=10)
                
            except:
                pass
        
        elif action == "kick":
            try:
                await message.author.kick(reason="Excessive mentions")
                
                embed = discord.Embed(
                    title="👢 User Kicked",
                    description=f"{message.author.mention} was kicked for excessive mentions ({mention_count})",
                    color=0xff0000
                )
                await message.channel.send(embed=embed, delete_after=10)
                
            except:
                pass

    async def check_duplicate_spam(self, message):
        """Check for duplicate/copy-paste spam"""
        content = message.content.lower().strip()
        if len(content) < 10:  # Ignore short messages
            return
        
        # Track duplicate messages
        self.duplicate_messages[content] += 1
        threshold = self.config.get("duplicate_threshold", 3)
        
        if self.duplicate_messages[content] >= threshold:
            await self.handle_duplicate_spam(message, content)

    async def handle_duplicate_spam(self, message, content):
        """Handle duplicate spam"""
        action = self.config.get("duplicate_action", "delete")
        
        # Log the action
        logging_cog = self.bot.get_cog('LoggingSystem')
        if logging_cog:
            await logging_cog.log_action(
                "antispam",
                message.author,
                message.author,
                f"Duplicate spam detected",
                guild=message.guild
            )
        
        if action == "delete":
            try:
                await message.delete()
                
                embed = discord.Embed(
                    title="🚫 Duplicate Spam Detected",
                    description=f"{message.author.mention}, please don't spam duplicate messages!",
                    color=0xff0000
                )
                await message.channel.send(embed=embed, delete_after=5)
                
            except:
                pass
        
        elif action == "timeout":
            try:
                await message.delete()
                until = timedelta(minutes=10)
                await message.author.timeout(until, reason="Duplicate spam")
                
                embed = discord.Embed(
                    title="🚫 Duplicate Spam Detected",
                    description=f"{message.author.mention} was timed out for duplicate spam",
                    color=0xff0000
                )
                await message.channel.send(embed=embed, delete_after=10)
                
            except:
                pass

    async def track_member_messages(self, message):
        """Track messages from new members for anti-raid"""
        if not self.config.get("anti_raid_enabled", True):
            return
        
        guild_id = message.guild.id
        current_time = time.time()
        
        # Check if user is a new member (joined within last 5 minutes)
        member_join_time = message.author.joined_at
        if member_join_time and (datetime.now() - member_join_time).total_seconds() < 300:
            self.member_messages[guild_id].append((message.author.id, current_time))
            
            # Clean old entries
            self.member_messages[guild_id] = [
                (user_id, timestamp) for user_id, timestamp in self.member_messages[guild_id]
                if current_time - timestamp < 300
            ]

    async def check_raid(self, guild):
        """Check for potential raid"""
        if not self.config.get("anti_raid_enabled", True):
            return
        
        guild_id = guild.id
        current_time = time.time()
        threshold = self.config.get("anti_raid_threshold", 5)
        timeframe = self.config.get("anti_raid_timeframe", 60)
        
        # Count new members in timeframe
        recent_members = [
            (user_id, timestamp) for user_id, timestamp in self.new_members[guild_id]
            if current_time - timestamp < timeframe
        ]
        
        if len(recent_members) >= threshold:
            await self.handle_raid(guild, recent_members)

    async def handle_raid(self, guild, recent_members):
        """Handle detected raid"""
        action = self.config.get("anti_raid_action", "kick")
        
        # Log the raid
        logging_cog = self.bot.get_cog('LoggingSystem')
        if logging_cog:
            await logging_cog.log_system_event(
                "anti_raid",
                f"Potential raid detected: {len(recent_members)} new members in {self.config.get('anti_raid_timeframe', 60)} seconds",
                guild,
                None,
                f"Action: {action}"
            )
        
        # Take action on new members
        for user_id, timestamp in recent_members:
            try:
                member = guild.get_member(user_id)
                if not member:
                    continue
                
                if action == "kick":
                    await member.kick(reason="Anti-raid protection")
                elif action == "ban":
                    await member.ban(reason="Anti-raid protection")
                
            except:
                pass
        
        # Send alert
        embed = discord.Embed(
            title="🚨 Anti-Raid Protection Activated",
            description=f"Detected {len(recent_members)} new members in {self.config.get('anti_raid_timeframe', 60)} seconds. Action: {action}",
            color=0xff0000
        )
        
        # Send to log channel or first available channel
        log_channel = None
        if logging_cog:
            log_channel = await logging_cog.get_or_create_log_channel(guild)
        
        if log_channel:
            await log_channel.send(embed=embed)
        else:
            # Send to first available channel
            for channel in guild.text_channels:
                try:
                    await channel.send(embed=embed)
                    break
                except:
                    continue

    async def check_ghost_pings(self, message):
        """Check for ghost pings (mentions that get deleted)"""
        if not self.config.get("ghost_ping_enabled", True):
            return
        
        # Check if message contains mentions
        if message.mentions or message.role_mentions:
            channel_id = message.channel.id
            current_time = time.time()
            
            # Store ping info
            self.ghost_pings[channel_id].append((message.author.id, current_time))
            
            # Clean old entries (older than 1 minute)
            self.ghost_pings[channel_id] = [
                (author_id, timestamp) for author_id, timestamp in self.ghost_pings[channel_id]
                if current_time - timestamp < 60
            ]

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        """Detect ghost pings when messages are deleted"""
        if not self.config.get("ghost_ping_enabled", True):
            return
        
        if message.author.bot or not message.guild:
            return
        
        # Check if deleted message had mentions
        if message.mentions or message.role_mentions:
            channel_id = message.channel.id
            current_time = time.time()
            
            # Check if this was a recent ping
            recent_pings = [
                (author_id, timestamp) for author_id, timestamp in self.ghost_pings[channel_id]
                if author_id == message.author.id and current_time - timestamp < 60
            ]
            
            if recent_pings:
                await self.handle_ghost_ping(message)

    async def handle_ghost_ping(self, message):
        """Handle detected ghost ping"""
        action = self.config.get("ghost_ping_action", "warn")
        
        # Log the ghost ping
        logging_cog = self.bot.get_cog('LoggingSystem')
        if logging_cog:
            await logging_cog.log_action(
                "ghost_ping",
                message.author,
                message.author,
                "Ghost ping detected",
                guild=message.guild
            )
        
        if action == "warn":
            embed = discord.Embed(
                title="👻 Ghost Ping Detected",
                description=f"{message.author.mention}, please don't ping people and delete your message!",
                color=0xffa500
            )
            await message.channel.send(embed=embed, delete_after=10)
        
        elif action == "timeout":
            try:
                until = timedelta(minutes=5)
                await message.author.timeout(until, reason="Ghost ping")
                
                embed = discord.Embed(
                    title="👻 Ghost Ping Detected",
                    description=f"{message.author.mention} was timed out for ghost pinging",
                    color=0xff0000
                )
                await message.channel.send(embed=embed, delete_after=10)
                
            except:
                pass

    @commands.command(name="automod")
    @commands.has_permissions(administrator=True)
    async def automod_config(self, ctx: commands.Context, setting: str = None, *, value: str = None):
        """Configure advanced auto-moderation"""
        
        if not setting:
            # Show current configuration
            embed = discord.Embed(
                title="🛡️ Advanced Auto-Moderation Configuration",
                color=0x9C84EF
            )
            
            embed.add_field(
                name="Mention Protection",
                value=f"**Limit:** {self.config.get('mention_limit', 5)} mentions\n**Action:** {self.config.get('mention_action', 'timeout')}\n**Duration:** {self.config.get('mention_duration', '10m')}",
                inline=True
            )
            
            embed.add_field(
                name="Duplicate Spam Protection",
                value=f"**Threshold:** {self.config.get('duplicate_threshold', 3)} duplicates\n**Action:** {self.config.get('duplicate_action', 'delete')}",
                inline=True
            )
            
            embed.add_field(
                name="Anti-Raid Protection",
                value=f"**Enabled:** {self.config.get('anti_raid_enabled', True)}\n**Threshold:** {self.config.get('anti_raid_threshold', 5)} members\n**Timeframe:** {self.config.get('anti_raid_timeframe', 60)} seconds\n**Action:** {self.config.get('anti_raid_action', 'kick')}",
                inline=True
            )
            
            embed.add_field(
                name="Ghost Ping Protection",
                value=f"**Enabled:** {self.config.get('ghost_ping_enabled', True)}\n**Action:** {self.config.get('ghost_ping_action', 'warn')}",
                inline=True
            )
            
            await ctx.send(embed=embed)
            return
        
        # Update configuration
        if setting == "mention_limit":
            try:
                limit = int(value)
                self.config["mention_limit"] = limit
                await ctx.reply(f"✅ Mention limit set to {limit}")
            except ValueError:
                await ctx.reply("❌ Please provide a valid number for mention limit")
        
        elif setting == "mention_action":
            if value in ["timeout", "kick", "ban"]:
                self.config["mention_action"] = value
                await ctx.reply(f"✅ Mention action set to {value}")
            else:
                await ctx.reply("❌ Valid actions: timeout, kick, ban")
        
        elif setting == "mention_duration":
            if re.match(r'^\d+[smhd]$', value):
                self.config["mention_duration"] = value
                await ctx.reply(f"✅ Mention duration set to {value}")
            else:
                await ctx.reply("❌ Valid format: 5s, 5m, 5h, 5d")
        
        elif setting == "duplicate_threshold":
            try:
                threshold = int(value)
                self.config["duplicate_threshold"] = threshold
                await ctx.reply(f"✅ Duplicate threshold set to {threshold}")
            except ValueError:
                await ctx.reply("❌ Please provide a valid number for duplicate threshold")
        
        elif setting == "duplicate_action":
            if value in ["delete", "timeout"]:
                self.config["duplicate_action"] = value
                await ctx.reply(f"✅ Duplicate action set to {value}")
            else:
                await ctx.reply("❌ Valid actions: delete, timeout")
        
        elif setting == "anti_raid":
            if value in ["enable", "disable"]:
                self.config["anti_raid_enabled"] = value == "enable"
                await ctx.reply(f"✅ Anti-raid protection {'enabled' if value == 'enable' else 'disabled'}")
            else:
                await ctx.reply("❌ Valid values: enable, disable")
        
        elif setting == "anti_raid_threshold":
            try:
                threshold = int(value)
                self.config["anti_raid_threshold"] = threshold
                await ctx.reply(f"✅ Anti-raid threshold set to {threshold}")
            except ValueError:
                await ctx.reply("❌ Please provide a valid number for anti-raid threshold")
        
        elif setting == "anti_raid_timeframe":
            try:
                timeframe = int(value)
                self.config["anti_raid_timeframe"] = timeframe
                await ctx.reply(f"✅ Anti-raid timeframe set to {timeframe} seconds")
            except ValueError:
                await ctx.reply("❌ Please provide a valid number for anti-raid timeframe")
        
        elif setting == "anti_raid_action":
            if value in ["kick", "ban"]:
                self.config["anti_raid_action"] = value
                await ctx.reply(f"✅ Anti-raid action set to {value}")
            else:
                await ctx.reply("❌ Valid actions: kick, ban")
        
        elif setting == "ghost_ping":
            if value in ["enable", "disable"]:
                self.config["ghost_ping_enabled"] = value == "enable"
                await ctx.reply(f"✅ Ghost ping protection {'enabled' if value == 'enable' else 'disabled'}")
            else:
                await ctx.reply("❌ Valid values: enable, disable")
        
        elif setting == "ghost_ping_action":
            if value in ["warn", "timeout"]:
                self.config["ghost_ping_action"] = value
                await ctx.reply(f"✅ Ghost ping action set to {value}")
            else:
                await ctx.reply("❌ Valid actions: warn, timeout")
        
        else:
            await ctx.reply("❌ Unknown setting! Use `-automod` to see available settings")
            return
        
        self.save_config()

async def setup(bot):
    await bot.add_cog(AdvancedAutoMod(bot))
