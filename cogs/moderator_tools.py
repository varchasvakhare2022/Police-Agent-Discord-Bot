import discord
from discord.ext import commands
import json
import os
from datetime import datetime, timedelta
import asyncio

class ModeratorTools(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.user_data_file = 'data/user_data.json'
        self.moderation_log_file = 'data/moderation_log.json'
        self.notes_file = 'data/notes.json'
        
        # Ensure data directory exists
        os.makedirs('data', exist_ok=True)
        
        # Load data
        self.load_data()
    
    def load_data(self):
        """Load user data, moderation logs, and notes from JSON files"""
        # Load user data
        if os.path.exists(self.user_data_file):
            try:
                with open(self.user_data_file, 'r') as f:
                    self.user_data = json.load(f)
            except:
                self.user_data = {}
        else:
            self.user_data = {}
        
        # Load moderation logs
        if os.path.exists(self.moderation_log_file):
            try:
                with open(self.moderation_log_file, 'r') as f:
                    self.moderation_log = json.load(f)
            except:
                self.moderation_log = {}
        else:
            self.moderation_log = {}
        
        # Load notes
        if os.path.exists(self.notes_file):
            try:
                with open(self.notes_file, 'r') as f:
                    self.notes = json.load(f)
            except:
                self.notes = {}
        else:
            self.notes = {}
    
    def save_data(self):
        """Save all data to JSON files"""
        with open(self.user_data_file, 'w') as f:
            json.dump(self.user_data, f, indent=2)
        
        with open(self.moderation_log_file, 'w') as f:
            json.dump(self.moderation_log, f, indent=2)
        
        with open(self.notes_file, 'w') as f:
            json.dump(self.notes, f, indent=2)
    
    def get_user_data(self, user_id):
        """Get or create user data"""
        user_id = str(user_id)
        if user_id not in self.user_data:
            self.user_data[user_id] = {
                'account_created': None,
                'server_joined': None,
                'punishments': [],
                'warnings': [],
                'notes': [],
                'last_seen': None
            }
        return self.user_data[user_id]
    
    def log_moderation_action(self, action_type, user_id, moderator_id, reason, details=None):
        """Log moderation action"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'action_type': action_type,
            'user_id': str(user_id),
            'moderator_id': str(moderator_id),
            'reason': reason,
            'details': details or {}
        }
        
        # Add to moderation log
        if 'moderation_log' not in self.moderation_log:
            self.moderation_log['moderation_log'] = []
        
        self.moderation_log['moderation_log'].append(log_entry)
        
        # Add to user's data
        user_data = self.get_user_data(user_id)
        user_data['punishments'].append(log_entry)
        
        self.save_data()
    
    def add_note(self, user_id, moderator_id, note):
        """Add private note to user"""
        user_id = str(user_id)
        note_entry = {
            'timestamp': datetime.now().isoformat(),
            'moderator_id': str(moderator_id),
            'note': note
        }
        
        user_data = self.get_user_data(user_id)
        user_data['notes'].append(note_entry)
        
        # Also add to notes file for easy access
        if user_id not in self.notes:
            self.notes[user_id] = []
        self.notes[user_id].append(note_entry)
        
        self.save_data()
    
    def calculate_account_age(self, user):
        """Calculate account age"""
        if not user.created_at:
            return "Unknown"
        
        age = datetime.now() - user.created_at
        years = age.days // 365
        days = age.days % 365
        
        if years > 0:
            return f"{years} year{'s' if years != 1 else ''}, {days} day{'s' if days != 1 else ''}"
        else:
            return f"{days} day{'s' if days != 1 else ''}"
    
    def get_join_date(self, member):
        """Get server join date"""
        if not member.joined_at:
            return "Unknown"
        
        return member.joined_at.strftime("%Y-%m-%d %H:%M:%S")
    
    def get_user_status(self, user):
        """Get user status"""
        if user.status == discord.Status.online:
            return "🟢 Online"
        elif user.status == discord.Status.idle:
            return "🟡 Idle"
        elif user.status == discord.Status.dnd:
            return "🔴 Do Not Disturb"
        elif user.status == discord.Status.offline:
            return "⚫ Offline"
        else:
            return "❓ Unknown"
    
    @commands.command(name='whois')
    @commands.has_permissions(manage_messages=True)
    async def whois_command(self, ctx, member: discord.Member):
        """Get comprehensive user information"""
        user_data = self.get_user_data(member.id)
        
        # Create embed
        embed = discord.Embed(
            title=f"👤 User Information: {member.display_name}",
            color=member.color if member.color != discord.Color.default() else 0x0099ff,
            timestamp=datetime.now()
        )
        
        # Basic info
        embed.add_field(
            name="📋 Basic Information",
            value=f"**Username:** {member.name}\n"
                  f"**Display Name:** {member.display_name}\n"
                  f"**ID:** `{member.id}`\n"
                  f"**Status:** {self.get_user_status(member)}",
            inline=False
        )
        
        # Account info
        embed.add_field(
            name="📅 Account Information",
            value=f"**Account Created:** {member.created_at.strftime('%Y-%m-%d %H:%M:%S')}\n"
                  f"**Account Age:** {self.calculate_account_age(member)}\n"
                  f"**Server Joined:** {self.get_join_date(member)}",
            inline=False
        )
        
        # Roles
        roles = [role.mention for role in member.roles[1:]]  # Exclude @everyone
        roles_text = ", ".join(roles) if roles else "No roles"
        embed.add_field(
            name="🎭 Roles",
            value=roles_text,
            inline=False
        )
        
        # Punishments
        punishment_count = len(user_data['punishments'])
        embed.add_field(
            name="⚠️ Punishments",
            value=f"**Total:** {punishment_count}",
            inline=True
        )
        
        # Warnings
        warning_count = len(user_data['warnings'])
        embed.add_field(
            name="🚨 Warnings",
            value=f"**Total:** {warning_count}",
            inline=True
        )
        
        # Notes
        note_count = len(user_data['notes'])
        embed.add_field(
            name="📝 Notes",
            value=f"**Total:** {note_count}",
            inline=True
        )
        
        # Recent activity
        if user_data['punishments']:
            recent_punishment = user_data['punishments'][-1]
            embed.add_field(
                name="🔍 Recent Punishment",
                value=f"**Type:** {recent_punishment['action_type']}\n"
                      f"**Reason:** {recent_punishment['reason']}\n"
                      f"**Date:** {datetime.fromisoformat(recent_punishment['timestamp']).strftime('%Y-%m-%d %H:%M')}",
                inline=False
            )
        
        # Set thumbnail
        embed.set_thumbnail(url=member.display_avatar.url)
        
        # Footer
        embed.set_footer(text=f"Requested by {ctx.author.display_name}")
        
        await ctx.send(embed=embed)
    
    @commands.command(name='history')
    @commands.has_permissions(manage_messages=True)
    async def history_command(self, ctx, member: discord.Member):
        """Get moderation history for a user"""
        user_data = self.get_user_data(member.id)
        
        if not user_data['punishments']:
            await ctx.send(f"{member.mention} has no moderation history.")
            return
        
        # Create embed
        embed = discord.Embed(
            title=f"📜 Moderation History: {member.display_name}",
            color=0xff6b6b,
            timestamp=datetime.now()
        )
        
        # Show last 10 punishments
        recent_punishments = user_data['punishments'][-10:]
        
        for i, punishment in enumerate(reversed(recent_punishments), 1):
            moderator = self.bot.get_user(int(punishment['moderator_id']))
            moderator_name = moderator.display_name if moderator else "Unknown"
            
            embed.add_field(
                name=f"#{len(user_data['punishments']) - len(recent_punishments) + i} - {punishment['action_type'].title()}",
                value=f"**Moderator:** {moderator_name}\n"
                      f"**Reason:** {punishment['reason']}\n"
                      f"**Date:** {datetime.fromisoformat(punishment['timestamp']).strftime('%Y-%m-%d %H:%M')}",
                inline=False
            )
        
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.set_footer(text=f"Showing last {len(recent_punishments)} of {len(user_data['punishments'])} total punishments")
        
        await ctx.send(embed=embed)
    
    @commands.command(name='note')
    @commands.has_permissions(manage_messages=True)
    async def note_command(self, ctx, member: discord.Member, *, note: str):
        """Add a private note to a user"""
        self.add_note(member.id, ctx.author.id, note)
        
        embed = discord.Embed(
            title="📝 Note Added",
            description=f"Private note added to {member.mention}",
            color=0x00ff00,
            timestamp=datetime.now()
        )
        embed.add_field(name="Note", value=note, inline=False)
        embed.add_field(name="Moderator", value=ctx.author.mention, inline=True)
        embed.add_field(name="User", value=member.mention, inline=True)
        
        await ctx.send(embed=embed)
    
    @commands.command(name='notes')
    @commands.has_permissions(manage_messages=True)
    async def notes_command(self, ctx, member: discord.Member):
        """View private notes for a user"""
        user_data = self.get_user_data(member.id)
        
        if not user_data['notes']:
            await ctx.send(f"No notes found for {member.mention}.")
            return
        
        embed = discord.Embed(
            title=f"📝 Private Notes: {member.display_name}",
            color=0xffff00,
            timestamp=datetime.now()
        )
        
        # Show last 5 notes
        recent_notes = user_data['notes'][-5:]
        
        for i, note in enumerate(reversed(recent_notes), 1):
            moderator = self.bot.get_user(int(note['moderator_id']))
            moderator_name = moderator.display_name if moderator else "Unknown"
            
            embed.add_field(
                name=f"Note #{len(user_data['notes']) - len(recent_notes) + i}",
                value=f"**Moderator:** {moderator_name}\n"
                      f"**Note:** {note['note']}\n"
                      f"**Date:** {datetime.fromisoformat(note['timestamp']).strftime('%Y-%m-%d %H:%M')}",
                inline=False
            )
        
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.set_footer(text=f"Showing last {len(recent_notes)} of {len(user_data['notes'])} total notes")
        
        await ctx.send(embed=embed)
    
    @commands.command(name='modlog')
    @commands.has_permissions(manage_messages=True)
    async def modlog_command(self, ctx, limit: int = 10):
        """View recent moderation actions"""
        if 'moderation_log' not in self.moderation_log or not self.moderation_log['moderation_log']:
            await ctx.send("No moderation actions found.")
            return
        
        # Get recent actions
        recent_actions = self.moderation_log['moderation_log'][-limit:]
        
        embed = discord.Embed(
            title="📋 Recent Moderation Actions",
            color=0x0099ff,
            timestamp=datetime.now()
        )
        
        for i, action in enumerate(reversed(recent_actions), 1):
            user = self.bot.get_user(int(action['user_id']))
            moderator = self.bot.get_user(int(action['moderator_id']))
            
            user_name = user.display_name if user else "Unknown"
            moderator_name = moderator.display_name if moderator else "Unknown"
            
            embed.add_field(
                name=f"#{len(self.moderation_log['moderation_log']) - len(recent_actions) + i} - {action['action_type'].title()}",
                value=f"**User:** {user_name}\n"
                      f"**Moderator:** {moderator_name}\n"
                      f"**Reason:** {action['reason']}\n"
                      f"**Date:** {datetime.fromisoformat(action['timestamp']).strftime('%Y-%m-%d %H:%M')}",
                inline=False
            )
        
        embed.set_footer(text=f"Showing last {len(recent_actions)} of {len(self.moderation_log['moderation_log'])} total actions")
        
        await ctx.send(embed=embed)
    
    @commands.command(name='clear_notes')
    @commands.has_permissions(administrator=True)
    async def clear_notes_command(self, ctx, member: discord.Member):
        """Clear all notes for a user (admin only)"""
        user_id = str(member.id)
        
        if user_id in self.notes:
            note_count = len(self.notes[user_id])
            del self.notes[user_id]
            
            # Also clear from user data
            user_data = self.get_user_data(member.id)
            user_data['notes'] = []
            
            self.save_data()
            await ctx.send(f"✅ Cleared {note_count} notes for {member.mention}")
        else:
            await ctx.send(f"{member.mention} has no notes to clear.")

async def setup(bot):
    await bot.add_cog(ModeratorTools(bot))
