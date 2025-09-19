import discord
from discord.ext import commands, tasks
import json
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Optional, Union
import os

class BehaviorScoring(commands.Cog):
    """User behavior scoring system with trust points and automatic restrictions"""
    
    def __init__(self, bot):
        self.bot = bot
        self.scores_file = "data/behavior_scores.json"
        self.config_file = "data/behavior_config.json"
        self.scores = self._load_scores()
        self.config = self._load_config()
        self.score_decay.start()  # Start the score decay task
        
    def _load_scores(self) -> Dict:
        """Load behavior scores from JSON file"""
        if os.path.exists(self.scores_file):
            try:
                with open(self.scores_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                pass
        return {}
    
    def _save_scores(self):
        """Save behavior scores to JSON file"""
        os.makedirs(os.path.dirname(self.scores_file), exist_ok=True)
        with open(self.scores_file, 'w') as f:
            json.dump(self.scores, f, indent=2)
    
    def _load_config(self) -> Dict:
        """Load behavior system configuration"""
        default_config = {
            "default_score": 100,
            "max_score": 1000,
            "min_score": -500,
            "score_thresholds": {
                "excellent": 800,
                "good": 500,
                "neutral": 100,
                "warning": 50,
                "restricted": 0,
                "severe": -100
            },
            "restrictions": {
                "warning": {
                    "slowmode_multiplier": 2,
                    "extra_verification": True
                },
                "restricted": {
                    "slowmode_multiplier": 5,
                    "extra_verification": True,
                    "limited_reactions": True
                },
                "severe": {
                    "auto_mute": True,
                    "auto_mute_duration": 3600,  # 1 hour
                    "manual_review_required": True
                }
            },
            "score_actions": {
                "message_sent": 1,
                "helpful_reaction": 5,
                "voice_activity": 2,
                "created_thread": 10,
                "event_participation": 15,
                "report_spam": 20,
                "warn_received": -50,
                "timeout_received": -100,
                "kick_received": -200,
                "ban_received": -500,
                "spam_detected": -75,
                "scam_attempt": -300,
                "raid_participation": -400
            },
            "decay": {
                "enabled": True,
                "interval_hours": 24,
                "amount": 1,
                "min_for_decay": 200
            }
        }
        
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    loaded_config = json.load(f)
                    # Merge with defaults to ensure all keys exist
                    for key, value in default_config.items():
                        if key not in loaded_config:
                            loaded_config[key] = value
                    return loaded_config
            except (json.JSONDecodeError, FileNotFoundError):
                pass
        
        # Save default config
        os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
        with open(self.config_file, 'w') as f:
            json.dump(default_config, f, indent=2)
        
        return default_config
    
    def get_user_score(self, user_id: int, guild_id: int) -> int:
        """Get user's behavior score"""
        guild_key = str(guild_id)
        user_key = str(user_id)
        
        if guild_key not in self.scores:
            self.scores[guild_key] = {}
        
        if user_key not in self.scores[guild_key]:
            self.scores[guild_key][user_key] = {
                "score": self.config["default_score"],
                "last_activity": datetime.now().isoformat(),
                "history": []
            }
            self._save_scores()
        
        return self.scores[guild_key][user_key]["score"]
    
    def modify_score(self, user_id: int, guild_id: int, change: int, reason: str, moderator: Optional[discord.Member] = None):
        """Modify user's behavior score"""
        guild_key = str(guild_id)
        user_key = str(user_id)
        
        if guild_key not in self.scores:
            self.scores[guild_key] = {}
        
        if user_key not in self.scores[guild_key]:
            self.scores[guild_key][user_key] = {
                "score": self.config["default_score"],
                "last_activity": datetime.now().isoformat(),
                "history": []
            }
        
        user_data = self.scores[guild_key][user_key]
        old_score = user_data["score"]
        new_score = max(self.config["min_score"], min(self.config["max_score"], old_score + change))
        
        user_data["score"] = new_score
        user_data["last_activity"] = datetime.now().isoformat()
        user_data["history"].append({
            "timestamp": datetime.now().isoformat(),
            "change": change,
            "reason": reason,
            "moderator": moderator.id if moderator else None,
            "old_score": old_score,
            "new_score": new_score
        })
        
        # Keep only last 50 history entries
        if len(user_data["history"]) > 50:
            user_data["history"] = user_data["history"][-50:]
        
        self._save_scores()
        return old_score, new_score
    
    def get_score_tier(self, score: int) -> str:
        """Get the tier name for a score"""
        thresholds = self.config["score_thresholds"]
        
        if score >= thresholds["excellent"]:
            return "excellent"
        elif score >= thresholds["good"]:
            return "good"
        elif score >= thresholds["neutral"]:
            return "neutral"
        elif score >= thresholds["warning"]:
            return "warning"
        elif score >= thresholds["restricted"]:
            return "restricted"
        else:
            return "severe"
    
    def get_tier_color(self, tier: str) -> int:
        """Get color for tier"""
        colors = {
            "excellent": 0x00ff00,
            "good": 0x90EE90,
            "neutral": 0xFFFFFF,
            "warning": 0xFFA500,
            "restricted": 0xFF6347,
            "severe": 0xFF0000
        }
        return colors.get(tier, 0xFFFFFF)
    
    async def apply_restrictions(self, member: discord.Member, tier: str):
        """Apply automatic restrictions based on score tier"""
        if tier not in self.config["restrictions"]:
            return
        
        restrictions = self.config["restrictions"][tier]
        
        # Auto-mute for severe cases
        if restrictions.get("auto_mute") and not member.is_timed_out():
            try:
                duration = restrictions.get("auto_mute_duration", 3600)
                until = datetime.now() + timedelta(seconds=duration)
                await member.timeout(until, reason="Automatic restriction due to low behavior score")
                
                # Log the action
                logging_cog = self.bot.get_cog('LoggingSystem')
                if logging_cog:
                    await logging_cog.log_system_event(
                        "auto_restriction", 
                        f"User automatically muted due to severe behavior score (tier: {tier})",
                        member.guild,
                        self.bot.user,
                        f"Duration: {duration} seconds"
                    )
            except discord.Forbidden:
                pass
    
    @tasks.loop(hours=24)
    async def score_decay(self):
        """Periodic score decay for inactive users"""
        if not self.config["decay"]["enabled"]:
            return
        
        decay_amount = self.config["decay"]["amount"]
        min_for_decay = self.config["decay"]["min_for_decay"]
        cutoff_time = datetime.now() - timedelta(hours=self.config["decay"]["interval_hours"])
        
        for guild_id, guild_data in self.scores.items():
            for user_id, user_data in guild_data.items():
                last_activity = datetime.fromisoformat(user_data["last_activity"])
                current_score = user_data["score"]
                
                # Only decay scores above minimum threshold and for inactive users
                if last_activity < cutoff_time and current_score > min_for_decay:
                    new_score = max(min_for_decay, current_score - decay_amount)
                    if new_score != current_score:
                        user_data["score"] = new_score
                        user_data["history"].append({
                            "timestamp": datetime.now().isoformat(),
                            "change": new_score - current_score,
                            "reason": "Automatic decay due to inactivity",
                            "moderator": None,
                            "old_score": current_score,
                            "new_score": new_score
                        })
        
        self._save_scores()
    
    @score_decay.before_loop
    async def before_score_decay(self):
        """Wait until bot is ready before starting score decay"""
        await self.bot.wait_until_ready()
    
    # Event listeners for automatic scoring
    @commands.Cog.listener()
    async def on_message(self, message):
        """Award points for messages (with spam protection)"""
        if message.author.bot or not message.guild:
            return
        
        # Check admin bypass
        admin_bypass = self.bot.get_cog('AdminBypass')
        if admin_bypass and admin_bypass.is_admin_or_owner(message.author):
            return
        
        # Basic anti-spam: limit points per minute
        user_id = message.author.id
        guild_id = message.guild.id
        
        # Award points for meaningful messages (not too short)
        if len(message.content.strip()) >= 10:
            self.modify_score(user_id, guild_id, self.config["score_actions"]["message_sent"], "Message sent")
    
    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        """Award points for helpful reactions"""
        if user.bot or not reaction.message.guild:
            return
        
        # Check admin bypass
        admin_bypass = self.bot.get_cog('AdminBypass')
        if admin_bypass and admin_bypass.is_admin_or_owner(user):
            return
        
        # Award points for helpful reactions
        helpful_emojis = ['👍', '❤️', '🔥', '👏', '💯', '✅']
        if str(reaction.emoji) in helpful_emojis:
            self.modify_score(user.id, reaction.message.guild.id, 
                            self.config["score_actions"]["helpful_reaction"], 
                            f"Helpful reaction: {reaction.emoji}")
    
    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        """Award points for voice activity"""
        if member.bot or not member.guild:
            return
        
        # Check admin bypass
        admin_bypass = self.bot.get_cog('AdminBypass')
        if admin_bypass and admin_bypass.is_admin_or_owner(member):
            return
        
        # Award points for joining voice channels
        if before.channel is None and after.channel is not None:
            self.modify_score(member.id, member.guild.id, 
                            self.config["score_actions"]["voice_activity"], 
                            "Joined voice channel")
    
    # Commands for managing behavior scores
    @commands.group(name="behavior", aliases=["score"], invoke_without_command=True)
    async def behavior(self, ctx, member: discord.Member = None):
        """View behavior score for a user"""
        target = member or ctx.author
        score = self.get_user_score(target.id, ctx.guild.id)
        tier = self.get_score_tier(score)
        
        embed = discord.Embed(
            title=f"Behavior Score - {target.display_name}",
            color=self.get_tier_color(tier)
        )
        
        embed.add_field(name="Score", value=f"{score}/{self.config['max_score']}", inline=True)
        embed.add_field(name="Tier", value=tier.title(), inline=True)
        embed.add_field(name="Status", value=self._get_tier_description(tier), inline=False)
        
        # Add score breakdown
        thresholds = self.config["score_thresholds"]
        breakdown = []
        for tier_name, threshold in sorted(thresholds.items(), key=lambda x: x[1], reverse=True):
            status = "✅" if score >= threshold else "❌"
            breakdown.append(f"{status} {tier_name.title()}: {threshold}+")
        
        embed.add_field(name="Tier Breakdown", value="\n".join(breakdown), inline=False)
        embed.set_footer(text=f"ID: {target.id}")
        
        await ctx.send(embed=embed)
    
    def _get_tier_description(self, tier: str) -> str:
        """Get description for tier"""
        descriptions = {
            "excellent": "🌟 Exemplary community member with full privileges",
            "good": "✅ Trusted member with standard access",
            "neutral": "📊 Standard member status",
            "warning": "⚠️ Under watch - some restrictions may apply",
            "restricted": "🚫 Limited access due to negative behavior",
            "severe": "💀 Severe restrictions - manual review required"
        }
        return descriptions.get(tier, "Unknown status")
    
    @behavior.command(name="history")
    @commands.has_permissions(moderate_members=True)
    async def behavior_history(self, ctx, member: discord.Member = None):
        """View behavior score history for a user"""
        target = member or ctx.author
        guild_key = str(ctx.guild.id)
        user_key = str(target.id)
        
        if guild_key not in self.scores or user_key not in self.scores[guild_key]:
            await ctx.send(f"{target.display_name} has no behavior history.")
            return
        
        history = self.scores[guild_key][user_key]["history"]
        if not history:
            await ctx.send(f"{target.display_name} has no recorded behavior changes.")
            return
        
        # Show last 10 entries
        recent_history = history[-10:]
        
        embed = discord.Embed(
            title=f"Behavior History - {target.display_name}",
            color=discord.Color.blue()
        )
        
        for entry in recent_history:
            timestamp = datetime.fromisoformat(entry["timestamp"])
            moderator = ""
            if entry["moderator"]:
                try:
                    mod = await self.bot.fetch_user(entry["moderator"])
                    moderator = f" (by {mod.display_name})"
                except:
                    moderator = f" (by {entry['moderator']})"
            
            change_text = f"+{entry['change']}" if entry['change'] > 0 else str(entry['change'])
            embed.add_field(
                name=f"{timestamp.strftime('%Y-%m-%d %H:%M')} - {change_text}",
                value=f"{entry['reason']}{moderator}\n{entry['old_score']} → {entry['new_score']}",
                inline=False
            )
        
        embed.set_footer(text=f"Showing last {len(recent_history)} entries")
        await ctx.send(embed=embed)
    
    @behavior.command(name="modify")
    @commands.has_permissions(moderate_members=True)
    async def behavior_modify(self, ctx, member: discord.Member, change: int, *, reason: str):
        """Manually modify a user's behavior score"""
        # Check admin bypass
        admin_bypass = self.bot.get_cog('AdminBypass')
        if admin_bypass and admin_bypass.is_admin_or_owner(member):
            await ctx.send("❌ Cannot modify behavior score for administrators or owners!")
            return
        
        if abs(change) > 200:
            await ctx.send("❌ Score change cannot exceed ±200 points!")
            return
        
        old_score, new_score = self.modify_score(member.id, ctx.guild.id, change, 
                                               f"Manual adjustment: {reason}", ctx.author)
        
        old_tier = self.get_score_tier(old_score)
        new_tier = self.get_score_tier(new_score)
        
        embed = discord.Embed(
            title="Behavior Score Modified",
            color=self.get_tier_color(new_tier)
        )
        
        embed.add_field(name="User", value=member.display_name, inline=True)
        embed.add_field(name="Change", value=f"{'+' if change > 0 else ''}{change}", inline=True)
        embed.add_field(name="New Score", value=f"{new_score}", inline=True)
        embed.add_field(name="Tier Change", value=f"{old_tier.title()} → {new_tier.title()}", inline=False)
        embed.add_field(name="Reason", value=reason, inline=False)
        embed.add_field(name="Moderator", value=ctx.author.display_name, inline=True)
        
        await ctx.send(embed=embed)
        
        # Apply restrictions if tier changed to restricted
        if new_tier in ["warning", "restricted", "severe"] and old_tier not in ["warning", "restricted", "severe"]:
            await self.apply_restrictions(member, new_tier)
        
        # Log the action
        logging_cog = self.bot.get_cog('LoggingSystem')
        if logging_cog:
            await logging_cog.log_action("behavior_modify", ctx.author, member, reason, 
                                       f"Score: {old_score} → {new_score} ({'+' if change > 0 else ''}{change})", 
                                       guild=ctx.guild)
    
    @behavior.command(name="leaderboard", aliases=["top"])
    async def behavior_leaderboard(self, ctx):
        """Show top behavior scores in the server"""
        guild_key = str(ctx.guild.id)
        
        if guild_key not in self.scores:
            await ctx.send("No behavior scores recorded yet!")
            return
        
        # Get all users and their scores
        user_scores = []
        for user_id, user_data in self.scores[guild_key].items():
            try:
                member = ctx.guild.get_member(int(user_id))
                if member:  # Only include current members
                    user_scores.append((member, user_data["score"]))
            except:
                continue
        
        if not user_scores:
            await ctx.send("No behavior scores found for current members!")
            return
        
        # Sort by score (highest first)
        user_scores.sort(key=lambda x: x[1], reverse=True)
        
        embed = discord.Embed(
            title="🏆 Behavior Score Leaderboard",
            color=discord.Color.gold()
        )
        
        # Show top 10
        top_users = user_scores[:10]
        leaderboard_text = []
        
        for i, (member, score) in enumerate(top_users, 1):
            tier = self.get_score_tier(score)
            tier_emoji = {
                "excellent": "🌟",
                "good": "✅",
                "neutral": "📊",
                "warning": "⚠️",
                "restricted": "🚫",
                "severe": "💀"
            }.get(tier, "❓")
            
            leaderboard_text.append(f"{i}. {tier_emoji} **{member.display_name}** - {score}")
        
        embed.description = "\n".join(leaderboard_text)
        embed.set_footer(text=f"Showing top {len(top_users)} members")
        
        await ctx.send(embed=embed)
    
    @behavior.command(name="config")
    @commands.has_permissions(administrator=True)
    async def behavior_config(self, ctx):
        """Show current behavior system configuration"""
        embed = discord.Embed(
            title="Behavior System Configuration",
            color=discord.Color.blue()
        )
        
        # Score thresholds
        thresholds = self.config["score_thresholds"]
        threshold_text = []
        for tier, score in sorted(thresholds.items(), key=lambda x: x[1], reverse=True):
            threshold_text.append(f"**{tier.title()}**: {score}+")
        
        embed.add_field(name="Score Thresholds", value="\n".join(threshold_text), inline=True)
        
        # Score actions
        actions = self.config["score_actions"]
        positive_actions = [f"**{k.replace('_', ' ').title()}**: +{v}" for k, v in actions.items() if v > 0]
        negative_actions = [f"**{k.replace('_', ' ').title()}**: {v}" for k, v in actions.items() if v < 0]
        
        if positive_actions:
            embed.add_field(name="Positive Actions", value="\n".join(positive_actions[:5]), inline=True)
        if negative_actions:
            embed.add_field(name="Negative Actions", value="\n".join(negative_actions[:5]), inline=True)
        
        # General settings
        embed.add_field(name="Score Range", 
                       value=f"{self.config['min_score']} to {self.config['max_score']}", 
                       inline=True)
        embed.add_field(name="Default Score", 
                       value=str(self.config['default_score']), 
                       inline=True)
        
        decay_status = "Enabled" if self.config["decay"]["enabled"] else "Disabled"
        embed.add_field(name="Score Decay", value=decay_status, inline=True)
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(BehaviorScoring(bot))
