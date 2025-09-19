import discord
from discord.ext import commands
import json
import os
from datetime import datetime, timedelta
import asyncio
import random

class ModeratorDutyMode(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.duty_data_file = 'data/duty_data.json'
        self.duty_config_file = 'data/duty_config.json'
        self.report_queue_file = 'data/report_queue.json'
        
        # Ensure data directory exists
        os.makedirs('data', exist_ok=True)
        
        # Load data
        self.load_data()
    
    def load_data(self):
        """Load duty data, configuration, and report queue from JSON files"""
        # Load duty data
        if os.path.exists(self.duty_data_file):
            try:
                with open(self.duty_data_file, 'r') as f:
                    self.duty_data = json.load(f)
            except:
                self.duty_data = {}
        else:
            self.duty_data = {}
        
        # Load duty configuration
        if os.path.exists(self.duty_config_file):
            try:
                with open(self.duty_config_file, 'r') as f:
                    self.duty_config = json.load(f)
            except:
                self.duty_config = {
                    'enabled': True,
                    'auto_assign': True,
                    'max_reports_per_mod': 5,
                    'duty_channel_id': None,
                    'report_channel_id': None,
                    'workload_balancing': True,
                    'duty_rotation': False,
                    'rotation_interval': 4  # hours
                }
        else:
            self.duty_config = {
                'enabled': True,
                'auto_assign': True,
                'max_reports_per_mod': 5,
                'duty_channel_id': None,
                'report_channel_id': None,
                'workload_balancing': True,
                'duty_rotation': False,
                'rotation_interval': 4
            }
        
        # Load report queue
        if os.path.exists(self.report_queue_file):
            try:
                with open(self.report_queue_file, 'r') as f:
                    self.report_queue = json.load(f)
            except:
                self.report_queue = []
        else:
            self.report_queue = []
        
        self.save_data()
    
    def save_data(self):
        """Save duty data, configuration, and report queue to JSON files"""
        with open(self.duty_data_file, 'w') as f:
            json.dump(self.duty_data, f, indent=2)
        
        with open(self.duty_config_file, 'w') as f:
            json.dump(self.duty_config, f, indent=2)
        
        with open(self.report_queue_file, 'w') as f:
            json.dump(self.report_queue, f, indent=2)
    
    def get_moderator_data(self, user_id):
        """Get or create moderator data"""
        user_id = str(user_id)
        if user_id not in self.duty_data:
            self.duty_data[user_id] = {
                'is_on_duty': False,
                'duty_start': None,
                'duty_end': None,
                'total_duty_time': 0,
                'reports_assigned': 0,
                'reports_resolved': 0,
                'current_reports': [],
                'last_activity': None,
                'duty_sessions': []
            }
        return self.duty_data[user_id]
    
    def get_active_moderators(self, guild_id):
        """Get list of active moderators in a guild"""
        active_mods = []
        
        for user_id, data in self.duty_data.items():
            if data['is_on_duty']:
                try:
                    user = self.bot.get_user(int(user_id))
                    if user:
                        guild = self.bot.get_guild(guild_id)
                        if guild and guild.get_member(user.id):
                            # Check if user has moderation permissions
                            member = guild.get_member(user.id)
                            if member.guild_permissions.manage_messages:
                                active_mods.append(user_id)
                except:
                    continue
        
        return active_mods
    
    def assign_report_to_moderator(self, report_data, guild_id):
        """Assign a report to an active moderator"""
        active_mods = self.get_active_moderators(guild_id)
        
        if not active_mods:
            return None
        
        # Find moderator with least reports
        if self.duty_config['workload_balancing']:
            mod_reports = {}
            for mod_id in active_mods:
                mod_data = self.get_moderator_data(mod_id)
                mod_reports[mod_id] = len(mod_data['current_reports'])
            
            # Sort by report count
            sorted_mods = sorted(mod_reports.items(), key=lambda x: x[1])
            assigned_mod = sorted_mods[0][0]
        else:
            # Random assignment
            assigned_mod = random.choice(active_mods)
        
        # Check if moderator can take more reports
        mod_data = self.get_moderator_data(assigned_mod)
        if len(mod_data['current_reports']) >= self.duty_config['max_reports_per_mod']:
            return None
        
        # Assign report
        report_data['assigned_moderator'] = assigned_mod
        report_data['assigned_at'] = datetime.now().isoformat()
        
        mod_data['current_reports'].append(report_data['report_id'])
        mod_data['reports_assigned'] += 1
        
        self.save_data()
        return assigned_mod
    
    def add_report_to_queue(self, report_type, user_id, reason, guild_id, details=None):
        """Add a report to the queue"""
        report_id = f"RPT_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{user_id}"
        
        report_data = {
            'report_id': report_id,
            'report_type': report_type,
            'user_id': str(user_id),
            'reason': reason,
            'guild_id': str(guild_id),
            'details': details or {},
            'created_at': datetime.now().isoformat(),
            'status': 'pending',
            'assigned_moderator': None,
            'assigned_at': None,
            'resolved_at': None,
            'resolved_by': None
        }
        
        self.report_queue.append(report_data)
        
        # Try to assign to active moderator
        if self.duty_config['auto_assign']:
            assigned_mod = self.assign_report_to_moderator(report_data, guild_id)
            if assigned_mod:
                asyncio.create_task(self.notify_assigned_moderator(assigned_mod, report_data))
        
        self.save_data()
        return report_id
    
    async def notify_assigned_moderator(self, moderator_id, report_data):
        """Notify moderator about assigned report"""
        try:
            moderator = self.bot.get_user(int(moderator_id))
            if moderator:
                embed = discord.Embed(
                    title="🚨 New Report Assigned",
                    color=0xff0000,
                    timestamp=datetime.now()
                )
                
                embed.add_field(
                    name="📋 Report ID",
                    value=f"`{report_data['report_id']}`",
                    inline=True
                )
                
                embed.add_field(
                    name="⚠️ Type",
                    value=report_data['report_type'].title(),
                    inline=True
                )
                
                embed.add_field(
                    name="👤 User",
                    value=f"<@{report_data['user_id']}>",
                    inline=True
                )
                
                embed.add_field(
                    name="📝 Reason",
                    value=report_data['reason'],
                    inline=False
                )
                
                embed.set_footer(text="You are on duty - please handle this report")
                
                await moderator.send(embed=embed)
        except Exception as e:
            print(f"Error notifying moderator: {e}")
    
    @commands.command(name='duty on')
    @commands.has_permissions(manage_messages=True)
    async def duty_on_command(self, ctx):
        """Go on duty as a moderator"""
        mod_data = self.get_moderator_data(ctx.author.id)
        
        if mod_data['is_on_duty']:
            await ctx.send("❌ You are already on duty!")
            return
        
        mod_data['is_on_duty'] = True
        mod_data['duty_start'] = datetime.now().isoformat()
        mod_data['last_activity'] = datetime.now().isoformat()
        
        # Add to duty sessions
        mod_data['duty_sessions'].append({
            'start': datetime.now().isoformat(),
            'end': None,
            'duration': 0
        })
        
        self.save_data()
        
        embed = discord.Embed(
            title="👮‍♂️ Moderator On Duty",
            color=0x00ff00,
            timestamp=datetime.now()
        )
        
        embed.add_field(name="👤 Moderator", value=ctx.author.mention, inline=True)
        embed.add_field(name="⏰ Started", value=datetime.now().strftime('%H:%M:%S'), inline=True)
        embed.add_field(name="📊 Status", value="On Duty", inline=True)
        
        # Show current workload
        active_mods = self.get_active_moderators(ctx.guild.id)
        embed.add_field(
            name="👥 Active Moderators",
            value=str(len(active_mods)),
            inline=True
        )
        
        embed.add_field(
            name="📋 Pending Reports",
            value=str(len([r for r in self.report_queue if r['status'] == 'pending'])),
            inline=True
        )
        
        await ctx.send(embed=embed)
        
        # Notify duty channel if configured
        if self.duty_config['duty_channel_id']:
            try:
                channel = self.bot.get_channel(self.duty_config['duty_channel_id'])
                if channel:
                    await channel.send(f"👮‍♂️ {ctx.author.mention} is now on duty!")
            except:
                pass
    
    @commands.command(name='duty off')
    @commands.has_permissions(manage_messages=True)
    async def duty_off_command(self, ctx):
        """Go off duty as a moderator"""
        mod_data = self.get_moderator_data(ctx.author.id)
        
        if not mod_data['is_on_duty']:
            await ctx.send("❌ You are not on duty!")
            return
        
        # Calculate duty time
        duty_start = datetime.fromisoformat(mod_data['duty_start'])
        duty_duration = datetime.now() - duty_start
        
        mod_data['is_on_duty'] = False
        mod_data['duty_end'] = datetime.now().isoformat()
        mod_data['total_duty_time'] += duty_duration.total_seconds()
        
        # Update current duty session
        if mod_data['duty_sessions']:
            mod_data['duty_sessions'][-1]['end'] = datetime.now().isoformat()
            mod_data['duty_sessions'][-1]['duration'] = duty_duration.total_seconds()
        
        # Reassign current reports
        for report_id in mod_data['current_reports']:
            report = next((r for r in self.report_queue if r['report_id'] == report_id), None)
            if report and report['status'] == 'pending':
                report['assigned_moderator'] = None
                report['assigned_at'] = None
                
                # Try to reassign
                assigned_mod = self.assign_report_to_moderator(report, ctx.guild.id)
                if assigned_mod:
                    asyncio.create_task(self.notify_assigned_moderator(assigned_mod, report))
        
        mod_data['current_reports'] = []
        
        self.save_data()
        
        embed = discord.Embed(
            title="👮‍♂️ Moderator Off Duty",
            color=0xff8800,
            timestamp=datetime.now()
        )
        
        embed.add_field(name="👤 Moderator", value=ctx.author.mention, inline=True)
        embed.add_field(name="⏰ Duration", value=f"{duty_duration.total_seconds()/3600:.1f} hours", inline=True)
        embed.add_field(name="📊 Status", value="Off Duty", inline=True)
        
        embed.add_field(
            name="📋 Reports Handled",
            value=str(mod_data['reports_assigned']),
            inline=True
        )
        
        embed.add_field(
            name="✅ Reports Resolved",
            value=str(mod_data['reports_resolved']),
            inline=True
        )
        
        await ctx.send(embed=embed)
        
        # Notify duty channel if configured
        if self.duty_config['duty_channel_id']:
            try:
                channel = self.bot.get_channel(self.duty_config['duty_channel_id'])
                if channel:
                    await channel.send(f"👮‍♂️ {ctx.author.mention} is now off duty!")
            except:
                pass
    
    @commands.command(name='duty status')
    async def duty_status_command(self, ctx, member: discord.Member = None):
        """Check duty status for a moderator"""
        member = member or ctx.author
        
        if not member.guild_permissions.manage_messages:
            await ctx.send("❌ This user is not a moderator.")
            return
        
        mod_data = self.get_moderator_data(member.id)
        
        embed = discord.Embed(
            title=f"👮‍♂️ Duty Status: {member.display_name}",
            color=0x00ff00 if mod_data['is_on_duty'] else 0xff8800,
            timestamp=datetime.now()
        )
        
        embed.add_field(
            name="📊 Status",
            value="On Duty" if mod_data['is_on_duty'] else "Off Duty",
            inline=True
        )
        
        if mod_data['is_on_duty']:
            duty_start = datetime.fromisoformat(mod_data['duty_start'])
            duty_duration = datetime.now() - duty_start
            embed.add_field(
                name="⏰ Current Session",
                value=f"{duty_duration.total_seconds()/3600:.1f} hours",
                inline=True
            )
        
        embed.add_field(
            name="📋 Current Reports",
            value=str(len(mod_data['current_reports'])),
            inline=True
        )
        
        embed.add_field(
            name="📊 Total Reports",
            value=f"Assigned: {mod_data['reports_assigned']}\nResolved: {mod_data['reports_resolved']}",
            inline=True
        )
        
        embed.add_field(
            name="⏰ Total Duty Time",
            value=f"{mod_data['total_duty_time']/3600:.1f} hours",
            inline=True
        )
        
        if mod_data['last_activity']:
            embed.add_field(
                name="🕐 Last Activity",
                value=datetime.fromisoformat(mod_data['last_activity']).strftime('%Y-%m-%d %H:%M'),
                inline=True
            )
        
        await ctx.send(embed=embed)
    
    @commands.command(name='duty roster')
    async def duty_roster_command(self, ctx):
        """Show all moderators and their duty status"""
        moderators = []
        
        for member in ctx.guild.members:
            if member.guild_permissions.manage_messages and not member.bot:
                mod_data = self.get_moderator_data(member.id)
                moderators.append((member, mod_data))
        
        if not moderators:
            await ctx.send("No moderators found.")
            return
        
        embed = discord.Embed(
            title="👮‍♂️ Moderator Duty Roster",
            color=0x0099ff,
            timestamp=datetime.now()
        )
        
        on_duty = []
        off_duty = []
        
        for member, mod_data in moderators:
            if mod_data['is_on_duty']:
                on_duty.append((member, mod_data))
            else:
                off_duty.append((member, mod_data))
        
        # Show on duty moderators
        if on_duty:
            duty_text = ""
            for member, mod_data in on_duty:
                duty_start = datetime.fromisoformat(mod_data['duty_start'])
                duty_duration = datetime.now() - duty_start
                duty_text += f"**{member.display_name}** - {duty_duration.total_seconds()/3600:.1f}h\n"
            
            embed.add_field(
                name="🟢 On Duty",
                value=duty_text,
                inline=True
            )
        
        # Show off duty moderators
        if off_duty:
            off_text = ""
            for member, mod_data in off_duty:
                off_text += f"**{member.display_name}** - {mod_data['total_duty_time']/3600:.1f}h total\n"
            
            embed.add_field(
                name="🔴 Off Duty",
                value=off_text,
                inline=True
            )
        
        # Show report queue
        pending_reports = len([r for r in self.report_queue if r['status'] == 'pending'])
        embed.add_field(
            name="📋 Report Queue",
            value=f"Pending: {pending_reports}",
            inline=True
        )
        
        await ctx.send(embed=embed)
    
    @commands.command(name='report queue')
    @commands.has_permissions(manage_messages=True)
    async def report_queue_command(self, ctx):
        """View the report queue"""
        pending_reports = [r for r in self.report_queue if r['status'] == 'pending']
        
        if not pending_reports:
            await ctx.send("No pending reports in the queue.")
            return
        
        embed = discord.Embed(
            title="📋 Report Queue",
            color=0xff0000,
            timestamp=datetime.now()
        )
        
        for i, report in enumerate(pending_reports[-10:], 1):  # Show last 10
            assigned_mod = "Unassigned"
            if report['assigned_moderator']:
                try:
                    mod = self.bot.get_user(int(report['assigned_moderator']))
                    assigned_mod = mod.display_name if mod else "Unknown"
                except:
                    assigned_mod = "Unknown"
            
            embed.add_field(
                name=f"Report #{i}",
                value=f"**ID:** `{report['report_id']}`\n"
                      f"**Type:** {report['report_type']}\n"
                      f"**User:** <@{report['user_id']}>\n"
                      f"**Assigned:** {assigned_mod}\n"
                      f"**Created:** {datetime.fromisoformat(report['created_at']).strftime('%H:%M')}",
                inline=True
            )
        
        embed.set_footer(text=f"Showing {len(pending_reports)} pending reports")
        await ctx.send(embed=embed)
    
    @commands.command(name='resolve report')
    @commands.has_permissions(manage_messages=True)
    async def resolve_report_command(self, ctx, report_id: str):
        """Resolve a report"""
        report = next((r for r in self.report_queue if r['report_id'] == report_id), None)
        
        if not report:
            await ctx.send(f"❌ Report `{report_id}` not found.")
            return
        
        if report['status'] != 'pending':
            await ctx.send(f"❌ Report `{report_id}` is already resolved.")
            return
        
        # Update report
        report['status'] = 'resolved'
        report['resolved_at'] = datetime.now().isoformat()
        report['resolved_by'] = str(ctx.author.id)
        
        # Update moderator data
        if report['assigned_moderator']:
            mod_data = self.get_moderator_data(report['assigned_moderator'])
            if report_id in mod_data['current_reports']:
                mod_data['current_reports'].remove(report_id)
            mod_data['reports_resolved'] += 1
        
        self.save_data()
        
        embed = discord.Embed(
            title="✅ Report Resolved",
            color=0x00ff00,
            timestamp=datetime.now()
        )
        
        embed.add_field(name="📋 Report ID", value=f"`{report_id}`", inline=True)
        embed.add_field(name="👮‍♂️ Resolved by", value=ctx.author.mention, inline=True)
        embed.add_field(name="⏰ Resolved at", value=datetime.now().strftime('%H:%M:%S'), inline=True)
        
        await ctx.send(embed=embed)
    
    @commands.command(name='duty config')
    @commands.has_permissions(administrator=True)
    async def duty_config_command(self, ctx, setting: str, *, value: str):
        """Configure duty mode settings (admin only)"""
        if setting.lower() == 'enabled':
            self.duty_config['enabled'] = value.lower() in ['true', 'yes', '1', 'on']
            await ctx.send(f"✅ Duty mode enabled: {self.duty_config['enabled']}")
        
        elif setting.lower() == 'auto_assign':
            self.duty_config['auto_assign'] = value.lower() in ['true', 'yes', '1', 'on']
            await ctx.send(f"✅ Auto-assign reports: {self.duty_config['auto_assign']}")
        
        elif setting.lower() == 'max_reports':
            try:
                max_reports = int(value)
                if 1 <= max_reports <= 20:
                    self.duty_config['max_reports_per_mod'] = max_reports
                    await ctx.send(f"✅ Max reports per mod: {max_reports}")
                else:
                    await ctx.send("❌ Invalid value. Use 1-20.")
            except ValueError:
                await ctx.send("❌ Invalid number.")
        
        elif setting.lower() == 'duty_channel':
            try:
                channel_id = int(value)
                channel = self.bot.get_channel(channel_id)
                if channel:
                    self.duty_config['duty_channel_id'] = channel_id
                    await ctx.send(f"✅ Duty channel set to: {channel.mention}")
                else:
                    await ctx.send("❌ Channel not found.")
            except ValueError:
                await ctx.send("❌ Invalid channel ID.")
        
        elif setting.lower() == 'report_channel':
            try:
                channel_id = int(value)
                channel = self.bot.get_channel(channel_id)
                if channel:
                    self.duty_config['report_channel_id'] = channel_id
                    await ctx.send(f"✅ Report channel set to: {channel.mention}")
                else:
                    await ctx.send("❌ Channel not found.")
            except ValueError:
                await ctx.send("❌ Invalid channel ID.")
        
        elif setting.lower() == 'workload_balancing':
            self.duty_config['workload_balancing'] = value.lower() in ['true', 'yes', '1', 'on']
            await ctx.send(f"✅ Workload balancing: {self.duty_config['workload_balancing']}")
        
        else:
            await ctx.send("❌ Invalid setting. Available: enabled, auto_assign, max_reports, duty_channel, report_channel, workload_balancing")
        
        self.save_data()

async def setup(bot):
    await bot.add_cog(ModeratorDutyMode(bot))
