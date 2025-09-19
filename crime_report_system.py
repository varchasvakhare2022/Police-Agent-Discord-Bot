import discord
from discord.ext import commands, tasks
import asyncio
from datetime import datetime, timedelta
import json
import os

class CrimeReportSystem:
    def __init__(self, bot):
        self.bot = bot
        self.daily_stats = {
            'warnings_issued': 0,
            'bans': 0,
            'raids_blocked': 0,
            'scam_messages_deleted': 0
        }
        self.stats_file = 'daily_crime_stats.json'
        self.load_stats()
        
    def load_stats(self):
        """Load daily statistics from file"""
        if os.path.exists(self.stats_file):
            try:
                with open(self.stats_file, 'r') as f:
                    self.daily_stats = json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                self.reset_daily_stats()
        else:
            self.reset_daily_stats()
    
    def save_stats(self):
        """Save daily statistics to file"""
        with open(self.stats_file, 'w') as f:
            self.daily_stats = self.daily_stats.copy()
            self.daily_stats = self.daily_stats.copy()
    
    def reset_daily_stats(self):
        """Reset daily statistics"""
        self.daily_stats = {
            'warnings_issued': 0,
            'bans': 0,
            'raids_blocked': 0,
            'scam_messages_deleted': 0
        }
        self.save_stats()
    
    def increment_warnings(self):
        """Increment warning count"""
        self.daily_stats['warnings_issued'] += 1
        self.save_stats()
    
    def increment_bans(self):
        """Increment ban count"""
        self.daily_stats['bans'] += 1
        self.save_stats()
    
    def increment_raids_blocked(self):
        """Increment raid blocked count"""
        self.daily_stats['raids_blocked'] += 1
        self.save_stats()
    
    def increment_scam_deleted(self):
        """Increment scam messages deleted count"""
        self.daily_stats['scam_messages_deleted'] += 1
        self.save_stats()
    
    def generate_daily_report(self):
        """Generate daily crime report embed"""
        embed = discord.Embed(
            title="🚔 Daily Crime Report",
            color=0xff0000,
            timestamp=datetime.now()
        )
        
        embed.add_field(
            name="📊 Statistics",
            value=f"**Warnings Issued:** {self.daily_stats['warnings_issued']}\n"
                  f"**Bans:** {self.daily_stats['bans']}\n"
                  f"**Raids Blocked:** {self.daily_stats['raids_blocked']}\n"
                  f"**Scam Messages Auto-Deleted:** {self.daily_stats['scam_messages_deleted']}",
            inline=False
        )
        
        embed.set_footer(text=f"Report generated at {datetime.now().strftime('%H:%M:%S')}")
        return embed
    
    async def send_daily_report(self, channel_id):
        """Send daily report to specified channel"""
        channel = self.bot.get_channel(channel_id)
        if channel:
            embed = self.generate_daily_report()
            await channel.send(embed=embed)
            self.reset_daily_stats()  # Reset after sending report
    
    @tasks.loop(hours=24)
    async def daily_report_task(self):
        """Task to send daily reports every 24 hours"""
        # You can set your report channel ID here
        report_channel_id = 123456789012345678  # Replace with your channel ID
        await self.send_daily_report(report_channel_id)
    
    def start_daily_reports(self):
        """Start the daily report task"""
        self.daily_report_task.start()

class CrimeReportCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.crime_system = CrimeReportSystem(bot)
    
    @commands.command(name='crime_report')
    async def manual_crime_report(self, ctx):
        """Manually generate crime report"""
        embed = self.crime_system.generate_daily_report()
        await ctx.send(embed=embed)
    
    @commands.command(name='add_warning')
    async def add_warning(self, ctx):
        """Add a warning to daily stats"""
        self.crime_system.increment_warnings()
        await ctx.send("✅ Warning added to daily statistics")
    
    @commands.command(name='add_ban')
    async def add_ban(self, ctx):
        """Add a ban to daily stats"""
        self.crime_system.increment_bans()
        await ctx.send("✅ Ban added to daily statistics")
    
    @commands.command(name='add_raid_blocked')
    async def add_raid_blocked(self, ctx):
        """Add a blocked raid to daily stats"""
        self.crime_system.increment_raids_blocked()
        await ctx.send("✅ Raid blocked added to daily statistics")
    
    @commands.command(name='add_scam_deleted')
    async def add_scam_deleted(self, ctx):
        """Add scam message deletion to daily stats"""
        self.crime_system.increment_scam_deleted()
        await ctx.send("✅ Scam message deletion added to daily statistics")
    
    @commands.command(name='crime_report')
    async def reset_daily_stats(self):
        """Reset daily statistics"""
        await ctx.send("✅ Daily statistics reset")
    
    @commands.command(name='start_daily_reports')
    async def start_daily_reports(self):
        """Start daily report task"""
        self.crime_system.start_daily_reports()
        await ctx.send("✅ Daily reports started")

async def setup(bot):
    await bot.add_cog(CrimeReportCog(bot))
