import discord
from discord.ext import commands, tasks
import json
import random
import string
import asyncio
from datetime import datetime, timedelta
import os
from PIL import Image, ImageDraw, ImageFont
import io
import base64

class CaptchaVerification(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.captcha_data_file = 'data/captcha_data.json'
        self.cooldown_data_file = 'data/verification_cooldown.json'
        self.cleanup_task.start()
    
    def cog_unload(self):
        self.cleanup_task.cancel()
    
    def generate_captcha(self):
        """Generate a random captcha string"""
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    
    def generate_captcha_image(self, captcha_text):
        """Generate a captcha image with the given text"""
        # Create image with random background
        width, height = 200, 80
        bg_colors = [
            (240, 248, 255),  # Alice Blue
            (255, 250, 240),  # Floral White
            (245, 245, 220),  # Beige
            (255, 255, 240),  # Ivory
            (248, 248, 255),  # Ghost White
        ]
        bg_color = random.choice(bg_colors)
        
        # Create image
        image = Image.new('RGB', (width, height), bg_color)
        draw = ImageDraw.Draw(image)
        
        # Add random noise lines
        for _ in range(random.randint(8, 15)):
            x1 = random.randint(0, width)
            y1 = random.randint(0, height)
            x2 = random.randint(0, width)
            y2 = random.randint(0, height)
            line_color = (random.randint(100, 200), random.randint(100, 200), random.randint(100, 200))
            draw.line([(x1, y1), (x2, y2)], fill=line_color, width=random.randint(1, 3))
        
        # Add random noise dots
        for _ in range(random.randint(50, 100)):
            x = random.randint(0, width)
            y = random.randint(0, height)
            dot_color = (random.randint(150, 220), random.randint(150, 220), random.randint(150, 220))
            draw.point((x, y), fill=dot_color)
        
        # Try to use a font, fallback to default if not available
        try:
            # Try different font sizes
            font_size = random.randint(24, 32)
            font = ImageFont.truetype("arial.ttf", font_size)
        except:
            try:
                font = ImageFont.load_default()
            except:
                font = None
        
        # Draw the captcha text with random positioning and colors
        text_color = (random.randint(0, 100), random.randint(0, 100), random.randint(0, 100))
        
        # Calculate text position (center it roughly)
        if font:
            bbox = draw.textbbox((0, 0), captcha_text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
        else:
            text_width = len(captcha_text) * 10
            text_height = 20
        
        x = (width - text_width) // 2 + random.randint(-10, 10)
        y = (height - text_height) // 2 + random.randint(-5, 5)
        
        # Draw text with slight rotation
        angle = random.randint(-15, 15)
        
        # Create a temporary image for rotation
        temp_img = Image.new('RGBA', (text_width + 20, text_height + 20), (0, 0, 0, 0))
        temp_draw = ImageDraw.Draw(temp_img)
        
        if font:
            temp_draw.text((10, 10), captcha_text, fill=text_color, font=font)
        else:
            temp_draw.text((10, 10), captcha_text, fill=text_color)
        
        # Rotate the text
        rotated = temp_img.rotate(angle, expand=1)
        
        # Paste rotated text onto main image
        image.paste(rotated, (x-10, y-10), rotated)
        
        # Add some distortion lines
        for _ in range(random.randint(3, 6)):
            x1 = random.randint(0, width)
            y1 = random.randint(0, height)
            x2 = random.randint(0, width)
            y2 = random.randint(0, height)
            line_color = (random.randint(200, 255), random.randint(200, 255), random.randint(200, 255))
            draw.line([(x1, y1), (x2, y2)], fill=line_color, width=1)
        
        # Convert to bytes
        img_bytes = io.BytesIO()
        image.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        
        return img_bytes
    
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
    
    def is_on_cooldown(self, user_id):
        """Check if user is on cooldown"""
        cooldown_data = self.load_cooldown_data()
        user_id_str = str(user_id)
        
        if user_id_str not in cooldown_data:
            return False
        
        cooldown_end = datetime.fromisoformat(cooldown_data[user_id_str]['cooldown_end'])
        return datetime.now() < cooldown_end
    
    def get_cooldown_remaining(self, user_id):
        """Get remaining cooldown time for user"""
        cooldown_data = self.load_cooldown_data()
        user_id_str = str(user_id)
        
        if user_id_str not in cooldown_data:
            return None
        
        cooldown_end = datetime.fromisoformat(cooldown_data[user_id_str]['cooldown_end'])
        remaining = cooldown_end - datetime.now()
        return remaining if remaining.total_seconds() > 0 else None
    
    def add_cooldown(self, user_id, hours=3):
        """Add user to cooldown"""
        cooldown_data = self.load_cooldown_data()
        user_id_str = str(user_id)
        
        cooldown_end = datetime.now() + timedelta(hours=hours)
        cooldown_data[user_id_str] = {
            'cooldown_end': cooldown_end.isoformat(),
            'added_at': datetime.now().isoformat()
        }
        
        self.save_cooldown_data(cooldown_data)
    
    def remove_cooldown(self, user_id):
        """Remove user from cooldown"""
        cooldown_data = self.load_cooldown_data()
        user_id_str = str(user_id)
        
        if user_id_str in cooldown_data:
            del cooldown_data[user_id_str]
            self.save_cooldown_data(cooldown_data)
    
    @tasks.loop(minutes=5)
    async def cleanup_task(self):
        """Clean up expired cooldowns"""
        cooldown_data = self.load_cooldown_data()
        current_time = datetime.now()
        
        expired_users = []
        for user_id, data in cooldown_data.items():
            cooldown_end = datetime.fromisoformat(data['cooldown_end'])
            if current_time >= cooldown_end:
                expired_users.append(user_id)
        
        for user_id in expired_users:
            del cooldown_data[user_id]
        
        if expired_users:
            self.save_cooldown_data(cooldown_data)
            print(f"Cleaned up {len(expired_users)} expired verification cooldowns")
    
    @cleanup_task.before_loop
    async def before_cleanup_task(self):
        await self.bot.wait_until_ready()
    
    async def send_captcha_dm(self, user, captcha_code):
        """Send captcha image to user's DM"""
        # Generate captcha image
        img_bytes = self.generate_captcha_image(captcha_code)
        
        # Create file object
        file = discord.File(img_bytes, filename="captcha.png")
        
        embed = discord.Embed(
            title="🔐 Server Verification Captcha",
            description="Please solve the captcha below to get verified!\n\nType the text you see in the image in the verification channel to complete verification.",
            color=0x00ff00
        )
        embed.set_image(url="attachment://captcha.png")
        embed.set_footer(text="You have 3 attempts to solve this captcha")
        
        try:
            await user.send(embed=embed, file=file)
            return True
        except discord.Forbidden:
            return False
    
    async def handle_verification_attempt(self, interaction, user):
        """Handle verification attempt with captcha"""
        # Check if user is already verified
        verified_role = interaction.guild.get_role(903238068910309398)
        if verified_role and verified_role in user.roles:
            embed = discord.Embed(
                title="✅ Already Verified",
                description="Listen bud, You are already verified and remember not to waste time of Police Agents from next time.",
                color=0x00ff00
            )
            embed.set_footer(text="No need to verify again")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Check if user is on cooldown
        if self.is_on_cooldown(user.id):
            remaining = self.get_cooldown_remaining(user.id)
            hours = int(remaining.total_seconds() // 3600)
            minutes = int((remaining.total_seconds() % 3600) // 60)
            
            embed = discord.Embed(
                title="⏰ Verification Cooldown",
                description=f"You are on cooldown! Please wait **{hours}h {minutes}m** before trying to verify again.",
                color=0xff0000
            )
            embed.set_footer(text="Please wait before trying again")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Generate captcha
        captcha_code = self.generate_captcha()
        
        # Store captcha data
        captcha_data = self.load_captcha_data()
        captcha_data[str(user.id)] = {
            'code': captcha_code,
            'attempts': 0,
            'max_attempts': 3,
            'created_at': datetime.now().isoformat()
        }
        self.save_captcha_data(captcha_data)
        
        # Try to send DM
        dm_sent = await self.send_captcha_dm(user, captcha_code)
        
        if dm_sent:
            embed = discord.Embed(
                title="📧 Captcha Sent!",
                description="I have sent you a captcha in your DMs! Please solve it to get verified.",
                color=0x0099ff
            )
            embed.set_footer(text="Check your DMs")
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            embed = discord.Embed(
                title="❌ DM Failed",
                description="I am unable to DM you. Please check your DM settings and allow DMs from server members, then try again.",
                color=0xff0000
            )
            embed.set_footer(text="Enable DMs from server members")
            await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @commands.Cog.listener()
    async def on_message(self, message):
        """Handle direct captcha input"""
        if message.author.bot:
            return
        
        # Check if message looks like a captcha code (6 characters, alphanumeric)
        if len(message.content) == 6 and message.content.isalnum():
            user_id = str(message.author.id)
            captcha_data = self.load_captcha_data()
            
            if user_id in captcha_data:
                user_captcha = captcha_data[user_id]
                
                # Handle DM case
                if not message.guild:
                    # Check attempts
                    if user_captcha['attempts'] >= user_captcha['max_attempts']:
                        # Add to cooldown
                        self.add_cooldown(message.author.id)
                        
                        # Clean up captcha data
                        del captcha_data[user_id]
                        self.save_captcha_data(captcha_data)
                        
                        embed = discord.Embed(
                            title="⏰ Verification Cooldown",
                            description="You have exceeded the maximum attempts. You are now on a **3-hour cooldown**.",
                            color=0xff0000
                        )
                        embed.set_footer(text="Please wait before trying again")
                        await message.reply(embed=embed)
                        return
                    
                    # Check captcha
                    if message.content.upper() == user_captcha['code']:
                        # Success! Find the guild and give verified role
                        # We need to find which guild the user is in
                        guild = None
                        for g in self.bot.guilds:
                            if g.get_member(message.author.id):
                                guild = g
                                break
                        
                        if guild:
                            verified_role = guild.get_role(903238068910309398)
                            if verified_role:
                                member = guild.get_member(message.author.id)
                                if member:
                                    await member.add_roles(verified_role)
                                
                                # Clean up captcha data
                                del captcha_data[user_id]
                                self.save_captcha_data(captcha_data)
                                
                                # Send success DM
                                embed = discord.Embed(
                                    title="✅ Verification Successful!",
                                    description="Congratulations! You have successfully verified yourself and gained access to the server.\n\nYou now have access to all verified channels and features!",
                                    color=0x00ff00
                                )
                                embed.set_footer(text="Welcome to the server!")
                                await message.reply(embed=embed)
                            else:
                                embed = discord.Embed(
                                    title="❌ Error",
                                    description="Verified role not found. Please contact an administrator.",
                                    color=0xff0000
                                )
                                await message.reply(embed=embed)
                        else:
                            embed = discord.Embed(
                                title="❌ Error",
                                description="Could not find the server. Please try again.",
                                color=0xff0000
                            )
                            await message.reply(embed=embed)
                    else:
                        # Wrong captcha
                        user_captcha['attempts'] += 1
                        remaining_attempts = user_captcha['max_attempts'] - user_captcha['attempts']
                        
                        captcha_data[user_id] = user_captcha
                        self.save_captcha_data(captcha_data)
                        
                        if remaining_attempts > 0:
                            embed = discord.Embed(
                                title="❌ Incorrect Captcha",
                                description=f"You have **{remaining_attempts} attempts** remaining.",
                                color=0xff9900
                            )
                            embed.set_footer(text="Please try again")
                            await message.reply(embed=embed)
                        else:
                            # Add to cooldown
                            self.add_cooldown(message.author.id)
                            
                            # Clean up captcha data
                            del captcha_data[user_id]
                            self.save_captcha_data(captcha_data)
                            
                            embed = discord.Embed(
                                title="⏰ Verification Cooldown",
                                description="You have exceeded the maximum attempts. You are now on a **3-hour cooldown**.",
                                color=0xff0000
                            )
                            embed.set_footer(text="Please wait before trying again")
                            await message.reply(embed=embed)
                    return
                
                # Handle server channel case
                if message.guild:
                    # Get verified role by ID
                    verified_role = message.guild.get_role(903238068910309398)
                    if not verified_role:
                        embed = discord.Embed(
                            title="❌ Error",
                            description="Verified role not found. Please contact an administrator.",
                            color=0xff0000
                        )
                        await message.reply(embed=embed, delete_after=5)
                        return
                    
                    # Check if user is already verified
                    if verified_role in message.author.roles:
                        # Clean up captcha data
                        del captcha_data[user_id]
                        self.save_captcha_data(captcha_data)
                        embed = discord.Embed(
                            title="✅ Already Verified",
                            description="You are already verified!",
                            color=0x00ff00
                        )
                        await message.reply(embed=embed, delete_after=5)
                        return
                    
                    # Check attempts
                    if user_captcha['attempts'] >= user_captcha['max_attempts']:
                        # Add to cooldown
                        self.add_cooldown(message.author.id)
                        
                        # Clean up captcha data
                        del captcha_data[user_id]
                        self.save_captcha_data(captcha_data)
                        
                        embed = discord.Embed(
                            title="⏰ Verification Cooldown",
                            description="You have exceeded the maximum attempts. You are now on a **3-hour cooldown**.",
                            color=0xff0000
                        )
                        embed.set_footer(text="Please wait before trying again")
                        await message.reply(embed=embed, delete_after=10)
                        return
                    
                    # Check captcha
                    if message.content.upper() == user_captcha['code']:
                        # Success! Give verified role
                        await message.author.add_roles(verified_role)
                        
                        # Clean up captcha data
                        del captcha_data[user_id]
                        self.save_captcha_data(captcha_data)
                        
                        embed = discord.Embed(
                            title="✅ Verification Successful!",
                            description="You have been verified successfully!",
                            color=0x00ff00
                        )
                        embed.set_footer(text="Welcome to the server!")
                        await message.reply(embed=embed, delete_after=5)
                        
                        # Send success DM
                        try:
                            embed = discord.Embed(
                                title="✅ Verification Successful!",
                                description="Congratulations! You have successfully verified yourself and gained access to the server.\n\nYou now have access to all verified channels and features!",
                                color=0x00ff00
                            )
                            embed.set_footer(text="Welcome to the server!")
                            await message.author.send(embed=embed)
                        except discord.Forbidden:
                            # Send a follow-up message in the channel if DM fails
                            embed = discord.Embed(
                                title="✅ Verification Complete!",
                                description="Check your DMs for confirmation.",
                                color=0x00ff00
                            )
                            await message.reply(embed=embed, delete_after=10)
                        except Exception as e:
                            embed = discord.Embed(
                                title="✅ Verification Complete!",
                                description="Check your DMs for confirmation.",
                                color=0x00ff00
                            )
                            await message.reply(embed=embed, delete_after=10)
                    else:
                        # Wrong captcha
                        user_captcha['attempts'] += 1
                        remaining_attempts = user_captcha['max_attempts'] - user_captcha['attempts']
                        
                        captcha_data[user_id] = user_captcha
                        self.save_captcha_data(captcha_data)
                        
                        if remaining_attempts > 0:
                            embed = discord.Embed(
                                title="❌ Incorrect Captcha",
                                description=f"You have **{remaining_attempts} attempts** remaining.",
                                color=0xff9900
                            )
                            embed.set_footer(text="Please try again")
                            await message.reply(embed=embed, delete_after=5)
                        else:
                            # Add to cooldown
                            self.add_cooldown(message.author.id)
                            
                            # Clean up captcha data
                            del captcha_data[user_id]
                            self.save_captcha_data(captcha_data)
                            
                            embed = discord.Embed(
                                title="⏰ Verification Cooldown",
                                description="You have exceeded the maximum attempts. You are now on a **3-hour cooldown**.",
                                color=0xff0000
                            )
                            embed.set_footer(text="Please wait before trying again")
                            await message.reply(embed=embed, delete_after=10)

    @commands.command(name="verify_captcha")
    async def verify_captcha(self, ctx, *, captcha_input):
        """Verify captcha input"""
        user_id = str(ctx.author.id)
        captcha_data = self.load_captcha_data()
        
        if user_id not in captcha_data:
            embed = discord.Embed(
                title="❌ No Active Captcha",
                description="No active captcha found. Please use the verify button first.",
                color=0xff0000
            )
            await ctx.reply(embed=embed, delete_after=5)
            return
        
        user_captcha = captcha_data[user_id]
        
        # Check if user is already verified
        verified_role = ctx.guild.get_role(903238068910309398)
        if verified_role and verified_role in ctx.author.roles:
            # Clean up captcha data
            del captcha_data[user_id]
            self.save_captcha_data(captcha_data)
            embed = discord.Embed(
                title="✅ Already Verified",
                description="You are already verified!",
                color=0x00ff00
            )
            await ctx.reply(embed=embed, delete_after=5)
            return
        
        # Check attempts
        if user_captcha['attempts'] >= user_captcha['max_attempts']:
            # Add to cooldown
            self.add_cooldown(ctx.author.id)
            
            # Clean up captcha data
            del captcha_data[user_id]
            self.save_captcha_data(captcha_data)
            
            embed = discord.Embed(
                title="⏰ Verification Cooldown",
                description="You have exceeded the maximum attempts. You are now on a **3-hour cooldown**.",
                color=0xff0000
            )
            embed.set_footer(text="Please wait before trying again")
            await ctx.reply(embed=embed, delete_after=10)
            return
        
        # Check captcha
        if captcha_input.upper() == user_captcha['code']:
            # Success! Give verified role
            await ctx.author.add_roles(verified_role)
            
            # Clean up captcha data
            del captcha_data[user_id]
            self.save_captcha_data(captcha_data)
            
            embed = discord.Embed(
                title="✅ Verification Successful!",
                description="You have been verified successfully!",
                color=0x00ff00
            )
            embed.set_footer(text="Welcome to the server!")
            await ctx.reply(embed=embed, delete_after=5)
            
            # Send success DM
            try:
                embed = discord.Embed(
                    title="✅ Verification Successful!",
                    description="Congratulations! You have successfully verified yourself and gained access to the server.\n\nYou now have access to all verified channels and features!",
                    color=0x00ff00
                )
                embed.set_footer(text="Welcome to the server!")
                await ctx.author.send(embed=embed)
            except discord.Forbidden:
                # Send a follow-up message in the channel if DM fails
                embed = discord.Embed(
                    title="✅ Verification Complete!",
                    description="Check your DMs for confirmation.",
                    color=0x00ff00
                )
                await ctx.reply(embed=embed, delete_after=10)
            except Exception as e:
                embed = discord.Embed(
                    title="✅ Verification Complete!",
                    description="Check your DMs for confirmation.",
                    color=0x00ff00
                )
                await ctx.reply(embed=embed, delete_after=10)
        else:
            # Wrong captcha
            user_captcha['attempts'] += 1
            remaining_attempts = user_captcha['max_attempts'] - user_captcha['attempts']
            
            captcha_data[user_id] = user_captcha
            self.save_captcha_data(captcha_data)
            
            if remaining_attempts > 0:
                embed = discord.Embed(
                    title="❌ Incorrect Captcha",
                    description=f"You have **{remaining_attempts} attempts** remaining.",
                    color=0xff9900
                )
                embed.set_footer(text="Please try again")
                await ctx.reply(embed=embed, delete_after=5)
            else:
                # Add to cooldown
                self.add_cooldown(ctx.author.id)
                
                # Clean up captcha data
                del captcha_data[user_id]
                self.save_captcha_data(captcha_data)
                
                embed = discord.Embed(
                    title="⏰ Verification Cooldown",
                    description="You have exceeded the maximum attempts. You are now on a **3-hour cooldown**.",
                    color=0xff0000
                )
                embed.set_footer(text="Please wait before trying again")
                await ctx.reply(embed=embed, delete_after=10)

async def setup(bot):
    await bot.add_cog(CaptchaVerification(bot))
