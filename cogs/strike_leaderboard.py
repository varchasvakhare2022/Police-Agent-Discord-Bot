import discord
from discord.ext import commands
import json
import os
from datetime import datetime, timedelta
import asyncio

class StrikeLeaderboard(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.strikes_file = 'data/strikes.json'
        self.leaderboard_file = 'data/leaderboard.json'
        
        # Ensure data directory exists
        os.makedirs('data', exist_ok=True)
        
        # Load data
        self.load_data()
    
    def load_data(self):
        """Load strikes and leaderboard data from JSON files"""
        # Load strikes
        if os.path.exists(self.strikes_file):
            try:
                with open(self.strikes_file, 'r') as f:
                    self.strikes = json.load(f)
            except:
                self.strikes = {}
        else:
            self.strikes = {}
        
        # Load leaderboard
        if os.path.exists(self.leaderboard_file):
            try:
                with open(self.leaderboard_file, 'r') as f:
                    self.leaderboard = json.load(f)
            except:
                self.leaderboard = {}
        else:
            self.leaderboard = {}
    
    def save_data(self):
        """Save strikes and leaderboard to JSON files"""
        with open(self.strikes_file, 'w') as f:
            json.dump(self.strikes, f, indent=2)
        
        with open(self.leaderboard_file, 'w') as f:
            json.dump(self.leaderboard, f, indent=2)
    
    def add_strike(self, user_id, moderator_id, reason, strike_type="warning"):
        """Add a strike to user's record"""
        user_id = str(user_id)
        strike_id = f"STRIKE_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{user_id}"
        
        strike_entry = {
            'strike_id': strike_id,
            'timestamp': datetime.now().isoformat(),
            'moderator_id': str(moderator_id),
            'reason': reason,
            'type': strike_type
        }
        
        # Add to user's strikes
        if user_id not in self.strikes:
            self.strikes[user_id] = []
        
        self.strikes[user_id].append(strike_entry)
        
        # Update leaderboard
        self.update_leaderboard(user_id)
        
        self.save_data()
        return strike_id
    
    def update_leaderboard(self, user_id):
        """Update leaderboard with user's strike count"""
        user_id = str(user_id)
        strike_count = len(self.strikes.get(user_id, []))
        
        self.leaderboard[user_id] = {
            'strike_count': strike_count,
            'last_strike': datetime.now().isoformat(),
            'user_id': user_id
        }
        
        self.save_data()
    
    def get_leaderboard_data(self, limit=10):
        """Get leaderboard data sorted by strike count"""
        # Sort by strike count (descending)
        sorted_users = sorted(
            self.leaderboard.items(),
            key=lambda x: x[1]['strike_count'],
            reverse=True
        )
        
        return sorted_users[:limit]
    
    def get_user_strikes(self, user_id):
        """Get strikes for a specific user"""
        user_id = str(user_id)
        return self.strikes.get(user_id, [])
    
    def get_strike_stats(self, user_id):
        """Get strike statistics for a user"""
        user_id = str(user_id)
        strikes = self.strikes.get(user_id, [])
        
        if not strikes:
            return {
                'total_strikes': 0,
                'recent_strikes': 0,
                'last_strike': None,
                'strike_types': {}
            }
        
        # Count strikes by type
        strike_types = {}
        for strike in strikes:
            strike_type = strike.get('type', 'warning')
            strike_types[strike_type] = strike_types.get(strike_type, 0) + 1
        
        # Count recent strikes (last 30 days)
        cutoff_date = datetime.now() - timedelta(days=30)
        recent_strikes = [
            strike for strike in strikes
            if datetime.fromisoformat(strike['timestamp']) > cutoff_date
        ]
        
        return {
            'total_strikes': len(strikes),
            'recent_strikes': len(recent_strikes),
            'last_strike': strikes[-1]['timestamp'] if strikes else None,
            'strike_types': strike_types
        }
    
    @commands.command(name='strike')
    @commands.has_permissions(manage_messages=True)
    async def strike_command(self, ctx, member: discord.Member, *, reason: str):
        """Issue a strike to a user"""
        strike_id = self.add_strike(member.id, ctx.author.id, reason)
        
        # Create embed
        embed = discord.Embed(
            title="⚡ Strike Issued",
            color=0xff6b6b,
            timestamp=datetime.now()
        )
        embed.add_field(name="User", value=member.mention, inline=True)
        embed.add_field(name="Moderator", value=ctx.author.mention, inline=True)
        embed.add_field(name="Reason", value=reason, inline=False)
        embed.add_field(name="Strike ID", value=f"`{strike_id}`", inline=True)
        
        # Get user's strike count
        stats = self.get_strike_stats(member.id)
        embed.add_field(name="Total Strikes", value=str(stats['total_strikes']), inline=True)
        
        # Add shame message based on strike count
        if stats['total_strikes'] == 1:
            embed.add_field(name="Status", value="🟡 First strike!", inline=True)
        elif stats['total_strikes'] == 2:
            embed.add_field(name="Status", value="🟠 Second strike!", inline=True)
        elif stats['total_strikes'] == 3:
            embed.add_field(name="Status", value="🔴 Third strike!", inline=True)
        elif stats['total_strikes'] >= 5:
            embed.add_field(name="Status", value="💀 Strike Master!", inline=True)
        else:
            embed.add_field(name="Status", value="⚠️ Strike added!", inline=True)
        
        await ctx.send(embed=embed)
    
    @commands.command(name='strikes')
    async def strikes_command(self, ctx, member: discord.Member = None):
        """View strikes for a user"""
        member = member or ctx.author
        strikes = self.get_user_strikes(member.id)
        
        if not strikes:
            await ctx.send(f"{member.mention} has no strikes! 🎉")
            return
        
        stats = self.get_strike_stats(member.id)
        
        embed = discord.Embed(
            title=f"⚡ Strike History: {member.display_name}",
            color=0xff6b6b,
            timestamp=datetime.now()
        )
        
        # Show strike count
        embed.add_field(name="Total Strikes", value=str(stats['total_strikes']), inline=True)
        embed.add_field(name="Recent Strikes (30d)", value=str(stats['recent_strikes']), inline=True)
        
        # Show strike types
        if stats['strike_types']:
            type_text = ", ".join([f"{k}: {v}" for k, v in stats['strike_types'].items()])
            embed.add_field(name="Strike Types", value=type_text, inline=False)
        
        # Show last 5 strikes
        recent_strikes = strikes[-5:]
        for i, strike in enumerate(reversed(recent_strikes), 1):
            moderator = self.bot.get_user(int(strike['moderator_id']))
            moderator_name = moderator.display_name if moderator else "Unknown"
            
            embed.add_field(
                name=f"Strike #{len(strikes) - len(recent_strikes) + i}",
                value=f"**Moderator:** {moderator_name}\n"
                      f"**Reason:** {strike['reason']}\n"
                      f"**Date:** {datetime.fromisoformat(strike['timestamp']).strftime('%Y-%m-%d %H:%M')}",
                inline=False
            )
        
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.set_footer(text=f"Showing last {len(recent_strikes)} of {len(strikes)} total strikes")
        
        await ctx.send(embed=embed)
    
    @commands.command(name='strikeboard')
    async def strikeboard_command(self, ctx, limit: int = 10):
        """View the strike leaderboard (public shame board) 😂"""
        leaderboard_data = self.get_leaderboard_data(limit)
        
        if not leaderboard_data:
            await ctx.send("No strikes found! Everyone is being good! 🎉")
            return
        
        embed = discord.Embed(
            title="🏆 Strike Leaderboard (Public Shame Board) 😂",
            description="Who's been the naughtiest?",
            color=0xff6b6b,
            timestamp=datetime.now()
        )
        
        # Add shame emojis based on position
        shame_emojis = ["🥇", "🥈", "🥉", "💀", "⚡", "🔥", "💥", "💢", "😈", "👹"]
        
        for i, (user_id, data) in enumerate(leaderboard_data):
            try:
                user = await self.bot.fetch_user(int(user_id))
                username = user.display_name
                avatar_url = user.display_avatar.url
            except:
                username = f"Unknown User ({user_id})"
                avatar_url = None
            
            strike_count = data['strike_count']
            
            # Choose shame emoji
            if i < len(shame_emojis):
                shame_emoji = shame_emojis[i]
            else:
                shame_emoji = "⚡"
            
            # Add shame message based on strike count
            if strike_count >= 10:
                shame_msg = "💀 Strike Master!"
            elif strike_count >= 5:
                shame_msg = "🔥 Strike Champion!"
            elif strike_count >= 3:
                shame_msg = "⚡ Strike Expert!"
            else:
                shame_msg = "⚠️ Strike Novice!"
            
            embed.add_field(
                name=f"{shame_emoji} #{i+1} {username}",
                value=f"**Strikes:** {strike_count}\n**Status:** {shame_msg}",
                inline=True
            )
        
        # Add footer with shame message
        embed.set_footer(text="😂 Public shame board - Don't be like these people!")
        
        await ctx.send(embed=embed)
    
    @commands.command(name='strike_stats')
    async def strike_stats_command(self, ctx):
        """View overall strike statistics"""
        total_strikes = sum(len(strikes) for strikes in self.strikes.values())
        total_users = len(self.strikes)
        
        if total_strikes == 0:
            await ctx.send("🎉 No strikes found! Everyone is being good!")
            return
        
        # Calculate average strikes per user
        avg_strikes = total_strikes / total_users if total_users > 0 else 0
        
        # Count strike types
        strike_types = {}
        for user_strikes in self.strikes.values():
            for strike in user_strikes:
                strike_type = strike.get('type', 'warning')
                strike_types[strike_type] = strike_types.get(strike_type, 0) + 1
        
        embed = discord.Embed(
            title="📊 Strike Statistics",
            color=0xff6b6b,
            timestamp=datetime.now()
        )
        
        embed.add_field(name="Total Strikes", value=str(total_strikes), inline=True)
        embed.add_field(name="Users with Strikes", value=str(total_users), inline=True)
        embed.add_field(name="Average Strikes", value=f"{avg_strikes:.1f}", inline=True)
        
        # Show strike types
        if strike_types:
            type_text = "\n".join([f"**{k.title()}:** {v}" for k, v in strike_types.items()])
            embed.add_field(name="Strike Types", value=type_text, inline=False)
        
        # Show top 3 strikers
        top_strikers = self.get_leaderboard_data(3)
        if top_strikers:
            top_text = ""
            for i, (user_id, data) in enumerate(top_strikers):
                try:
                    user = await self.bot.fetch_user(int(user_id))
                    username = user.display_name
                except:
                    username = f"Unknown User ({user_id})"
                
                top_text += f"**#{i+1}** {username}: {data['strike_count']} strikes\n"
            
            embed.add_field(name="Top 3 Strikers", value=top_text, inline=False)
        
        await ctx.send(embed=embed)
    
    @commands.command(name='clear_strikes')
    @commands.has_permissions(administrator=True)
    async def clear_strikes_command(self, ctx, member: discord.Member):
        """Clear all strikes for a user (admin only)"""
        user_id = str(member.id)
        
        if user_id in self.strikes:
            strike_count = len(self.strikes[user_id])
            del self.strikes[user_id]
            
            # Remove from leaderboard
            if user_id in self.leaderboard:
                del self.leaderboard[user_id]
            
            self.save_data()
            await ctx.send(f"✅ Cleared {strike_count} strikes for {member.mention}")
        else:
            await ctx.send(f"{member.mention} has no strikes to clear.")

async def setup(bot):
    await bot.add_cog(StrikeLeaderboard(bot))
