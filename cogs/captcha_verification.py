import discord
from discord.ext import commands
import random
import string
import time
import json
import os
from datetime import datetime, timedelta

class CaptchaVerification(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.captcha_file = "data/captcha_sessions.json"
        self.load_captcha_sessions()
        
        # CAPTCHA sessions: user_id -> {"code": str, "timestamp": float, "attempts": int}
        self.captcha_sessions = {}

    def load_captcha_sessions(self):
        """Load CAPTCHA sessions from JSON file"""
        try:
            if os.path.exists(self.captcha_file):
                with open(self.captcha_file, 'r') as f:
                    self.captcha_sessions = json.load(f)
        except Exception as e:
            print(f"Error loading CAPTCHA sessions: {e}")
            self.captcha_sessions = {}

    def save_captcha_sessions(self):
        """Save CAPTCHA sessions to JSON file"""
        try:
            os.makedirs("data", exist_ok=True)
            with open(self.captcha_file, 'w') as f:
                json.dump(self.captcha_sessions, f, indent=2)
        except Exception as e:
            print(f"Error saving CAPTCHA sessions: {e}")

    def generate_captcha_code(self, length=6):
        """Generate a random CAPTCHA code"""
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

    def create_captcha_embed(self, code, user):
        """Create CAPTCHA verification embed"""
        embed = discord.Embed(
            title="🔐 CAPTCHA Verification Required",
            description=f"Hello {user.mention}! Please complete the CAPTCHA to verify you're human.",
            color=0x9C84EF
        )
        
        embed.add_field(
            name="📝 Instructions",
            value="1. Look at the code below\n2. Type it exactly as shown\n3. You have 5 minutes to complete\n4. Case sensitive!",
            inline=False
        )
        
        embed.add_field(
            name="🔤 Verification Code",
            value=f"```\n{code}\n```",
            inline=False
        )
        
        embed.add_field(
            name="⏰ Time Limit",
            value="5 minutes",
            inline=True
        )
        
        embed.add_field(
            name="❌ Attempts",
            value="3 attempts allowed",
            inline=True
        )
        
        embed.set_footer(text="Police Agent Bot - Anti-Bot Protection")
        
        return embed

    async def start_captcha_verification(self, user, guild):
        """Start CAPTCHA verification process"""
        user_id = str(user.id)
        
        # Generate CAPTCHA code
        captcha_code = self.generate_captcha_code()
        
        # Store session
        self.captcha_sessions[user_id] = {
            "code": captcha_code,
            "timestamp": time.time(),
            "attempts": 0,
            "guild_id": guild.id
        }
        self.save_captcha_sessions()
        
        # Create embed
        embed = self.create_captcha_embed(captcha_code, user)
        
        # Send DM to user
        try:
            await user.send(embed=embed)
            return True
        except:
            return False

    async def verify_captcha(self, user, input_code):
        """Verify CAPTCHA code"""
        user_id = str(user.id)
        
        if user_id not in self.captcha_sessions:
            return False, "No active CAPTCHA session found!"
        
        session = self.captcha_sessions[user_id]
        
        # Check if session expired (5 minutes)
        if time.time() - session["timestamp"] > 300:
            del self.captcha_sessions[user_id]
            self.save_captcha_sessions()
            return False, "CAPTCHA session expired! Please start verification again."
        
        # Check attempts
        if session["attempts"] >= 3:
            del self.captcha_sessions[user_id]
            self.save_captcha_sessions()
            return False, "Too many failed attempts! Please start verification again."
        
        # Verify code
        if input_code.upper() == session["code"]:
            # Success!
            guild_id = session["guild_id"]
            guild = self.bot.get_guild(guild_id)
            
            if guild:
                # Add verified role
                verified_role = discord.utils.get(guild.roles, name="Verified")
                if not verified_role:
                    verified_role = await guild.create_role(
                        name="Verified",
                        color=discord.Color.green(),
                        reason="Auto-created verified role for CAPTCHA verification"
                    )
                
                await user.add_roles(verified_role, reason="CAPTCHA verification completed")
                
                # Log the action
                logging_cog = self.bot.get_cog('LoggingSystem')
                if logging_cog:
                    await logging_cog.log_system_event(
                        "captcha_verification",
                        f"{user.display_name} completed CAPTCHA verification",
                        guild,
                        user
                    )
            
            # Clean up session
            del self.captcha_sessions[user_id]
            self.save_captcha_sessions()
            
            return True, "CAPTCHA verification successful! You now have access to the server."
        
        else:
            # Failed attempt
            session["attempts"] += 1
            self.save_captcha_sessions()
            
            remaining_attempts = 3 - session["attempts"]
            if remaining_attempts > 0:
                return False, f"Incorrect code! {remaining_attempts} attempts remaining."
            else:
                return False, "Too many failed attempts! Please start verification again."

    @commands.command(name="verify-captcha")
    @commands.has_permissions(administrator=True)
    async def verify_captcha_command(self, ctx: commands.Context, member: discord.Member = None):
        """Send CAPTCHA verification to a user"""
        
        if not member:
            await ctx.reply("❌ Please specify a user to verify!")
            return
        
        # Check if user is already verified
        verified_role = discord.utils.get(ctx.guild.roles, name="Verified")
        if verified_role and verified_role in member.roles:
            await ctx.reply(f"✅ {member.mention} is already verified!")
            return
        
        # Start CAPTCHA verification
        success = await self.start_captcha_verification(member, ctx.guild)
        
        if success:
            embed = discord.Embed(
                title="✅ CAPTCHA Sent",
                description=f"CAPTCHA verification has been sent to {member.mention}'s DMs",
                color=0x00ff00
            )
            await ctx.reply(embed=embed)
        else:
            embed = discord.Embed(
                title="❌ CAPTCHA Failed",
                description=f"Could not send CAPTCHA to {member.mention}. They may have DMs disabled.",
                color=0xff0000
            )
            await ctx.reply(embed=embed)

    @commands.command(name="captcha-verify")
    async def captcha_verify(self, ctx: commands.Context, *, code: str):
        """Verify CAPTCHA code"""
        
        success, message = await self.verify_captcha(ctx.author, code)
        
        if success:
            embed = discord.Embed(
                title="✅ Verification Successful!",
                description=message,
                color=0x00ff00
            )
            await ctx.reply(embed=embed, ephemeral=True)
        else:
            embed = discord.Embed(
                title="❌ Verification Failed",
                description=message,
                color=0xff0000
            )
            await ctx.reply(embed=embed, ephemeral=True)

    @commands.command(name="captcha-status")
    async def captcha_status(self, ctx: commands.Context):
        """Check CAPTCHA verification status"""
        
        user_id = str(ctx.author.id)
        
        if user_id not in self.captcha_sessions:
            await ctx.reply("❌ No active CAPTCHA session found!", ephemeral=True)
            return
        
        session = self.captcha_sessions[user_id]
        remaining_time = 300 - (time.time() - session["timestamp"])
        remaining_attempts = 3 - session["attempts"]
        
        embed = discord.Embed(
            title="🔐 CAPTCHA Status",
            description=f"**Time Remaining:** {int(remaining_time)} seconds\n**Attempts Left:** {remaining_attempts}",
            color=0x9C84EF
        )
        
        await ctx.reply(embed=embed, ephemeral=True)

    @commands.command(name="captcha-reset")
    @commands.has_permissions(administrator=True)
    async def captcha_reset(self, ctx: commands.Context, member: discord.Member):
        """Reset CAPTCHA verification for a user"""
        
        user_id = str(member.id)
        
        if user_id in self.captcha_sessions:
            del self.captcha_sessions[user_id]
            self.save_captcha_sessions()
        
        embed = discord.Embed(
            title="✅ CAPTCHA Reset",
            description=f"CAPTCHA verification has been reset for {member.mention}",
            color=0x00ff00
        )
        
        await ctx.reply(embed=embed)

    @commands.command(name="captcha-stats")
    @commands.has_permissions(administrator=True)
    async def captcha_stats(self, ctx: commands.Context):
        """Show CAPTCHA verification statistics"""
        
        active_sessions = len(self.captcha_sessions)
        
        embed = discord.Embed(
            title="📊 CAPTCHA Statistics",
            color=0x9C84EF
        )
        
        embed.add_field(
            name="Active Sessions",
            value=str(active_sessions),
            inline=True
        )
        
        embed.add_field(
            name="Total Users",
            value=str(len(ctx.guild.members)),
            inline=True
        )
        
        # Count verified users
        verified_role = discord.utils.get(ctx.guild.roles, name="Verified")
        verified_count = len(verified_role.members) if verified_role else 0
        
        embed.add_field(
            name="Verified Users",
            value=str(verified_count),
            inline=True
        )
        
        await ctx.reply(embed=embed)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        """Automatically send CAPTCHA to new members"""
        
        # Check if CAPTCHA verification is enabled for this guild
        # You can add guild-specific settings here
        
        # Wait a bit for the member to fully join
        await asyncio.sleep(2)
        
        # Start CAPTCHA verification
        await self.start_captcha_verification(member, member.guild)

    @commands.Cog.listener()
    async def on_message(self, message):
        """Handle CAPTCHA verification in DMs"""
        
        if message.author.bot or not isinstance(message.channel, discord.DMChannel):
            return
        
        # Check if this is a CAPTCHA verification attempt
        if len(message.content) == 6 and message.content.isalnum():
            success, response = await self.verify_captcha(message.author, message.content)
            
            if success:
                embed = discord.Embed(
                    title="✅ Verification Successful!",
                    description=response,
                    color=0x00ff00
                )
            else:
                embed = discord.Embed(
                    title="❌ Verification Failed",
                    description=response,
                    color=0xff0000
                )
            
            await message.reply(embed=embed)

async def setup(bot):
    await bot.add_cog(CaptchaVerification(bot))
