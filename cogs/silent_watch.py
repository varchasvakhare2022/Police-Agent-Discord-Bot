import discord
from discord.ext import commands
import json
import os
from datetime import datetime, timedelta
import asyncio

class SilentWatchMode(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.watch_data_file = 'data/watch_data.json'
        self.watch_config_file = 'data/watch_config.json'
        self.suspicious_activity_file = 'data/suspicious_activity.json'
        
        # Ensure data directory exists
        os.makedirs('data', exist_ok=True)
        
        # Load data
        self.load_data()
    
    def load_data(self):
        """Load watch data, configuration, and suspicious activity from JSON files"""
        # Load watch data
        if os.path.exists(self.watch_data_file):
            try:
                with open(self.watch_data_file, 'r') as f:
                    self.watch_data = json.load(f)
            except:
                self.watch_data = {}
        else:
            self.watch_data = {}
        
        # Load watch configuration
        if os.path.exists(self.watch_config_file):
            try:
                with open(self.watch_config_file, 'r') as f:
                    self.watch_config = json.load(f)
            except:
                self.watch_config = {
                    'enabled': True,
                    'thresholds': {
                        'message_count': 50,  # Messages per hour
                        'edit_count': 20,     # Edits per hour
                        'delete_count': 10,   # Deletions per hour
                        'join_count': 5       # Joins per hour
                    },
                    'alert_channel_id': None,
                    'watch_duration': 24,  # Hours
                    'auto_watch': True
                }
        else:
            self.watch_config = {
                'enabled': True,
                'thresholds': {
                    'message_count': 50,
                    'edit_count': 20,
                    'delete_count': 10,
                    'join_count': 5
                },
                'alert_channel_id': None,
                'watch_duration': 24,
                'auto_watch': True
            }
        
        # Load suspicious activity
        if os.path.exists(self.suspicious_activity_file):
            try:
                with open(self.suspicious_activity_file, 'r') as f:
                    self.suspicious_activity = json.load(f)
            except:
                self.suspicious_activity = {}
        else:
            self.suspicious_activity = {}
        
        self.save_data()
    
    def save_data(self):
        """Save watch data, configuration, and suspicious activity to JSON files"""
        with open(self.watch_data_file, 'w') as f:
            json.dump(self.watch_data, f, indent=2)
        
        with open(self.watch_config_file, 'w') as f:
            json.dump(self.watch_config, f, indent=2)
        
        with open(self.suspicious_activity_file, 'w') as f:
            json.dump(self.suspicious_activity, f, indent=2)
    
    def get_user_watch_data(self, user_id):
        """Get or create watch data for a user"""
        user_id = str(user_id)
        if user_id not in self.watch_data:
            self.watch_data[user_id] = {
                'is_watched': False,
                'watch_start': None,
                'watch_end': None,
                'activities': {
                    'messages': [],
                    'edits': [],
                    'deletions': [],
                    'joins': []
                },
                'suspicious_score': 0,
                'last_activity': None
            }
        return self.watch_data[user_id]
    
    def add_activity(self, user_id, activity_type, data):
        """Add activity to user's watch data"""
        user_data = self.get_user_watch_data(user_id)
        
        activity_entry = {
            'timestamp': datetime.now().isoformat(),
            'data': data
        }
        
        user_data['activities'][activity_type].append(activity_entry)
        user_data['last_activity'] = datetime.now().isoformat()
        
        # Clean old activities (keep last 24 hours)
        cutoff_time = datetime.now() - timedelta(hours=24)
        for activity_type in user_data['activities']:
            user_data['activities'][activity_type] = [
                activity for activity in user_data['activities'][activity_type]
                if datetime.fromisoformat(activity['timestamp']) > cutoff_time
            ]
        
        self.save_data()
        
        # Check thresholds
        self.check_thresholds(user_id)
    
    def check_thresholds(self, user_id):
        """Check if user has crossed any thresholds"""
        user_data = self.get_user_watch_data(user_id)
        
        # Count activities in last hour
        cutoff_time = datetime.now() - timedelta(hours=1)
        
        message_count = len([
            activity for activity in user_data['activities']['messages']
            if datetime.fromisoformat(activity['timestamp']) > cutoff_time
        ])
        
        edit_count = len([
            activity for activity in user_data['activities']['edits']
            if datetime.fromisoformat(activity['timestamp']) > cutoff_time
        ])
        
        delete_count = len([
            activity for activity in user_data['activities']['deletions']
            if datetime.fromisoformat(activity['timestamp']) > cutoff_time
        ])
        
        join_count = len([
            activity for activity in user_data['activities']['joins']
            if datetime.fromisoformat(activity['timestamp']) > cutoff_time
        ])
        
        # Check thresholds
        thresholds = self.watch_config['thresholds']
        crossed_thresholds = []
        
        if message_count >= thresholds['message_count']:
            crossed_thresholds.append(f"Messages: {message_count}/{thresholds['message_count']}")
        
        if edit_count >= thresholds['edit_count']:
            crossed_thresholds.append(f"Edits: {edit_count}/{thresholds['edit_count']}")
        
        if delete_count >= thresholds['delete_count']:
            crossed_thresholds.append(f"Deletions: {delete_count}/{thresholds['delete_count']}")
        
        if join_count >= thresholds['join_count']:
            crossed_thresholds.append(f"Joins: {join_count}/{thresholds['join_count']}")
        
        # If thresholds crossed, alert moderators
        if crossed_thresholds:
            self.alert_moderators(user_id, crossed_thresholds)
    
    def alert_moderators(self, user_id, crossed_thresholds):
        """Alert moderators about suspicious activity"""
        user_data = self.get_user_watch_data(user_id)
        
        # Create alert
        alert = {
            'timestamp': datetime.now().isoformat(),
            'user_id': user_id,
            'crossed_thresholds': crossed_thresholds,
            'suspicious_score': user_data['suspicious_score']
        }
        
        self.suspicious_activity[user_id] = alert
        
        # Send alert to channel if configured
        if self.watch_config['alert_channel_id']:
            asyncio.create_task(self.send_alert_to_channel(alert))
        
        self.save_data()
    
    async def send_alert_to_channel(self, alert):
        """Send alert to configured channel"""
        try:
            channel = self.bot.get_channel(self.watch_config['alert_channel_id'])
            if channel:
                user = self.bot.get_user(int(alert['user_id']))
                username = user.display_name if user else f"Unknown ({alert['user_id']})"
                
                embed = discord.Embed(
                    title="🚨 Suspicious Activity Alert",
                    color=0xff0000,
                    timestamp=datetime.now()
                )
                
                embed.add_field(
                    name="👤 User",
                    value=username,
                    inline=True
                )
                
                embed.add_field(
                    name="⚠️ Crossed Thresholds",
                    value="\n".join(alert['crossed_thresholds']),
                    inline=False
                )
                
                embed.add_field(
                    name="📊 Suspicious Score",
                    value=str(alert['suspicious_score']),
                    inline=True
                )
                
                embed.set_footer(text="Silent Watch Mode Alert")
                
                await channel.send(embed=embed)
        except Exception as e:
            print(f"Error sending alert: {e}")
    
    @commands.command(name='watch_user')
    @commands.has_permissions(manage_messages=True)
    async def watch_user_command(self, ctx, member: discord.Member, duration: int = 24):
        """Start watching a user"""
        user_data = self.get_user_watch_data(member.id)
        
        if user_data['is_watched']:
            await ctx.send(f"❌ {member.mention} is already being watched.")
            return
        
        user_data['is_watched'] = True
        user_data['watch_start'] = datetime.now().isoformat()
        user_data['watch_end'] = (datetime.now() + timedelta(hours=duration)).isoformat()
        
        self.save_data()
        
        embed = discord.Embed(
            title="👁️ Silent Watch Mode Activated",
            color=0x0099ff,
            timestamp=datetime.now()
        )
        
        embed.add_field(name="👤 User", value=member.mention, inline=True)
        embed.add_field(name="⏰ Duration", value=f"{duration} hours", inline=True)
        embed.add_field(name="📊 Status", value="Watching", inline=True)
        
        await ctx.send(embed=embed)
    
    @commands.command(name='unwatch_user')
    @commands.has_permissions(manage_messages=True)
    async def unwatch_user_command(self, ctx, member: discord.Member):
        """Stop watching a user"""
        user_data = self.get_user_watch_data(member.id)
        
        if not user_data['is_watched']:
            await ctx.send(f"❌ {member.mention} is not being watched.")
            return
        
        user_data['is_watched'] = False
        user_data['watch_end'] = datetime.now().isoformat()
        
        self.save_data()
        
        embed = discord.Embed(
            title="👁️ Silent Watch Mode Deactivated",
            color=0x00ff00,
            timestamp=datetime.now()
        )
        
        embed.add_field(name="👤 User", value=member.mention, inline=True)
        embed.add_field(name="📊 Status", value="Stopped Watching", inline=True)
        
        await ctx.send(embed=embed)
    
    @commands.command(name='watch_status')
    @commands.has_permissions(manage_messages=True)
    async def watch_status_command(self, ctx, member: discord.Member = None):
        """Check watch status for a user"""
        if member:
            user_data = self.get_user_watch_data(member.id)
            
            embed = discord.Embed(
                title=f"👁️ Watch Status: {member.display_name}",
                color=0x0099ff,
                timestamp=datetime.now()
            )
            
            embed.add_field(
                name="📊 Status",
                value="Being Watched" if user_data['is_watched'] else "Not Watched",
                inline=True
            )
            
            if user_data['is_watched']:
                embed.add_field(
                    name="⏰ Watch Started",
                    value=datetime.fromisoformat(user_data['watch_start']).strftime('%Y-%m-%d %H:%M'),
                    inline=True
                )
                
                embed.add_field(
                    name="⏰ Watch Ends",
                    value=datetime.fromisoformat(user_data['watch_end']).strftime('%Y-%m-%d %H:%M'),
                    inline=True
                )
            
            # Show activity counts
            message_count = len(user_data['activities']['messages'])
            edit_count = len(user_data['activities']['edits'])
            delete_count = len(user_data['activities']['deletions'])
            join_count = len(user_data['activities']['joins'])
            
            embed.add_field(
                name="📈 Activity (24h)",
                value=f"Messages: {message_count}\nEdits: {edit_count}\nDeletions: {delete_count}\nJoins: {join_count}",
                inline=False
            )
            
            embed.add_field(
                name="⚠️ Suspicious Score",
                value=str(user_data['suspicious_score']),
                inline=True
            )
            
            await ctx.send(embed=embed)
        else:
            # Show all watched users
            watched_users = [
                user_id for user_id, data in self.watch_data.items()
                if data['is_watched']
            ]
            
            if not watched_users:
                await ctx.send("No users are currently being watched.")
                return
            
            embed = discord.Embed(
                title="👁️ Currently Watched Users",
                color=0x0099ff,
                timestamp=datetime.now()
            )
            
            for user_id in watched_users:
                try:
                    user = await self.bot.fetch_user(int(user_id))
                    username = user.display_name
                except:
                    username = f"Unknown ({user_id})"
                
                user_data = self.watch_data[user_id]
                embed.add_field(
                    name=username,
                    value=f"Score: {user_data['suspicious_score']}\n"
                          f"Messages: {len(user_data['activities']['messages'])}",
                    inline=True
                )
            
            await ctx.send(embed=embed)
    
    @commands.command(name='watch_config')
    @commands.has_permissions(administrator=True)
    async def watch_config_command(self, ctx, setting: str, *, value: str):
        """Configure watch mode settings (admin only)"""
        if setting.lower() == 'enabled':
            self.watch_config['enabled'] = value.lower() in ['true', 'yes', '1', 'on']
            await ctx.send(f"✅ Watch mode enabled: {self.watch_config['enabled']}")
        
        elif setting.lower() == 'alert_channel':
            try:
                channel_id = int(value)
                channel = self.bot.get_channel(channel_id)
                if channel:
                    self.watch_config['alert_channel_id'] = channel_id
                    await ctx.send(f"✅ Alert channel set to: {channel.mention}")
                else:
                    await ctx.send("❌ Channel not found.")
            except ValueError:
                await ctx.send("❌ Invalid channel ID.")
        
        elif setting.lower() == 'message_threshold':
            try:
                threshold = int(value)
                self.watch_config['thresholds']['message_count'] = threshold
                await ctx.send(f"✅ Message threshold set to: {threshold}")
            except ValueError:
                await ctx.send("❌ Invalid threshold value.")
        
        elif setting.lower() == 'edit_threshold':
            try:
                threshold = int(value)
                self.watch_config['thresholds']['edit_count'] = threshold
                await ctx.send(f"✅ Edit threshold set to: {threshold}")
            except ValueError:
                await ctx.send("❌ Invalid threshold value.")
        
        elif setting.lower() == 'delete_threshold':
            try:
                threshold = int(value)
                self.watch_config['thresholds']['delete_count'] = threshold
                await ctx.send(f"✅ Delete threshold set to: {threshold}")
            except ValueError:
                await ctx.send("❌ Invalid threshold value.")
        
        elif setting.lower() == 'join_threshold':
            try:
                threshold = int(value)
                self.watch_config['thresholds']['join_count'] = threshold
                await ctx.send(f"✅ Join threshold set to: {threshold}")
            except ValueError:
                await ctx.send("❌ Invalid threshold value.")
        
        else:
            await ctx.send("❌ Invalid setting. Available: enabled, alert_channel, message_threshold, edit_threshold, delete_threshold, join_threshold")
        
        self.save_data()
    
    @commands.command(name='watch_alerts')
    @commands.has_permissions(manage_messages=True)
    async def watch_alerts_command(self, ctx):
        """View recent suspicious activity alerts"""
        if not self.suspicious_activity:
            await ctx.send("No suspicious activity alerts found.")
            return
        
        embed = discord.Embed(
            title="🚨 Recent Suspicious Activity Alerts",
            color=0xff0000,
            timestamp=datetime.now()
        )
        
        # Show last 10 alerts
        recent_alerts = list(self.suspicious_activity.items())[-10:]
        
        for user_id, alert in recent_alerts:
            try:
                user = await self.bot.fetch_user(int(user_id))
                username = user.display_name
            except:
                username = f"Unknown ({user_id})"
            
            embed.add_field(
                name=f"👤 {username}",
                value=f"**Thresholds:** {', '.join(alert['crossed_thresholds'])}\n"
                      f"**Score:** {alert['suspicious_score']}\n"
                      f"**Time:** {datetime.fromisoformat(alert['timestamp']).strftime('%Y-%m-%d %H:%M')}",
                inline=True
            )
        
        await ctx.send(embed=embed)
    
    @commands.Cog.listener()
    async def on_message(self, message):
        """Track user messages"""
        if message.author.bot or not self.watch_config['enabled']:
            return
        
        user_data = self.get_user_watch_data(message.author.id)
        if user_data['is_watched']:
            self.add_activity(message.author.id, 'messages', {
                'content': message.content,
                'channel_id': message.channel.id,
                'message_id': message.id
            })
    
    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        """Track message edits"""
        if after.author.bot or not self.watch_config['enabled']:
            return
        
        user_data = self.get_user_watch_data(after.author.id)
        if user_data['is_watched']:
            self.add_activity(after.author.id, 'edits', {
                'before': before.content,
                'after': after.content,
                'channel_id': after.channel.id,
                'message_id': after.id
            })
    
    @commands.Cog.listener()
    async def on_message_delete(self, message):
        """Track message deletions"""
        if message.author.bot or not self.watch_config['enabled']:
            return
        
        user_data = self.get_user_watch_data(message.author.id)
        if user_data['is_watched']:
            self.add_activity(message.author.id, 'deletions', {
                'content': message.content,
                'channel_id': message.channel.id,
                'message_id': message.id
            })
    
    @commands.Cog.listener()
    async def on_member_join(self, member):
        """Track member joins"""
        if not self.watch_config['enabled']:
            return
        
        user_data = self.get_user_watch_data(member.id)
        if user_data['is_watched']:
            self.add_activity(member.id, 'joins', {
                'guild_id': member.guild.id,
                'joined_at': member.joined_at.isoformat() if member.joined_at else None
            })

async def setup(bot):
    await bot.add_cog(SilentWatchMode(bot))
