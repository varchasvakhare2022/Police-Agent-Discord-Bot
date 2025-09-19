import discord
from discord.ext import commands
import json
import os
import time
import uuid
from datetime import datetime, timedelta
import inspect

class DetailedModLogs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.cases_file = "data/mod_cases.json"
        self.message_logs_file = "data/message_logs.json"
        self.load_data()

    def load_data(self):
        """Load mod cases and message logs"""
        try:
            if os.path.exists(self.cases_file):
                with open(self.cases_file, 'r') as f:
                    self.mod_cases = json.load(f)
            else:
                self.mod_cases = {}
                self.save_cases()
        except Exception as e:
            print(f"Error loading mod cases: {e}")
            self.mod_cases = {}

        try:
            if os.path.exists(self.message_logs_file):
                with open(self.message_logs_file, 'r') as f:
                    self.message_logs = json.load(f)
            else:
                self.message_logs = {}
                self.save_message_logs()
        except Exception as e:
            print(f"Error loading message logs: {e}")
            self.message_logs = {}

    def save_cases(self):
        """Save mod cases to JSON file"""
        try:
            os.makedirs("data", exist_ok=True)
            with open(self.cases_file, 'w') as f:
                json.dump(self.mod_cases, f, indent=2)
        except Exception as e:
            print(f"Error saving mod cases: {e}")

    def save_message_logs(self):
        """Save message logs to JSON file"""
        try:
            os.makedirs("data", exist_ok=True)
            with open(self.message_logs_file, 'w') as f:
                json.dump(self.message_logs, f, indent=2)
        except Exception as e:
            print(f"Error saving message logs: {e}")

    def generate_case_id(self, guild_id: int) -> str:
        """Generate a unique case ID"""
        guild_key = str(guild_id)
        if guild_key not in self.mod_cases:
            self.mod_cases[guild_key] = {}
        
        case_number = len(self.mod_cases[guild_key]) + 1
        return f"{guild_id}-{case_number:04d}"

    async def log_mod_action(self, guild: discord.Guild, action_type: str, moderator: discord.Member, 
                           target: discord.Member = None, reason: str = "No reason provided", 
                           duration: str = None, case_id: str = None) -> str:
        """Log a moderation action with detailed information"""
        
        if not case_id:
            case_id = self.generate_case_id(guild.id)
        
        # Get or create log channel
        log_channel = await self.get_or_create_log_channel(guild)
        if not log_channel:
            return case_id
        
        # Store case data
        guild_key = str(guild.id)
        if guild_key not in self.mod_cases:
            self.mod_cases[guild_key] = {}
        
        self.mod_cases[guild_key][case_id] = {
            "action_type": action_type,
            "moderator_id": moderator.id,
            "moderator_name": moderator.display_name,
            "target_id": target.id if target else None,
            "target_name": target.display_name if target else None,
            "reason": reason,
            "duration": duration,
            "timestamp": time.time(),
            "guild_id": guild.id,
            "guild_name": guild.name
        }
        self.save_cases()
        
        # Create detailed embed
        embed = discord.Embed(
            title=f"🛡️ Moderation Action: {action_type.title()}",
            color=self.get_action_color(action_type),
            timestamp=datetime.now()
        )
        
        embed.add_field(
            name="📋 Case ID",
            value=f"`{case_id}`",
            inline=True
        )
        
        embed.add_field(
            name="👮 Moderator",
            value=f"{moderator.mention} (`{moderator.id}`)",
            inline=True
        )
        
        if target:
            embed.add_field(
                name="🎯 Target",
                value=f"{target.mention} (`{target.id}`)",
                inline=True
            )
        
        embed.add_field(
            name="📝 Reason",
            value=reason,
            inline=False
        )
        
        if duration:
            embed.add_field(
                name="⏰ Duration",
                value=duration,
                inline=True
            )
        
        embed.add_field(
            name="🏢 Server",
            value=guild.name,
            inline=True
        )
        
        embed.set_footer(text=f"Case ID: {case_id}")
        
        try:
            await log_channel.send(embed=embed)
        except Exception as e:
            print(f"Error sending mod log: {e}")
        
        return case_id

    async def log_message_action(self, guild: discord.Guild, action_type: str, moderator: discord.Member,
                               message: discord.Message, reason: str = "No reason provided") -> str:
        """Log message deletion/editing with content"""
        
        case_id = self.generate_case_id(guild.id)
        
        # Store message data
        guild_key = str(guild.id)
        if guild_key not in self.message_logs:
            self.message_logs[guild_key] = {}
        
        self.message_logs[guild_key][case_id] = {
            "action_type": action_type,
            "moderator_id": moderator.id,
            "moderator_name": moderator.display_name,
            "message_id": message.id,
            "author_id": message.author.id,
            "author_name": message.author.display_name,
            "channel_id": message.channel.id,
            "channel_name": message.channel.name,
            "content": message.content,
            "attachments": [att.url for att in message.attachments],
            "embeds": [embed.to_dict() for embed in message.embeds],
            "reason": reason,
            "timestamp": time.time(),
            "guild_id": guild.id,
            "guild_name": guild.name
        }
        self.save_message_logs()
        
        # Get or create log channel
        log_channel = await self.get_or_create_log_channel(guild)
        if not log_channel:
            return case_id
        
        # Create detailed embed
        embed = discord.Embed(
            title=f"📝 Message {action_type.title()}",
            color=self.get_action_color(action_type),
            timestamp=datetime.now()
        )
        
        embed.add_field(
            name="📋 Case ID",
            value=f"`{case_id}`",
            inline=True
        )
        
        embed.add_field(
            name="👮 Moderator",
            value=f"{moderator.mention} (`{moderator.id}`)",
            inline=True
        )
        
        embed.add_field(
            name="👤 Author",
            value=f"{message.author.mention} (`{message.author.id}`)",
            inline=True
        )
        
        embed.add_field(
            name="📍 Channel",
            value=f"{message.channel.mention}",
            inline=True
        )
        
        embed.add_field(
            name="📝 Content",
            value=f"```{message.content[:1000]}{'...' if len(message.content) > 1000 else ''}```",
            inline=False
        )
        
        if message.attachments:
            embed.add_field(
                name="📎 Attachments",
                value="\n".join([f"[{att.filename}]({att.url})" for att in message.attachments[:5]]),
                inline=False
            )
        
        embed.add_field(
            name="📝 Reason",
            value=reason,
            inline=False
        )
        
        embed.set_footer(text=f"Case ID: {case_id}")
        
        try:
            await log_channel.send(embed=embed)
        except Exception as e:
            print(f"Error sending message log: {e}")
        
        return case_id

    def get_action_color(self, action_type: str) -> int:
        """Get color for action type"""
        colors = {
            "kick": 0xff8b8b,
            "ban": 0xff0000,
            "timeout": 0xffa500,
            "untimeout": 0x00ff00,
            "unban": 0x00ff00,
            "delete": 0xff0000,
            "edit": 0xffa500,
            "warn": 0xffa500,
            "mute": 0xff8b8b,
            "unmute": 0x00ff00
        }
        return colors.get(action_type.lower(), 0x808080)

    async def get_or_create_log_channel(self, guild: discord.Guild) -> discord.TextChannel:
        """Get or create mod log channel"""
        # Check if we have a stored log channel
        guild_key = str(guild.id)
        if guild_key in self.mod_cases:
            # Try to find existing log channel
            for channel in guild.text_channels:
                if "mod-log" in channel.name.lower() or "moderation" in channel.name.lower():
                    return channel
        
        # Create new log channel
        try:
            if not guild.me.guild_permissions.manage_channels:
                return None
            
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(read_messages=False),
                guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
            }
            
            channel = await guild.create_text_channel(
                name="mod-logs",
                overwrites=overwrites,
                topic="Police Agent - Detailed Moderation Logs",
                reason="Auto-created mod log channel"
            )
            
            # Send welcome message
            embed = discord.Embed(
                title="🛡️ Moderation Logs Channel",
                description="This channel will log all moderation actions with detailed information and case IDs.",
                color=0x9C84EF
            )
            embed.add_field(
                name="📋 Features",
                value="• Case IDs for easy reference\n• Detailed action logs\n• Message deletion/editing logs\n• Timestamps and reasons",
                inline=False
            )
            embed.set_footer(text="Police Agent Bot")
            
            await channel.send(embed=embed)
            return channel
            
        except Exception as e:
            print(f"Error creating mod log channel: {e}")
            return None

    @commands.command(name="mod_case")
    @commands.has_permissions(administrator=True)
    async def view_case(self, ctx: commands.Context, case_id: str):
        """View detailed information about a specific case"""
        
        guild_key = str(ctx.guild.id)
        if guild_key not in self.mod_cases:
            await ctx.reply("❌ No mod cases found for this server!")
            return
        
        if case_id not in self.mod_cases[guild_key]:
            await ctx.reply(f"❌ Case `{case_id}` not found!")
            return
        
        case = self.mod_cases[guild_key][case_id]
        
        embed = discord.Embed(
            title=f"📋 Case Details: {case_id}",
            color=self.get_action_color(case["action_type"]),
            timestamp=datetime.fromtimestamp(case["timestamp"])
        )
        
        embed.add_field(
            name="🛡️ Action",
            value=case["action_type"].title(),
            inline=True
        )
        
        embed.add_field(
            name="👮 Moderator",
            value=f"{case['moderator_name']} (`{case['moderator_id']}`)",
            inline=True
        )
        
        if case["target_name"]:
            embed.add_field(
                name="🎯 Target",
                value=f"{case['target_name']} (`{case['target_id']}`)",
                inline=True
            )
        
        embed.add_field(
            name="📝 Reason",
            value=case["reason"],
            inline=False
        )
        
        if case["duration"]:
            embed.add_field(
                name="⏰ Duration",
                value=case["duration"],
                inline=True
            )
        
        embed.add_field(
            name="🕐 Date",
            value=f"<t:{int(case['timestamp'])}:F>",
            inline=True
        )
        
        await ctx.send(embed=embed)

    @commands.command(name="mod_cases")
    @commands.has_permissions(administrator=True)
    async def list_cases(self, ctx: commands.Context, user: discord.Member = None, limit: int = 10):
        """List recent mod cases"""
        
        guild_key = str(ctx.guild.id)
        if guild_key not in self.mod_cases:
            await ctx.reply("❌ No mod cases found for this server!")
            return
        
        cases = self.mod_cases[guild_key]
        
        if user:
            # Filter cases for specific user
            user_cases = {
                case_id: case for case_id, case in cases.items()
                if case["target_id"] == user.id
            }
            cases = user_cases
        
        if not cases:
            await ctx.reply("❌ No cases found!")
            return
        
        # Sort by timestamp (newest first)
        sorted_cases = sorted(cases.items(), key=lambda x: x[1]["timestamp"], reverse=True)
        
        embed = discord.Embed(
            title=f"📋 Recent Mod Cases{' - ' + user.display_name if user else ''}",
            color=0x9C84EF
        )
        
        for case_id, case in sorted_cases[:limit]:
            embed.add_field(
                name=f"Case {case_id}",
                value=f"**Action:** {case['action_type'].title()}\n**Moderator:** {case['moderator_name']}\n**Reason:** {case['reason'][:50]}{'...' if len(case['reason']) > 50 else ''}",
                inline=True
            )
        
        embed.set_footer(text=f"Showing {len(sorted_cases[:limit])} of {len(sorted_cases)} cases")
        await ctx.send(embed=embed)

    @commands.command(name="message-log")
    @commands.has_permissions(administrator=True)
    async def view_message_log(self, ctx: commands.Context, case_id: str):
        """View detailed message log"""
        
        guild_key = str(ctx.guild.id)
        if guild_key not in self.message_logs:
            await ctx.reply("❌ No message logs found for this server!")
            return
        
        if case_id not in self.message_logs[guild_key]:
            await ctx.reply(f"❌ Message log `{case_id}` not found!")
            return
        
        log = self.message_logs[guild_key][case_id]
        
        embed = discord.Embed(
            title=f"📝 Message Log: {case_id}",
            color=self.get_action_color(log["action_type"]),
            timestamp=datetime.fromtimestamp(log["timestamp"])
        )
        
        embed.add_field(
            name="📋 Action",
            value=log["action_type"].title(),
            inline=True
        )
        
        embed.add_field(
            name="👮 Moderator",
            value=f"{log['moderator_name']} (`{log['moderator_id']}`)",
            inline=True
        )
        
        embed.add_field(
            name="👤 Author",
            value=f"{log['author_name']} (`{log['author_id']}`)",
            inline=True
        )
        
        embed.add_field(
            name="📍 Channel",
            value=f"#{log['channel_name']}",
            inline=True
        )
        
        embed.add_field(
            name="📝 Content",
            value=f"```{log['content'][:1000]}{'...' if len(log['content']) > 1000 else ''}```",
            inline=False
        )
        
        if log["attachments"]:
            embed.add_field(
                name="📎 Attachments",
                value="\n".join([f"[{att}]({att})" for att in log["attachments"][:5]]),
                inline=False
            )
        
        embed.add_field(
            name="📝 Reason",
            value=log["reason"],
            inline=False
        )
        
        await ctx.send(embed=embed)

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        """Log deleted messages"""
        if message.author.bot or not message.guild:
            return
        
        # Check if message was deleted by a moderator
        # This is a simplified check - in practice, you'd need to track who deleted it
        await self.log_message_action(
            message.guild,
            "delete",
            message.guild.me,  # Placeholder - in practice, track the actual moderator
            message,
            "Message deleted"
        )

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        """Log edited messages"""
        if before.author.bot or not before.guild:
            return
        
        if before.content != after.content:
            await self.log_message_action(
                before.guild,
                "edit",
                before.guild.me,  # Placeholder - in practice, track the actual moderator
                before,
                "Message edited"
            )

async def setup(bot):
    await bot.add_cog(DetailedModLogs(bot))
