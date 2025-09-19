import discord
from discord.ext import commands
import json
import os
from datetime import datetime, timedelta
import asyncio
import traceback

class ComprehensiveLogging(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.logs_file = 'data/bot_logs.json'
        self.admin_logs_file = 'data/admin_logs.json'
        self.activity_logs_file = 'data/activity_logs.json'
        self.log_config_file = 'data/log_config.json'
        
        # Ensure data directory exists
        os.makedirs('data', exist_ok=True)
        
        # Load data
        self.load_data()
    
    def load_data(self):
        """Load logging configuration and log data from JSON files"""
        # Load log configuration
        if os.path.exists(self.log_config_file):
            try:
                with open(self.log_config_file, 'r') as f:
                    self.log_config = json.load(f)
            except:
                self.log_config = {
                    'enabled': True,
                    'log_level': 'detailed',  # basic, detailed, verbose
                    'log_channel_id': None,
                    'admin_log_channel_id': None,
                    'retention_days': 30,
                    'log_commands': True,
                    'log_moderation': True,
                    'log_errors': True,
                    'log_activity': True
                }
        else:
            self.log_config = {
                'enabled': True,
                'log_level': 'detailed',
                'log_channel_id': None,
                'admin_log_channel_id': None,
                'retention_days': 30,
                'log_commands': True,
                'log_moderation': True,
                'log_errors': True,
                'log_activity': True
            }
        
        # Load bot logs
        if os.path.exists(self.logs_file):
            try:
                with open(self.logs_file, 'r') as f:
                    self.bot_logs = json.load(f)
            except:
                self.bot_logs = []
        else:
            self.bot_logs = []
        
        # Load admin logs
        if os.path.exists(self.admin_logs_file):
            try:
                with open(self.admin_logs_file, 'r') as f:
                    self.admin_logs = json.load(f)
            except:
                self.admin_logs = []
        else:
            self.admin_logs = []
        
        # Load activity logs
        if os.path.exists(self.activity_logs_file):
            try:
                with open(self.activity_logs_file, 'r') as f:
                    self.activity_logs = json.load(f)
            except:
                self.activity_logs = []
        else:
            self.activity_logs = []
        
        self.save_data()
    
    def save_data(self):
        """Save all log data to JSON files"""
        with open(self.log_config_file, 'w') as f:
            json.dump(self.log_config, f, indent=2)
        
        with open(self.logs_file, 'w') as f:
            json.dump(self.bot_logs, f, indent=2)
        
        with open(self.admin_logs_file, 'w') as f:
            json.dump(self.admin_logs, f, indent=2)
        
        with open(self.activity_logs_file, 'w') as f:
            json.dump(self.activity_logs, f, indent=2)
    
    def log_activity(self, activity_type, user_id, moderator_id, action, details=None, guild_id=None):
        """Log bot activity"""
        if not self.log_config['enabled']:
            return
        
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'activity_type': activity_type,
            'user_id': str(user_id) if user_id else None,
            'moderator_id': str(moderator_id) if moderator_id else None,
            'action': action,
            'details': details or {},
            'guild_id': str(guild_id) if guild_id else None
        }
        
        # Add to appropriate log
        if activity_type in ['moderation', 'warning', 'ban', 'kick', 'mute']:
            self.admin_logs.append(log_entry)
        else:
            self.activity_logs.append(log_entry)
        
        # Clean old logs
        self.clean_old_logs()
        
        self.save_data()
        
        # Send to log channel if configured
        if self.log_config['log_channel_id']:
            asyncio.create_task(self.send_log_to_channel(log_entry))
    
    def log_command(self, ctx, command_name, success=True, error=None):
        """Log command usage"""
        if not self.log_config['log_commands']:
            return
        
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'command': command_name,
            'user_id': str(ctx.author.id),
            'guild_id': str(ctx.guild.id) if ctx.guild else None,
            'channel_id': str(ctx.channel.id),
            'success': success,
            'error': str(error) if error else None,
            'args': ctx.args[2:] if len(ctx.args) > 2 else [],  # Skip bot and ctx
            'kwargs': ctx.kwargs
        }
        
        self.bot_logs.append(log_entry)
        self.clean_old_logs()
        self.save_data()
    
    def log_error(self, error, context=None):
        """Log bot errors"""
        if not self.log_config['log_errors']:
            return
        
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'error_type': type(error).__name__,
            'error_message': str(error),
            'traceback': traceback.format_exc(),
            'context': context or {}
        }
        
        self.bot_logs.append(log_entry)
        self.clean_old_logs()
        self.save_data()
    
    def log_moderation_action(self, action_type, user_id, moderator_id, reason, details=None, guild_id=None):
        """Log moderation actions"""
        if not self.log_config['log_moderation']:
            return
        
        self.log_activity(
            'moderation',
            user_id,
            moderator_id,
            action_type,
            {
                'reason': reason,
                'details': details or {}
            },
            guild_id
        )
    
    def clean_old_logs(self):
        """Clean logs older than retention period"""
        cutoff_date = datetime.now() - timedelta(days=self.log_config['retention_days'])
        
        # Clean bot logs
        self.bot_logs = [
            log for log in self.bot_logs
            if datetime.fromisoformat(log['timestamp']) > cutoff_date
        ]
        
        # Clean admin logs
        self.admin_logs = [
            log for log in self.admin_logs
            if datetime.fromisoformat(log['timestamp']) > cutoff_date
        ]
        
        # Clean activity logs
        self.activity_logs = [
            log for log in self.activity_logs
            if datetime.fromisoformat(log['timestamp']) > cutoff_date
        ]
    
    async def send_log_to_channel(self, log_entry):
        """Send log entry to configured channel"""
        try:
            channel = self.bot.get_channel(self.log_config['log_channel_id'])
            if channel:
                embed = self.create_log_embed(log_entry)
                await channel.send(embed=embed)
        except Exception as e:
            print(f"Error sending log to channel: {e}")
    
    def create_log_embed(self, log_entry):
        """Create embed for log entry"""
        activity_type = log_entry['activity_type']
        
        # Set color based on activity type
        if activity_type in ['moderation', 'warning', 'ban', 'kick']:
            color = 0xff0000  # Red
        elif activity_type in ['error']:
            color = 0xff8800  # Orange
        else:
            color = 0x0099ff  # Blue
        
        embed = discord.Embed(
            title=f"📋 Bot Activity Log",
            color=color,
            timestamp=datetime.fromisoformat(log_entry['timestamp'])
        )
        
        embed.add_field(
            name="🔍 Activity Type",
            value=activity_type.title(),
            inline=True
        )
        
        if log_entry['user_id']:
            try:
                user = self.bot.get_user(int(log_entry['user_id']))
                user_name = user.display_name if user else f"Unknown ({log_entry['user_id']})"
            except:
                user_name = f"Unknown ({log_entry['user_id']})"
            
            embed.add_field(
                name="👤 User",
                value=user_name,
                inline=True
            )
        
        if log_entry['moderator_id']:
            try:
                moderator = self.bot.get_user(int(log_entry['moderator_id']))
                moderator_name = moderator.display_name if moderator else f"Unknown ({log_entry['moderator_id']})"
            except:
                moderator_name = f"Unknown ({log_entry['moderator_id']})"
            
            embed.add_field(
                name="👮‍♂️ Moderator",
                value=moderator_name,
                inline=True
            )
        
        embed.add_field(
            name="⚡ Action",
            value=log_entry['action'],
            inline=False
        )
        
        if log_entry['details']:
            details_text = str(log_entry['details'])[:1000]  # Limit length
            embed.add_field(
                name="📝 Details",
                value=details_text,
                inline=False
            )
        
        embed.set_footer(text="Bot Activity Log")
        
        return embed
    
    @commands.command(name='bot_logs')
    @commands.has_permissions(administrator=True)
    async def bot_logs_command(self, ctx, log_type: str = 'all', limit: int = 20):
        """View bot logs (admin only)"""
        if log_type.lower() == 'all':
            logs = self.bot_logs[-limit:]
        elif log_type.lower() == 'admin':
            logs = self.admin_logs[-limit:]
        elif log_type.lower() == 'activity':
            logs = self.activity_logs[-limit:]
        else:
            await ctx.send("❌ Invalid log type. Use: all, admin, activity")
            return
        
        if not logs:
            await ctx.send(f"No {log_type} logs found.")
            return
        
        embed = discord.Embed(
            title=f"📋 Bot Logs: {log_type.title()}",
            color=0x0099ff,
            timestamp=datetime.now()
        )
        
        for i, log in enumerate(reversed(logs), 1):
            log_text = f"**Time:** {datetime.fromisoformat(log['timestamp']).strftime('%Y-%m-%d %H:%M')}\n"
            
            if 'command' in log:
                log_text += f"**Command:** {log['command']}\n"
                log_text += f"**User:** {log.get('user_id', 'Unknown')}\n"
                log_text += f"**Success:** {log.get('success', 'Unknown')}\n"
            elif 'activity_type' in log:
                log_text += f"**Type:** {log['activity_type']}\n"
                log_text += f"**Action:** {log['action']}\n"
                log_text += f"**User:** {log.get('user_id', 'Unknown')}\n"
            elif 'error_type' in log:
                log_text += f"**Error:** {log['error_type']}\n"
                log_text += f"**Message:** {log['error_message'][:100]}...\n"
            
            embed.add_field(
                name=f"Log #{i}",
                value=log_text,
                inline=False
            )
        
        embed.set_footer(text=f"Showing last {len(logs)} of {len(self.bot_logs)} total logs")
        await ctx.send(embed=embed)
    
    @commands.command(name='log_config')
    @commands.has_permissions(administrator=True)
    async def log_config_command(self, ctx, setting: str, *, value: str):
        """Configure logging settings (admin only)"""
        if setting.lower() == 'enabled':
            self.log_config['enabled'] = value.lower() in ['true', 'yes', '1', 'on']
            await ctx.send(f"✅ Logging enabled: {self.log_config['enabled']}")
        
        elif setting.lower() == 'log_level':
            if value.lower() in ['basic', 'detailed', 'verbose']:
                self.log_config['log_level'] = value.lower()
                await ctx.send(f"✅ Log level set to: {self.log_config['log_level']}")
            else:
                await ctx.send("❌ Invalid log level. Use: basic, detailed, verbose")
        
        elif setting.lower() == 'log_channel':
            try:
                channel_id = int(value)
                channel = self.bot.get_channel(channel_id)
                if channel:
                    self.log_config['log_channel_id'] = channel_id
                    await ctx.send(f"✅ Log channel set to: {channel.mention}")
                else:
                    await ctx.send("❌ Channel not found.")
            except ValueError:
                await ctx.send("❌ Invalid channel ID.")
        
        elif setting.lower() == 'admin_log_channel':
            try:
                channel_id = int(value)
                channel = self.bot.get_channel(channel_id)
                if channel:
                    self.log_config['admin_log_channel_id'] = channel_id
                    await ctx.send(f"✅ Admin log channel set to: {channel.mention}")
                else:
                    await ctx.send("❌ Channel not found.")
            except ValueError:
                await ctx.send("❌ Invalid channel ID.")
        
        elif setting.lower() == 'retention_days':
            try:
                days = int(value)
                if 1 <= days <= 365:
                    self.log_config['retention_days'] = days
                    await ctx.send(f"✅ Log retention set to: {days} days")
                else:
                    await ctx.send("❌ Invalid retention period. Use 1-365 days.")
            except ValueError:
                await ctx.send("❌ Invalid number.")
        
        elif setting.lower() == 'log_commands':
            self.log_config['log_commands'] = value.lower() in ['true', 'yes', '1', 'on']
            await ctx.send(f"✅ Command logging: {self.log_config['log_commands']}")
        
        elif setting.lower() == 'log_moderation':
            self.log_config['log_moderation'] = value.lower() in ['true', 'yes', '1', 'on']
            await ctx.send(f"✅ Moderation logging: {self.log_config['log_moderation']}")
        
        elif setting.lower() == 'log_errors':
            self.log_config['log_errors'] = value.lower() in ['true', 'yes', '1', 'on']
            await ctx.send(f"✅ Error logging: {self.log_config['log_errors']}")
        
        elif setting.lower() == 'log_activity':
            self.log_config['log_activity'] = value.lower() in ['true', 'yes', '1', 'on']
            await ctx.send(f"✅ Activity logging: {self.log_config['log_activity']}")
        
        else:
            await ctx.send("❌ Invalid setting. Available: enabled, log_level, log_channel, admin_log_channel, retention_days, log_commands, log_moderation, log_errors, log_activity")
        
        self.save_data()
    
    @commands.command(name='log_status')
    @commands.has_permissions(administrator=True)
    async def log_status_command(self, ctx):
        """Show current logging configuration (admin only)"""
        embed = discord.Embed(
            title="📋 Logging Configuration",
            color=0x0099ff,
            timestamp=datetime.now()
        )
        
        embed.add_field(
            name="🔄 Status",
            value="✅ Enabled" if self.log_config['enabled'] else "❌ Disabled",
            inline=True
        )
        
        embed.add_field(
            name="📊 Log Level",
            value=self.log_config['log_level'].title(),
            inline=True
        )
        
        embed.add_field(
            name="⏰ Retention",
            value=f"{self.log_config['retention_days']} days",
            inline=True
        )
        
        if self.log_config['log_channel_id']:
            channel = self.bot.get_channel(self.log_config['log_channel_id'])
            channel_name = channel.mention if channel else "Unknown Channel"
            embed.add_field(
                name="📝 Log Channel",
                value=channel_name,
                inline=True
            )
        else:
            embed.add_field(
                name="📝 Log Channel",
                value="❌ Not set",
                inline=True
            )
        
        if self.log_config['admin_log_channel_id']:
            channel = self.bot.get_channel(self.log_config['admin_log_channel_id'])
            channel_name = channel.mention if channel else "Unknown Channel"
            embed.add_field(
                name="👮‍♂️ Admin Log Channel",
                value=channel_name,
                inline=True
            )
        else:
            embed.add_field(
                name="👮‍♂️ Admin Log Channel",
                value="❌ Not set",
                inline=True
            )
        
        # Show log counts
        embed.add_field(
            name="📊 Log Counts",
            value=f"**Bot Logs:** {len(self.bot_logs)}\n"
                  f"**Admin Logs:** {len(self.admin_logs)}\n"
                  f"**Activity Logs:** {len(self.activity_logs)}",
            inline=False
        )
        
        # Show logging options
        embed.add_field(
            name="🔧 Logging Options",
            value=f"**Commands:** {'✅' if self.log_config['log_commands'] else '❌'}\n"
                  f"**Moderation:** {'✅' if self.log_config['log_moderation'] else '❌'}\n"
                  f"**Errors:** {'✅' if self.log_config['log_errors'] else '❌'}\n"
                  f"**Activity:** {'✅' if self.log_config['log_activity'] else '❌'}",
            inline=True
        )
        
        await ctx.send(embed=embed)
    
    @commands.command(name='clear_logs')
    @commands.has_permissions(administrator=True)
    async def clear_logs_command(self, ctx, log_type: str = 'all'):
        """Clear logs (admin only)"""
        if log_type.lower() == 'all':
            self.bot_logs = []
            self.admin_logs = []
            self.activity_logs = []
            await ctx.send("✅ All logs cleared.")
        elif log_type.lower() == 'bot':
            self.bot_logs = []
            await ctx.send("✅ Bot logs cleared.")
        elif log_type.lower() == 'admin':
            self.admin_logs = []
            await ctx.send("✅ Admin logs cleared.")
        elif log_type.lower() == 'activity':
            self.activity_logs = []
            await ctx.send("✅ Activity logs cleared.")
        else:
            await ctx.send("❌ Invalid log type. Use: all, bot, admin, activity")
        
        self.save_data()
    
    @commands.Cog.listener()
    async def on_command(self, ctx):
        """Log command usage"""
        self.log_command(ctx, ctx.command.name)
    
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        """Log command errors"""
        self.log_command(ctx, ctx.command.name, success=False, error=error)
        self.log_error(error, {'command': ctx.command.name, 'user_id': ctx.author.id})

async def setup(bot):
    await bot.add_cog(ComprehensiveLogging(bot))
