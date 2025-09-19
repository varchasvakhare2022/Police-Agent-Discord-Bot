import discord
from discord.ext import commands, tasks
import json
import os
from datetime import datetime, timedelta
import asyncio

class DailySecurityReport(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.report_config_file = 'data/report_config.json'
        self.daily_violations_file = 'data/daily_violations.json'
        
        # Ensure data directory exists
        os.makedirs('data', exist_ok=True)
        
        # Load data
        self.load_data()
        
        # Start daily report task
        self.daily_report_task.start()
    
    def load_data(self):
        """Load report configuration and daily violations from JSON files"""
        # Load report config
        if os.path.exists(self.report_config_file):
            try:
                with open(self.report_config_file, 'r') as f:
                    self.report_config = json.load(f)
            except:
                self.report_config = {
                    'dm_admins': True,
                    'logs_channel_id': None,
                    'report_time': '18:00',  # 6 PM
                    'enabled': True
                }
        else:
            self.report_config = {
                'dm_admins': True,
                'logs_channel_id': None,
                'report_time': '18:00',
                'enabled': True
            }
        
        # Load daily violations
        if os.path.exists(self.daily_violations_file):
            try:
                with open(self.daily_violations_file, 'r') as f:
                    self.daily_violations = json.load(f)
            except:
                self.daily_violations = {}
        else:
            self.daily_violations = {}
        
        self.save_data()
    
    def save_data(self):
        """Save report configuration and daily violations to JSON files"""
        with open(self.report_config_file, 'w') as f:
            json.dump(self.report_config, f, indent=2)
        
        with open(self.daily_violations_file, 'w') as f:
            json.dump(self.daily_violations, f, indent=2)
    
    def record_violation(self, violation_type, user_id, moderator_id, reason, details=None):
        """Record a violation for daily reporting"""
        today = datetime.now().strftime('%Y-%m-%d')
        
        if today not in self.daily_violations:
            self.daily_violations[today] = {
                'violations': [],
                'summary': {
                    'total_violations': 0,
                    'violation_types': {},
                    'users_violated': set(),
                    'moderators_active': set()
                }
            }
        
        violation_entry = {
            'timestamp': datetime.now().isoformat(),
            'type': violation_type,
            'user_id': str(user_id),
            'moderator_id': str(moderator_id),
            'reason': reason,
            'details': details or {}
        }
        
        self.daily_violations[today]['violations'].append(violation_entry)
        
        # Update summary
        summary = self.daily_violations[today]['summary']
        summary['total_violations'] += 1
        summary['violation_types'][violation_type] = summary['violation_types'].get(violation_type, 0) + 1
        summary['users_violated'].add(str(user_id))
        summary['moderators_active'].add(str(moderator_id))
        
        self.save_data()
    
    def get_today_violations(self):
        """Get today's violations"""
        today = datetime.now().strftime('%Y-%m-%d')
        return self.daily_violations.get(today, {
            'violations': [],
            'summary': {
                'total_violations': 0,
                'violation_types': {},
                'users_violated': set(),
                'moderators_active': set()
            }
        })
    
    def generate_security_report(self):
        """Generate daily security report"""
        today_data = self.get_today_violations()
        summary = today_data['summary']
        violations = today_data['violations']
        
        # Create embed
        embed = discord.Embed(
            title="🛡️ Daily Security Report",
            description=f"Security summary for {datetime.now().strftime('%Y-%m-%d')}",
            color=0x0099ff,
            timestamp=datetime.now()
        )
        
        # Overall statistics
        embed.add_field(
            name="📊 Overall Statistics",
            value=f"**Total Violations:** {summary['total_violations']}\n"
                  f"**Users Violated:** {len(summary['users_violated'])}\n"
                  f"**Moderators Active:** {len(summary['moderators_active'])}",
            inline=False
        )
        
        # Violation types breakdown
        if summary['violation_types']:
            type_text = "\n".join([f"**{k.title()}:** {v}" for k, v in summary['violation_types'].items()])
            embed.add_field(
                name="⚠️ Violation Types",
                value=type_text,
                inline=True
            )
        
        # Recent violations (last 5)
        if violations:
            recent_violations = violations[-5:]
            violation_text = ""
            for violation in recent_violations:
                try:
                    user = self.bot.get_user(int(violation['user_id']))
                    username = user.display_name if user else f"Unknown ({violation['user_id']})"
                except:
                    username = f"Unknown ({violation['user_id']})"
                
                moderator = self.bot.get_user(int(violation['moderator_id']))
                moderator_name = moderator.display_name if moderator else "Unknown"
                
                violation_text += f"**{violation['type'].title()}** - {username}\n"
                violation_text += f"*Moderator:* {moderator_name}\n"
                violation_text += f"*Reason:* {violation['reason'][:50]}...\n\n"
            
            embed.add_field(
                name="🔍 Recent Violations",
                value=violation_text,
                inline=False
            )
        
        # Security status
        if summary['total_violations'] == 0:
            status = "🟢 **EXCELLENT** - No violations today!"
            embed.color = 0x00ff00
        elif summary['total_violations'] <= 3:
            status = "🟡 **GOOD** - Low violation count"
            embed.color = 0xffff00
        elif summary['total_violations'] <= 10:
            status = "🟠 **MODERATE** - Some violations detected"
            embed.color = 0xff8800
        else:
            status = "🔴 **HIGH** - Many violations detected"
            embed.color = 0xff0000
        
        embed.add_field(
            name="🛡️ Security Status",
            value=status,
            inline=False
        )
        
        embed.set_footer(text="Daily Security Report - Police Agent Bot")
        
        return embed
    
    async def send_report_to_admins(self, embed):
        """Send report to all admins via DM"""
        if not self.report_config['dm_admins']:
            return
        
        for guild in self.bot.guilds:
            admins = [member for member in guild.members 
                     if member.guild_permissions.administrator and not member.bot]
            
            for admin in admins:
                try:
                    await admin.send(embed=embed)
                except discord.Forbidden:
                    # Admin has DMs disabled
                    continue
                except Exception as e:
                    print(f"Error sending DM to admin {admin}: {e}")
    
    async def send_report_to_logs(self, embed):
        """Send report to logs channel"""
        if not self.report_config['logs_channel_id']:
            return
        
        try:
            channel = self.bot.get_channel(self.report_config['logs_channel_id'])
            if channel:
                await channel.send(embed=embed)
        except Exception as e:
            print(f"Error sending report to logs channel: {e}")
    
    @tasks.loop(time=datetime.time(hour=18, minute=30))  # 12:00 AM IST (UTC+5:30)
    async def daily_report_task(self):
        """Daily report task - runs at 12:00 AM IST"""
        if not self.report_config['enabled']:
            return
        
        # Generate report
        embed = self.generate_security_report()
        
        # Send to admins via DM
        await self.send_report_to_admins(embed)
        
        # Send to logs channel
        await self.send_report_to_logs(embed)
        
        # Reset daily violations for next day
        self.daily_violations = {}
        self.save_data()
    
    @daily_report_task.before_loop
    async def before_daily_report(self):
        """Wait until bot is ready"""
        await self.bot.wait_until_ready()
    
    @commands.command(name='security report')
    @commands.has_permissions(manage_messages=True)
    async def manual_security_report(self, ctx):
        """Manually generate and send security report"""
        embed = self.generate_security_report()
        await ctx.send(embed=embed)
    
    @commands.command(name='report config')
    @commands.has_permissions(administrator=True)
    async def report_config_command(self, ctx, setting: str, value: str):
        """Configure daily security reports"""
        if setting.lower() == 'dm_admins':
            self.report_config['dm_admins'] = value.lower() in ['true', 'yes', '1', 'on']
            await ctx.send(f"✅ DM admins set to: {self.report_config['dm_admins']}")
        
        elif setting.lower() == 'logs_channel':
            try:
                channel_id = int(value)
                channel = self.bot.get_channel(channel_id)
                if channel:
                    self.report_config['logs_channel_id'] = channel_id
                    await ctx.send(f"✅ Logs channel set to: {channel.mention}")
                else:
                    await ctx.send("❌ Channel not found.")
            except ValueError:
                await ctx.send("❌ Invalid channel ID.")
        
        elif setting.lower() == 'report_time':
            try:
                # Validate time format (HH:MM)
                datetime.strptime(value, '%H:%M')
                self.report_config['report_time'] = value
                await ctx.send(f"✅ Report time set to: {value}")
            except ValueError:
                await ctx.send("❌ Invalid time format. Use HH:MM (e.g., 18:00)")
        
        elif setting.lower() == 'enabled':
            self.report_config['enabled'] = value.lower() in ['true', 'yes', '1', 'on']
            await ctx.send(f"✅ Daily reports enabled: {self.report_config['enabled']}")
        
        else:
            await ctx.send("❌ Invalid setting. Available: dm_admins, logs_channel, report_time, enabled")
        
        self.save_data()
    
    @commands.command(name='report status')
    @commands.has_permissions(manage_messages=True)
    async def report_status_command(self, ctx):
        """Show current report configuration"""
        embed = discord.Embed(
            title="📊 Daily Security Report Configuration",
            color=0x0099ff,
            timestamp=datetime.now()
        )
        
        embed.add_field(
            name="📧 DM Admins",
            value="✅ Enabled" if self.report_config['dm_admins'] else "❌ Disabled",
            inline=True
        )
        
        if self.report_config['logs_channel_id']:
            channel = self.bot.get_channel(self.report_config['logs_channel_id'])
            channel_name = channel.mention if channel else "Unknown Channel"
            embed.add_field(
                name="📝 Logs Channel",
                value=channel_name,
                inline=True
            )
        else:
            embed.add_field(
                name="📝 Logs Channel",
                value="❌ Not set",
                inline=True
            )
        
        embed.add_field(
            name="⏰ Report Time",
            value=self.report_config['report_time'],
            inline=True
        )
        
        embed.add_field(
            name="🔄 Status",
            value="✅ Enabled" if self.report_config['enabled'] else "❌ Disabled",
            inline=True
        )
        
        # Show today's violations count
        today_data = self.get_today_violations()
        embed.add_field(
            name="📊 Today's Violations",
            value=str(today_data['summary']['total_violations']),
            inline=True
        )
        
        await ctx.send(embed=embed)
    
    @commands.command(name='test report')
    @commands.has_permissions(administrator=True)
    async def test_report_command(self, ctx):
        """Test the daily security report system"""
        embed = self.generate_security_report()
        await ctx.send("🧪 **Test Report Generated:**", embed=embed)
    
    @commands.command(name='stop daily reports')
    @commands.has_permissions(administrator=True)
    async def stop_daily_reports_command(self, ctx):
        """Stop the daily security reports"""
        if self.daily_report_task.is_running():
            self.daily_report_task.cancel()
            await ctx.send("✅ Daily security reports have been stopped.")
        else:
            await ctx.send("❌ Daily security reports are not currently running.")
    
    @commands.command(name='start daily reports')
    @commands.has_permissions(administrator=True)
    async def start_daily_reports_command(self, ctx):
        """Start the daily security reports"""
        if not self.daily_report_task.is_running():
            self.daily_report_task.start()
            await ctx.send("✅ Daily security reports have been started. They will run at 12:00 AM IST daily.")
        else:
            await ctx.send("❌ Daily security reports are already running.")
    
    @commands.command(name='add violation')
    @commands.has_permissions(manage_messages=True)
    async def add_violation_command(self, ctx, violation_type: str, user: discord.Member, *, reason: str):
        """Manually add a violation to the daily report"""
        self.record_violation(violation_type, user.id, ctx.author.id, reason)
        await ctx.send(f"✅ Added {violation_type} violation for {user.mention}")

async def setup(bot):
    await bot.add_cog(DailySecurityReport(bot))
