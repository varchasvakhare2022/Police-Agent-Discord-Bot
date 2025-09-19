import discord
from discord.ext import commands, tasks
import asyncio
import random
from datetime import datetime, timedelta

class ServerPatrols:
    def __init__(self, bot):
        self.bot = bot
        self.active_channels = set()
        self.last_activity = {}
        self.patrol_messages = [
            "🚓 Police patrols are active. Stay out of trouble.",
            "🚔 Officers are patrolling the area. Behave yourselves!",
            "👮‍♂️ Police presence detected. Keep it clean!",
            "🚓 Patrol units are monitoring. Stay safe!",
            "🚔 Law enforcement is active. No funny business!"
        ]
        self.activity_threshold = 5  # Messages in last 5 minutes
        self.patrol_cooldown = 300  # 5 minutes between patrols
    
    def is_channel_active(self, channel_id):
        """Check if channel has recent activity"""
        if channel_id not in self.last_activity:
            return False
        
        time_since_activity = datetime.now() - self.last_activity[channel_id]
        return time_since_activity.total_seconds() < 300  # 5 minutes
    
    def record_activity(self, channel_id):
        """Record channel activity"""
        self.last_activity[channel_id] = datetime.now()
    
    async def send_patrol_message(self, channel):
        """Send patrol message to active channel"""
        if not self.is_channel_active(channel.id):
            return False
        
        message = random.choice(self.patrol_messages)
        await channel.send(message)
        return True
    
    @tasks.loop(minutes=10)
    async def patrol_task(self):
        """Main patrol task - runs every 10 minutes"""
        active_channels = [
            ch for ch in self.bot.get_all_channels() 
            if isinstance(ch, discord.TextChannel) and self.is_channel_active(ch.id)
        ]
        
        if active_channels:
            # Pick random active channel
            target_channel = random.choice(active_channels)
            await self.send_patrol_message(target_channel)
    
    def start_patrols(self):
        """Start patrol system"""
        self.patrol_task.start()

class PatrolCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.patrol_system = ServerPatrols(bot)
    
    @commands.Cog.listener()
    async def on_message(self, message):
        """Track channel activity"""
        if not message.author.bot and isinstance(message.channel, discord.TextChannel):
            self.patrol_system.record_activity(message.channel.id)
    
    @commands.command(name='patrol_status')
    @commands.has_permissions(manage_messages=True)
    async def patrol_status(self, ctx):
        """Check patrol system status"""
        active_channels = len([
            ch for ch in ctx.guild.text_channels 
            if self.patrol_system.is_channel_active(ch.id)
        ])
        
        await ctx.send(f"🚓 Patrol System Status:\n"
                      f"Active channels: {active_channels}\n"
                      f"Next patrol in: {self.patrol_system.patrol_cooldown} seconds")
    
    @commands.command(name='force_patrol')
    @commands.has_permissions(manage_messages=True)
    async def force_patrol(self, ctx):
        """Force a patrol message"""
        success = await self.patrol_system.send_patrol_message(ctx.channel)
        if success:
            await ctx.send("✅ Patrol message sent to active channel")
        await ctx.send("Patrol message sent to active channel")

async def setup(bot):
    await bot.add_cog(PatrolCog(bot))
