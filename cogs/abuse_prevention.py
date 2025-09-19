import discord
from discord.ext import commands
import time
from collections import defaultdict
import inspect

class AbusePrevention(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.user_cooldowns = defaultdict(dict)
        self.command_usage = defaultdict(list)
        self.mass_action_tracker = defaultdict(list)

    def check_cooldown(self, user_id: int, command_name: str, cooldown_seconds: int) -> bool:
        """Check if user is on cooldown for a command"""
        current_time = time.time()
        
        if command_name in self.user_cooldowns[user_id]:
            last_used = self.user_cooldowns[user_id][command_name]
            if current_time - last_used < cooldown_seconds:
                return False
        
        self.user_cooldowns[user_id][command_name] = current_time
        return True

    def check_rate_limit(self, user_id: int, command_name: str, max_uses: int, time_window: int) -> bool:
        """Check if user is rate limited for a command"""
        current_time = time.time()
        
        # Clean old entries
        self.command_usage[user_id] = [
            (cmd, timestamp) for cmd, timestamp in self.command_usage[user_id]
            if current_time - timestamp < time_window
        ]
        
        # Count recent uses
        recent_uses = sum(1 for cmd, _ in self.command_usage[user_id] if cmd == command_name)
        
        if recent_uses >= max_uses:
            return False
        
        # Add current use
        self.command_usage[user_id].append((command_name, current_time))
        return True

    def check_mass_action(self, user_id: int, action_type: str, max_actions: int, time_window: int) -> bool:
        """Check for mass actions (e.g., mass kick/ban)"""
        current_time = time.time()
        
        # Clean old entries
        self.mass_action_tracker[user_id] = [
            (action, timestamp) for action, timestamp in self.mass_action_tracker[user_id]
            if current_time - timestamp < time_window
        ]
        
        # Count recent actions
        recent_actions = sum(1 for action, _ in self.mass_action_tracker[user_id] if action == action_type)
        
        if recent_actions >= max_actions:
            return False
        
        # Add current action
        self.mass_action_tracker[user_id].append((action_type, current_time))
        return True

    @commands.Cog.listener()
    async def on_command(self, ctx):
        """Apply cooldowns and rate limiting to commands"""
        
        # Define cooldowns for different command types
        cooldowns = {
            'kick': 5,      # 5 seconds
            'ban': 10,      # 10 seconds
            'timeout': 3,   # 3 seconds
            'unban': 5,     # 5 seconds
            'blacklist': 30, # 30 seconds
            'antispam': 10,  # 10 seconds
        }
        
        # Define rate limits (max uses per minute)
        rate_limits = {
            'kick': 5,      # Max 5 kicks per minute
            'ban': 3,       # Max 3 bans per minute
            'timeout': 10,  # Max 10 timeouts per minute
            'unban': 5,     # Max 5 unbans per minute
        }
        
        command_name = ctx.command.name
        user_id = ctx.author.id
        
        # Check cooldown
        if command_name in cooldowns:
            if not self.check_cooldown(user_id, command_name, cooldowns[command_name]):
                remaining = cooldowns[command_name] - (time.time() - self.user_cooldowns[user_id][command_name])
                await ctx.reply(f"⏰ You're on cooldown! Please wait {remaining:.1f} seconds before using this command again.", delete_after=5)
                return
        
        # Check rate limit
        if command_name in rate_limits:
            if not self.check_rate_limit(user_id, command_name, rate_limits[command_name], 60):
                await ctx.reply(f"🚫 Rate limit exceeded! You can only use `{command_name}` {rate_limits[command_name]} times per minute.", delete_after=5)
                return
        
        # Check for mass actions
        if command_name in ['kick', 'ban']:
            if not self.check_mass_action(user_id, command_name, 3, 300):  # Max 3 kicks/bans per 5 minutes
                await ctx.reply(f"🚫 Mass {command_name} detected! Please slow down. You can only {command_name} 3 users per 5 minutes.", delete_after=10)
                return

    @commands.command(name="cooldowns")
    @commands.has_permissions(administrator=True)
    async def show_cooldowns(self, ctx: commands.Context, member: discord.Member = None):
        """Show cooldown information for a user"""
        
        if not member:
            member = ctx.author
        
        user_id = member.id
        current_time = time.time()
        
        embed = discord.Embed(
            title=f"⏰ Cooldowns for {member.display_name}",
            color=0x9C84EF
        )
        
        cooldowns = {
            'kick': 5,
            'ban': 10,
            'timeout': 3,
            'unban': 5,
            'blacklist': 30,
            'antispam': 10,
        }
        
        cooldown_info = []
        for command, cooldown_time in cooldowns.items():
            if command in self.user_cooldowns[user_id]:
                last_used = self.user_cooldowns[user_id][command]
                remaining = cooldown_time - (current_time - last_used)
                
                if remaining > 0:
                    cooldown_info.append(f"`{command}`: {remaining:.1f}s remaining")
                else:
                    cooldown_info.append(f"`{command}`: ✅ Ready")
            else:
                cooldown_info.append(f"`{command}`: ✅ Ready")
        
        embed.add_field(
            name="Command Cooldowns",
            value="\n".join(cooldown_info),
            inline=False
        )
        
        # Show rate limit info
        rate_limit_info = []
        rate_limits = {
            'kick': 5,
            'ban': 3,
            'timeout': 10,
            'unban': 5,
        }
        
        for command, max_uses in rate_limits.items():
            recent_uses = sum(1 for cmd, _ in self.command_usage[user_id] if cmd == command)
            rate_limit_info.append(f"`{command}`: {recent_uses}/{max_uses} uses (per minute)")
        
        embed.add_field(
            name="Rate Limits",
            value="\n".join(rate_limit_info),
            inline=False
        )
        
        await ctx.send(embed=embed)

    @commands.command(name="reset-cooldowns")
    @commands.has_permissions(administrator=True)
    async def reset_cooldowns(self, ctx: commands.Context, member: discord.Member):
        """Reset cooldowns for a user"""
        
        user_id = member.id
        
        # Reset cooldowns
        if user_id in self.user_cooldowns:
            del self.user_cooldowns[user_id]
        
        # Reset rate limits
        if user_id in self.command_usage:
            del self.command_usage[user_id]
        
        # Reset mass action tracker
        if user_id in self.mass_action_tracker:
            del self.mass_action_tracker[user_id]
        
        embed = discord.Embed(
            title="✅ Cooldowns Reset",
            description=f"All cooldowns and rate limits have been reset for {member.mention}",
            color=0x00ff00
        )
        
        await ctx.send(embed=embed)

    @commands.command(name="abuse-stats")
    @commands.has_permissions(administrator=True)
    async def abuse_stats(self, ctx: commands.Context):
        """Show abuse prevention statistics"""
        
        embed = discord.Embed(
            title="🛡️ Abuse Prevention Statistics",
            color=0x9C84EF
        )
        
        # Count users with active cooldowns
        active_cooldowns = sum(1 for user_cooldowns in self.user_cooldowns.values() if user_cooldowns)
        
        # Count users with rate limits
        active_rate_limits = sum(1 for user_usage in self.command_usage.values() if user_usage)
        
        # Count users with mass action tracking
        active_mass_tracking = sum(1 for user_actions in self.mass_action_tracker.values() if user_actions)
        
        embed.add_field(
            name="Active Protections",
            value=inspect.cleandoc(
                f"""
                **Users with Cooldowns:** {active_cooldowns}
                **Users with Rate Limits:** {active_rate_limits}
                **Users with Mass Action Tracking:** {active_mass_tracking}
                """
            ),
            inline=True
        )
        
        # Show protection settings
        embed.add_field(
            name="Protection Settings",
            value=inspect.cleandoc(
                """
                **Kick Cooldown:** 5 seconds
                **Ban Cooldown:** 10 seconds
                **Timeout Cooldown:** 3 seconds
                **Mass Action Limit:** 3 per 5 minutes
                """
            ),
            inline=True
        )
        
        embed.add_field(
            name="Rate Limits (per minute)",
            value=inspect.cleandoc(
                """
                **Kicks:** 5
                **Bans:** 3
                **Timeouts:** 10
                **Unbans:** 5
                """
            ),
            inline=True
        )
        
        await ctx.send(embed=embed)

    @commands.command(name="emergency-stop")
    @commands.is_owner()
    async def emergency_stop(self, ctx: commands.Context):
        """Emergency stop all abuse prevention (owner only)"""
        
        # Clear all tracking data
        self.user_cooldowns.clear()
        self.command_usage.clear()
        self.mass_action_tracker.clear()
        
        embed = discord.Embed(
            title="🚨 Emergency Stop Activated",
            description="All abuse prevention measures have been disabled!",
            color=0xff0000
        )
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(AbusePrevention(bot))
