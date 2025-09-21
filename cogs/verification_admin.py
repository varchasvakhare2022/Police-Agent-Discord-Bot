import discord
from discord.ext import commands
import json
import os
from datetime import datetime

class VerificationAdmin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.captcha_data_file = 'data/captcha_data.json'
        self.cooldown_data_file = 'data/verification_cooldown.json'
    
    def load_captcha_data(self):
        """Load captcha data from JSON file"""
        try:
            if os.path.exists(self.captcha_data_file):
                with open(self.captcha_data_file, 'r') as f:
                    return json.load(f)
            return {}
        except (json.JSONDecodeError, FileNotFoundError):
            return {}
    
    def save_captcha_data(self, data):
        """Save captcha data to JSON file"""
        os.makedirs('data', exist_ok=True)
        with open(self.captcha_data_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def load_cooldown_data(self):
        """Load cooldown data from JSON file"""
        try:
            if os.path.exists(self.cooldown_data_file):
                with open(self.cooldown_data_file, 'r') as f:
                    return json.load(f)
            return {}
        except (json.JSONDecodeError, FileNotFoundError):
            return {}
    
    def save_cooldown_data(self, data):
        """Save cooldown data to JSON file"""
        os.makedirs('data', exist_ok=True)
        with open(self.cooldown_data_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    @commands.command(name="verification_status")
    @commands.has_permissions(administrator=True)
    async def verification_status(self, ctx, user: discord.Member = None):
        """Check verification status of a user"""
        if user is None:
            user = ctx.author
        
        # Check if user is verified
        verified_role = ctx.guild.get_role(903238068910309398)
        is_verified = verified_role and verified_role in user.roles
        
        # Check captcha data
        captcha_data = self.load_captcha_data()
        user_captcha = captcha_data.get(str(user.id), {})
        
        # Check cooldown data
        cooldown_data = self.load_cooldown_data()
        user_cooldown = cooldown_data.get(str(user.id), {})
        
        embed = discord.Embed(
            title=f"Verification Status - {user.display_name}",
            color=0x00ff00 if is_verified else 0xff0000
        )
        
        embed.add_field(
            name="Verified Status",
            value="✅ Verified" if is_verified else "❌ Not Verified",
            inline=False
        )
        
        if user_captcha:
            embed.add_field(
                name="Active Captcha",
                value=f"Code: `{user_captcha.get('code', 'N/A')}`\n"
                      f"Attempts: {user_captcha.get('attempts', 0)}/{user_captcha.get('max_attempts', 3)}",
                inline=False
            )
        
        if user_cooldown:
            cooldown_end = datetime.fromisoformat(user_cooldown['cooldown_end'])
            remaining = cooldown_end - datetime.now()
            if remaining.total_seconds() > 0:
                hours = int(remaining.total_seconds() // 3600)
                minutes = int((remaining.total_seconds() % 3600) // 60)
                embed.add_field(
                    name="Cooldown",
                    value=f"⏰ {hours}h {minutes}m remaining",
                    inline=False
                )
        
        await ctx.send(embed=embed)
    
    @commands.command(name="clear_verification")
    @commands.has_permissions(administrator=True)
    async def clear_verification(self, ctx, user: discord.Member):
        """Clear verification data for a user"""
        # Clear captcha data
        captcha_data = self.load_captcha_data()
        if str(user.id) in captcha_data:
            del captcha_data[str(user.id)]
            self.save_captcha_data(captcha_data)
        
        # Clear cooldown data
        cooldown_data = self.load_cooldown_data()
        if str(user.id) in cooldown_data:
            del cooldown_data[str(user.id)]
            self.save_cooldown_data(cooldown_data)
        
        await ctx.send(f"✅ Cleared all verification data for {user.mention}")
    
    @commands.command(name="verification_stats")
    @commands.has_permissions(administrator=True)
    async def verification_stats(self, ctx):
        """Show verification system statistics"""
        captcha_data = self.load_captcha_data()
        cooldown_data = self.load_cooldown_data()
        
        # Count active captchas
        active_captchas = len(captcha_data)
        
        # Count users on cooldown
        current_time = datetime.now()
        users_on_cooldown = 0
        for user_id, data in cooldown_data.items():
            cooldown_end = datetime.fromisoformat(data['cooldown_end'])
            if current_time < cooldown_end:
                users_on_cooldown += 1
        
        # Count verified users
        verified_role = ctx.guild.get_role(903238068910309398)
        verified_count = len(verified_role.members) if verified_role else 0
        
        embed = discord.Embed(
            title="📊 Verification System Statistics",
            color=0x0099ff
        )
        
        embed.add_field(
            name="Verified Users",
            value=f"✅ {verified_count}",
            inline=True
        )
        
        embed.add_field(
            name="Active Captchas",
            value=f"🔐 {active_captchas}",
            inline=True
        )
        
        embed.add_field(
            name="Users on Cooldown",
            value=f"⏰ {users_on_cooldown}",
            inline=True
        )
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(VerificationAdmin(bot))
