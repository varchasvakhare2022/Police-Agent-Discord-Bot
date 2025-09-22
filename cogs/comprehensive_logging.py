import discord
from discord.ext import commands
import json
import os
from datetime import datetime
import asyncio

class ComprehensiveLogging(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.log_channel_id = 1419643352986423379
        self.suspicious_activities = {}
        self.user_activity_tracker = {}
        
    def get_log_channel(self, guild):
        """Get the log channel for the guild"""
        return guild.get_channel(self.log_channel_id)
    
    def create_log_embed(self, title, description, color=0xff0000, fields=None, thumbnail=None):
        """Create a standardized log embed"""
        current_time = datetime.now()
        embed = discord.Embed(
            title=f"🚨 {title}",
            description=description,
            color=color,
            timestamp=current_time
        )
        
        if fields:
            for field in fields:
                embed.add_field(
                    name=field.get('name', ''),
                    value=field.get('value', ''),
                    inline=field.get('inline', False)
                )
        
        if thumbnail:
            embed.set_thumbnail(url=thumbnail)
        
        # Footer with exact time
        embed.set_footer(text=f"Police Agent Logging System • {current_time.strftime('%Y-%m-%d %H:%M:%S')} UTC")
        return embed
    
    async def send_log(self, guild, embed):
        """Send log to the designated log channel"""
        log_channel = self.get_log_channel(guild)
        if log_channel:
            try:
                await log_channel.send(embed=embed)
            except discord.Forbidden:
                print(f"Could not send log to channel {self.log_channel_id} - insufficient permissions")
            except Exception as e:
                print(f"Error sending log: {e}")
    
    def track_user_activity(self, user_id, activity_type, details):
        """Track user activity for suspicious behavior detection"""
        if user_id not in self.user_activity_tracker:
            self.user_activity_tracker[user_id] = {
                'activities': [],
                'warning_count': 0,
                'last_activity': None
            }
        
        activity = {
            'type': activity_type,
            'details': details,
            'timestamp': datetime.now().isoformat()
        }
        
        self.user_activity_tracker[user_id]['activities'].append(activity)
        self.user_activity_tracker[user_id]['last_activity'] = datetime.now()
        
        # Keep only last 50 activities per user
        if len(self.user_activity_tracker[user_id]['activities']) > 50:
            self.user_activity_tracker[user_id]['activities'] = self.user_activity_tracker[user_id]['activities'][-50:]
    
    def detect_suspicious_activity(self, user_id, guild_id):
        """Detect suspicious patterns in user behavior"""
        if user_id not in self.user_activity_tracker:
            return None
        
        activities = self.user_activity_tracker[user_id]['activities']
        recent_activities = [a for a in activities if (datetime.now() - datetime.fromisoformat(a['timestamp'])).seconds < 300]  # Last 5 minutes
        
        # Check for rapid rule violations
        rule_violations = [a for a in recent_activities if a['type'] == 'rule_violation']
        if len(rule_violations) >= 3:
            return {
                'type': 'rapid_violations',
                'severity': 'high',
                'description': f'User has violated {len(rule_violations)} rules in the last 5 minutes',
                'details': [v['details'] for v in rule_violations]
            }
        
        # Check for spam patterns
        spam_activities = [a for a in recent_activities if a['type'] == 'spam']
        if len(spam_activities) >= 5:
            return {
                'type': 'spam_pattern',
                'severity': 'medium',
                'description': f'User has spammed {len(spam_activities)} times in the last 5 minutes',
                'details': [s['details'] for s in spam_activities]
            }
        
        return None
    
    # Member Events
    @commands.Cog.listener()
    async def on_member_join(self, member):
        """Log when a member joins"""
        embed = self.create_log_embed(
            "Member Joined",
            f"**User:** {member.mention} ({member.name}#{member.discriminator})\n"
            f"**ID:** {member.id}\n"
            f"**Account Created:** <t:{int(member.created_at.timestamp())}:F>\n"
            f"**Joined:** <t:{int(member.joined_at.timestamp())}:F>",
            color=0x00ff00,
            thumbnail=member.display_avatar.url
        )
        
        await self.send_log(member.guild, embed)
        self.track_user_activity(member.id, 'join', f'Joined server at {datetime.now()}')
    
    @commands.Cog.listener()
    async def on_member_remove(self, member):
        """Log when a member leaves"""
        embed = self.create_log_embed(
            "Member Left",
            f"**User:** {member.name}#{member.discriminator}\n"
            f"**ID:** {member.id}\n"
            f"**Left:** <t:{int(datetime.now().timestamp())}:F>\n"
            f"**Roles:** {', '.join([role.name for role in member.roles[1:]]) if member.roles[1:] else 'None'}",
            color=0xff9900,
            thumbnail=member.display_avatar.url
        )
        
        await self.send_log(member.guild, embed)
        self.track_user_activity(member.id, 'leave', f'Left server at {datetime.now()}')
    
    @commands.Cog.listener()
    async def on_member_ban(self, guild, user):
        """Log when a member is banned"""
        embed = self.create_log_embed(
            "Member Banned",
            f"**User:** {user.name}#{user.discriminator}\n"
            f"**ID:** {user.id}\n"
            f"**Banned:** <t:{int(datetime.now().timestamp())}:F>",
            color=0xff0000,
            thumbnail=user.display_avatar.url
        )
        
        await self.send_log(guild, embed)
        self.track_user_activity(user.id, 'ban', f'Banned from server at {datetime.now()}')
    
    @commands.Cog.listener()
    async def on_member_unban(self, guild, user):
        """Log when a member is unbanned"""
        embed = self.create_log_embed(
            "Member Unbanned",
            f"**User:** {user.name}#{user.discriminator}\n"
            f"**ID:** {user.id}\n"
            f"**Unbanned:** <t:{int(datetime.now().timestamp())}:F>",
            color=0x00ff00,
            thumbnail=user.display_avatar.url
        )
        
        await self.send_log(guild, embed)
        self.track_user_activity(user.id, 'unban', f'Unbanned from server at {datetime.now()}')
    
    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        """Log when a member's roles are updated"""
        if before.roles != after.roles:
            added_roles = [role for role in after.roles if role not in before.roles]
            removed_roles = [role for role in before.roles if role not in after.roles]
            
            if added_roles or removed_roles:
                embed = self.create_log_embed(
                    "Member Roles Updated",
                    f"**User:** {after.mention} ({after.name}#{after.discriminator})\n"
                    f"**ID:** {after.id}",
                    color=0x0099ff,
                    thumbnail=after.display_avatar.url
                )
                
                if added_roles:
                    embed.add_field(
                        name="➕ Roles Added",
                        value=', '.join([role.mention for role in added_roles]),
                        inline=False
                    )
                
                if removed_roles:
                    embed.add_field(
                        name="➖ Roles Removed",
                        value=', '.join([role.mention for role in removed_roles]),
                        inline=False
                    )
                
                await self.send_log(after.guild, embed)
                self.track_user_activity(after.id, 'role_change', f'Roles updated at {datetime.now()}')
    
    # Message Events
    @commands.Cog.listener()
    async def on_message_delete(self, message):
        """Log when a message is deleted"""
        if message.author.bot:
            return
        
        embed = self.create_log_embed(
            "Message Deleted",
            f"**User:** {message.author.mention} ({message.author.name}#{message.author.discriminator})\n"
            f"**Channel:** {message.channel.mention}\n"
            f"**Content:** {message.content[:1000] if message.content else 'No text content'}",
            color=0xff0000,
            thumbnail=message.author.display_avatar.url
        )
        
        if message.attachments:
            embed.add_field(
                name="Attachments",
                value=f"{len(message.attachments)} file(s) deleted",
                inline=False
            )
        
        await self.send_log(message.guild, embed)
        self.track_user_activity(message.author.id, 'message_delete', f'Deleted message in {message.channel.name}')
    
    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        """Log when a message is edited"""
        if after.author.bot or before.content == after.content:
            return
        
        embed = self.create_log_embed(
            "Message Edited",
            f"**User:** {after.author.mention} ({after.author.name}#{after.author.discriminator})\n"
            f"**Channel:** {after.channel.mention}\n"
            f"**Message Link:** [Jump to Message]({after.jump_url})",
            color=0xff9900,
            thumbnail=after.author.display_avatar.url
        )
        
        embed.add_field(
            name="Before",
            value=before.content[:1000] if before.content else 'No content',
            inline=False
        )
        
        embed.add_field(
            name="After",
            value=after.content[:1000] if after.content else 'No content',
            inline=False
        )
        
        await self.send_log(after.guild, embed)
        self.track_user_activity(after.author.id, 'message_edit', f'Edited message in {after.channel.name}')
    
    # Voice Events
    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        """Log voice state changes"""
        if before.channel != after.channel:
            embed = self.create_log_embed(
                "Voice Channel Change",
                f"**User:** {member.mention} ({member.name}#{member.discriminator})\n"
                f"**ID:** {member.id}",
                color=0x0099ff,
                thumbnail=member.display_avatar.url
            )
            
            if before.channel:
                embed.add_field(name="Left", value=before.channel.mention, inline=True)
            if after.channel:
                embed.add_field(name="Joined", value=after.channel.mention, inline=True)
            
            await self.send_log(member.guild, embed)
            self.track_user_activity(member.id, 'voice_change', f'Changed voice channel at {datetime.now()}')
    
    # Command Events - Disabled command error logging
    # @commands.Cog.listener()
    # async def on_command_error(self, ctx, error):
    #     """Log command errors"""
    #     pass  # Command errors are no longer logged
    
    # Integration with Rule Monitor
    async def log_rule_violation(self, user, rule_num, rule_message, guild, original_message=None, channel=None):
        """Log rule violations from the rule monitor"""
        embed = self.create_log_embed(
            "Rule Violation Detected",
            f"**User:** {user.mention} ({user.name}#{user.discriminator})\n"
            f"**User ID:** {user.id}\n"
            f"**Rule Broken:** #{rule_num}",
            color=0xff0000,
            thumbnail=user.display_avatar.url
        )
        
        # Add channel information if provided
        if channel:
            embed.add_field(
                name="📍 Channel",
                value=f"{channel.mention} ({channel.name})\n**Channel ID:** {channel.id}",
                inline=True
            )
        
        # Add the user's original message if provided
        if original_message:
            embed.add_field(
                name="💬 User's Message",
                value=f"```{original_message[:1000]}```",
                inline=False
            )
        
        # Add message link if possible
        if channel and original_message:
            embed.add_field(
                name="🔗 Message Link",
                value=f"[Jump to Message](https://discord.com/channels/{guild.id}/{channel.id})",
                inline=True
            )
        
        await self.send_log(guild, embed)
        self.track_user_activity(user.id, 'rule_violation', f'Violated Rule #{rule_num} in #{channel.name if channel else "unknown"}')
        
        # Check for suspicious activity
        suspicious = self.detect_suspicious_activity(user.id, guild.id)
        if suspicious:
            await self.log_suspicious_activity(user, suspicious, guild)
    
    async def log_suspicious_activity(self, user, activity, guild):
        """Log suspicious user activity"""
        embed = self.create_log_embed(
            "🚨 Suspicious Activity Alert",
            f"**User:** {user.mention} ({user.name}#{user.discriminator})\n"
            f"**Type:** {activity['type'].replace('_', ' ').title()}\n"
            f"**Severity:** {activity['severity'].upper()}\n"
            f"**Description:** {activity['description']}",
            color=0xff0000,
            thumbnail=user.display_avatar.url
        )
        
        if activity.get('details'):
            embed.add_field(
                name="Recent Activities",
                value='\n'.join([f"• {detail}" for detail in activity['details'][-5:]]),
                inline=False
            )
        
        await self.send_log(guild, embed)
    
    # Warning System Integration
    async def log_warning_issued(self, user, moderator, reason, warning_id, guild):
        """Log when a warning is issued"""
        embed = self.create_log_embed(
            "Warning Issued",
            f"**User:** {user.mention} ({user.name}#{user.discriminator})\n"
            f"**User ID:** {user.id}\n"
            f"**Moderator:** {moderator.mention} ({moderator.name}#{moderator.discriminator})\n"
            f"**Moderator ID:** {moderator.id}\n"
            f"**Warning ID:** #{warning_id}\n"
            f"**Reason:** {reason}",
            color=0xff9900,
            thumbnail=user.display_avatar.url
        )
        
        await self.send_log(guild, embed)
        self.track_user_activity(user.id, 'warning', f'Received warning #{warning_id} from {moderator.name}')
    
    async def log_warnings_cleared(self, user, moderator, warning_count, guild):
        """Log when warnings are cleared for a user"""
        embed = self.create_log_embed(
            "Warnings Cleared",
            f"**User:** {user.mention} ({user.name}#{user.discriminator})\n"
            f"**User ID:** {user.id}\n"
            f"**Moderator:** {moderator.mention} ({moderator.name}#{moderator.discriminator})\n"
            f"**Moderator ID:** {moderator.id}\n"
            f"**Warnings Cleared:** {warning_count}",
            color=0x00ff00,
            thumbnail=user.display_avatar.url
        )
        
        await self.send_log(guild, embed)
        self.track_user_activity(user.id, 'warnings_cleared', f'All {warning_count} warnings cleared by {moderator.name}')
    
    async def log_specific_warning_cleared(self, user, moderator, warning_data, guild):
        """Log when a specific warning is cleared"""
        embed = self.create_log_embed(
            "Specific Warning Cleared",
            f"**User:** {user.mention} ({user.name}#{user.discriminator})\n"
            f"**User ID:** {user.id}\n"
            f"**Moderator:** {moderator.mention} ({moderator.name}#{moderator.discriminator})\n"
            f"**Moderator ID:** {moderator.id}\n"
            f"**Warning ID:** #{warning_data['id']}",
            color=0x00ff00,
            thumbnail=user.display_avatar.url
        )
        
        embed.add_field(
            name="Cleared Warning Details",
            value=f"**Reason:** {warning_data['reason']}\n**Original Moderator:** <@{warning_data['moderator_id']}>\n**Original Date:** <t:{int(datetime.fromisoformat(warning_data['timestamp']).timestamp())}:F>",
            inline=False
        )
        
        await self.send_log(guild, embed)
        self.track_user_activity(user.id, 'specific_warning_cleared', f'Warning #{warning_data["id"]} cleared by {moderator.name}')
    
    # Admin Commands
    @commands.command(name='useractivity')
    @commands.has_permissions(manage_messages=True)
    async def check_user_activity(self, ctx, user: discord.Member):
        """Check a user's recent activity"""
        if user.id not in self.user_activity_tracker:
            embed = discord.Embed(
                title="User Activity Report",
                description=f"No activity recorded for {user.mention}",
                color=0x0099ff
            )
        else:
            activities = self.user_activity_tracker[user.id]['activities'][-10:]  # Last 10 activities
            
            embed = discord.Embed(
                title=f"User Activity Report - {user.name}",
                description=f"**Total Activities:** {len(self.user_activity_tracker[user.id]['activities'])}\n"
                           f"**Last Activity:** <t:{int(self.user_activity_tracker[user.id]['last_activity'].timestamp())}:F>",
                color=0x0099ff,
                thumbnail=user.display_avatar.url
            )
            
            if activities:
                activity_text = ""
                for activity in activities:
                    timestamp = datetime.fromisoformat(activity['timestamp'])
                    activity_text += f"**<t:{int(timestamp.timestamp())}:R>** - {activity['type']}: {activity['details']}\n"
                
                embed.add_field(
                    name="Recent Activities",
                    value=activity_text[:1000] if len(activity_text) > 1000 else activity_text,
                    inline=False
                )
        
        await ctx.reply(embed=embed)
    
    @commands.command(name='logsstatus')
    @commands.has_permissions(manage_messages=True)
    async def logs_status(self, ctx):
        """Check logging system status"""
        log_channel = self.get_log_channel(ctx.guild)
        
        embed = discord.Embed(
            title="Logging System Status",
            color=0x00ff00 if log_channel else 0xff0000
        )
        
        if log_channel:
            embed.description = f"✅ Logging to: {log_channel.mention}\n**Channel ID:** {self.log_channel_id}"
            embed.add_field(
                name="Tracked Users",
                value=str(len(self.user_activity_tracker)),
                inline=True
            )
        else:
            embed.description = f"❌ Log channel not found!\n**Expected ID:** {self.log_channel_id}"
        
        await ctx.reply(embed=embed)

async def setup(bot):
    await bot.add_cog(ComprehensiveLogging(bot))
