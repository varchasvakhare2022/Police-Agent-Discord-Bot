import discord
from discord.ext import commands
import json
import os
import random

class PoliceFeatures(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.command_count = 0
        self.badges_file = 'data/police_badges.json'
        self.count_file = 'data/command_count.json'
        self.load_data()
        
        self.siren_messages = [
            "🚨 YOU'RE UNDER ARREST… just kidding.",
            "🚨 PULL OVER! Oh wait, this is Discord...",
            "🚨 STOP RIGHT THERE! ...and have a great day!",
            "🚨 FREEZE! Actually, keep typing, it's fine.",
            "🚨 HANDS UP! Now give yourself a high-five!"
        ]
    
    def load_data(self):
        """Load command count and badges data"""
        # Load command count
        if os.path.exists(self.count_file):
            try:
                with open(self.count_file, 'r') as f:
                    data = json.load(f)
                    self.command_count = data.get('count', 0)
            except:
                self.command_count = 0
        
        # Load badges data
        if os.path.exists(self.badges_file):
            try:
                with open(self.badges_file, 'r') as f:
                    self.badges_data = json.load(f)
            except:
                self.badges_data = {}
        else:
            self.badges_data = {}
    
    def save_data(self):
        """Save command count and badges data"""
        # Save command count
        os.makedirs('data', exist_ok=True)
        with open(self.count_file, 'w') as f:
            json.dump({'count': self.command_count}, f)
        
        # Save badges data
        with open(self.badges_file, 'w') as f:
            json.dump(self.badges_data, f)
    
    @commands.Cog.listener()
    async def on_command_completion(self, ctx):
        """Track command usage for easter eggs"""
        self.command_count += 1
        
        # Check for 100th command
        if self.command_count % 100 == 0:
            message = random.choice(self.siren_messages)
            await ctx.send(message)
        
        self.save_data()
    
    @commands.command(name='badge')
    @commands.has_permissions(manage_messages=True)
    async def give_badge(self, ctx, member: discord.Member, *, reason: str = "Good behavior"):
        """Give a Good Citizen badge to a member"""
        user_id = str(member.id)
        guild_id = str(ctx.guild.id)
        
        if guild_id not in self.badges_data:
            self.badges_data[guild_id] = {}
        
        if user_id not in self.badges_data[guild_id]:
            self.badges_data[guild_id][user_id] = {
                'badges': 0,
                'reasons': []
            }
        
        self.badges_data[guild_id][user_id]['badges'] += 1
        self.badges_data[guild_id][user_id]['reasons'].append(reason)
        
        badge_count = self.badges_data[guild_id][user_id]['badges']
        
        embed = discord.Embed(
            title="👮‍♂️ Good Citizen Badge Awarded!",
            description=f"{member.mention} has been awarded a **Good Citizen Badge**!",
            color=0x00ff00
        )
        embed.add_field(name="Reason", value=reason, inline=False)
        embed.add_field(name="Total Badges", value=f"🏅 {badge_count}", inline=True)
        embed.add_field(name="Awarded by", value=ctx.author.mention, inline=True)
        embed.set_thumbnail(url=member.display_avatar.url)
        
        await ctx.send(embed=embed)
        self.save_data()
    
    @commands.command(name='badges')
    async def check_badges(self, ctx, member: discord.Member = None):
        """Check a member's Good Citizen badges"""
        member = member or ctx.author
        user_id = str(member.id)
        guild_id = str(ctx.guild.id)
        
        if guild_id not in self.badges_data or user_id not in self.badges_data[guild_id]:
            await ctx.send(f"{member.mention} has no Good Citizen badges yet.")
            return
        
        user_badges = self.badges_data[guild_id][user_id]
        badge_count = user_badges['badges']
        reasons = user_badges['reasons']
        
        embed = discord.Embed(
            title=f"👮‍♂️ {member.display_name}'s Good Citizen Badges",
            color=0x0099ff
        )
        embed.add_field(name="Total Badges", value=f"🏅 {badge_count}", inline=True)
        
        if reasons:
            recent_reasons = reasons[-5:]  # Show last 5 reasons
            embed.add_field(
                name="Recent Awards",
                value="\n".join(f"• {reason}" for reason in recent_reasons),
                inline=False
            )
        
        embed.set_thumbnail(url=member.display_avatar.url)
        await ctx.send(embed=embed)
    
    @commands.command(name='leaderboard')
    async def badge_leaderboard(self, ctx):
        """Show Good Citizen badge leaderboard"""
        guild_id = str(ctx.guild.id)
        
        if guild_id not in self.badges_data:
            await ctx.send("No badges have been awarded in this server yet.")
            return
        
        # Sort users by badge count
        user_badges = []
        for user_id, data in self.badges_data[guild_id].items():
            try:
                user = await self.bot.fetch_user(int(user_id))
                user_badges.append((user.display_name, data['badges']))
            except:
                continue
        
        user_badges.sort(key=lambda x: x[1], reverse=True)
        
        if not user_badges:
            await ctx.send("No valid badge holders found.")
            return
        
        embed = discord.Embed(
            title="🏆 Good Citizen Badge Leaderboard",
            color=0xffd700
        )
        
        for i, (username, badge_count) in enumerate(user_badges[:10], 1):
            medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
            embed.add_field(
                name=f"{medal} {username}",
                value=f"🏅 {badge_count} badges",
                inline=False
            )
        
        await ctx.send(embed=embed)
    
    @commands.command(name='siren_test')
    @commands.has_permissions(administrator=True)
    async def test_siren(self, ctx):
        """Test the siren easter egg (admin only)"""
        message = random.choice(self.siren_messages)
        await ctx.send(f"🚨 **Siren Test:** {message}")
    
    @commands.command(name='command_count')
    async def show_command_count(self, ctx):
        """Show current command count"""
        next_siren = 100 - (self.command_count % 100)
        await ctx.send(f"📊 **Command Statistics:**\n"
                      f"Total commands: {self.command_count}\n"
                      f"Next siren alert in: {next_siren} commands")

async def setup(bot):
    await bot.add_cog(PoliceFeatures(bot))
