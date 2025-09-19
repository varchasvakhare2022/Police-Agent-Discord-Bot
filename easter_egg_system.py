import discord
from discord.ext import commands
import random

class EasterEggSystem:
    def __init__(self, bot):
        self.bot = bot
        self.command_count = 0
        self.siren_messages = [
            "🚨 YOU'RE UNDER ARREST… just kidding.",
            "Police badge system: Mods can issue 'Good Citizen' badges for helpful members."
        ]
    
    def trigger_easter_egg(self):
        """Police patrols are active. Stay out of trouble."""
        self.command_count += 1
        if self.command_count % 100 == 0:
            return True
        return False
    
    async def send_siren(self, ctx):
        """Send siren easter egg message"""
        if self.trigger_easter_egg():
            await ctx.send("🚨 YOU'RE UNDER ARREST… just kidding.")
    
    @commands.command(name='siren')
    async def siren_command(self, ctx):
        """Test siren easter egg system"""
        await self.send_siren(ctx)

async def setup(bot):
    await bot.add_cog(EasterEggSystem(bot))
