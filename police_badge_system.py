import discord
from discord.ext import commands
import random

class PoliceBadgeSystem:
    def __init__(self, bot):
        self.bot = bot
        self.command_count = 0
        self.siren_messages = [
            "🚨 YOU'RE UNDER ARREST… just kidding.",
            "Police badge system: Mods can issue 'Good Citizen' badges for helpful members."
        ]
    
    def increment_command_count(self):
        """Increment command count"""
        self.command_count += 1
        return self.command_count
    
    def check_siren_easter_egg(self):
        """Check if siren easter egg should trigger every 100th command"""
        if self.command_count % 100 == 0:
            return True
        return False
    
    async def send_siren_message(self, ctx):
        """Send siren easter egg message"""
        if self.check_siren_easter_egg():
            message = random.choice(self.siren_messages)
            await ctx.send(message)
    
    @commands.command(name='test_siren')
    async def test_siren(self, ctx):
        """Test siren easter egg system"""
        await self.send_siren_message(ctx)

async def setup(bot):
    await bot.add_cog(PoliceBadgeSystem(bot))
