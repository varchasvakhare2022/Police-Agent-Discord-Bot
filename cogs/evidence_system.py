import discord
from discord.ext import commands
import json
import os
import uuid
from datetime import datetime
import asyncio

class EvidenceSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.evidence_file = 'data/evidence.json'
        self.warnings_file = 'data/warnings.json'
        self.cases_file = 'data/cases.json'
        
        # Ensure data directory exists
        os.makedirs('data', exist_ok=True)
        
        # Load existing data
        self.load_data()
    
    def load_data(self):
        """Load evidence, warnings, and cases from JSON files"""
        # Load evidence
        if os.path.exists(self.evidence_file):
            try:
                with open(self.evidence_file, 'r') as f:
                    self.evidence = json.load(f)
            except:
                self.evidence = {}
        else:
            self.evidence = {}
        
        # Load warnings
        if os.path.exists(self.warnings_file):
            try:
                with open(self.warnings_file, 'r') as f:
                    self.warnings = json.load(f)
            except:
                self.warnings = {}
        else:
            self.warnings = {}
        
        # Load cases
        if os.path.exists(self.cases_file):
            try:
                with open(self.cases_file, 'r') as f:
                    self.cases = json.load(f)
            except:
                self.cases = {}
        else:
            self.cases = {}
    
    def save_data(self):
        """Save all data to JSON files"""
        with open(self.evidence_file, 'w') as f:
            json.dump(self.evidence, f, indent=2)
        
        with open(self.warnings_file, 'w') as f:
            json.dump(self.warnings, f, indent=2)
        
        with open(self.cases_file, 'w') as f:
            json.dump(self.cases, f, indent=2)
    
    def generate_case_id(self):
        """Generate unique case ID"""
        return str(uuid.uuid4())[:8].upper()
    
    def store_evidence(self, case_id, action_type, user_id, moderator_id, reason, evidence_data=None):
        """Store evidence for a case"""
        if case_id not in self.evidence:
            self.evidence[case_id] = []
        
        evidence_entry = {
            'timestamp': datetime.now().isoformat(),
            'action_type': action_type,
            'user_id': str(user_id),
            'moderator_id': str(moderator_id),
            'reason': reason,
            'evidence_data': evidence_data or {}
        }
        
        self.evidence[case_id].append(evidence_entry)
        self.save_data()
    
    def store_warning(self, user_id, moderator_id, reason, case_id=None):
        """Store warning in user's record"""
        user_id = str(user_id)
        
        if user_id not in self.warnings:
            self.warnings[user_id] = []
        
        warning_entry = {
            'warning_id': self.generate_case_id(),
            'timestamp': datetime.now().isoformat(),
            'moderator_id': str(moderator_id),
            'reason': reason,
            'case_id': case_id
        }
        
        self.warnings[user_id].append(warning_entry)
        self.save_data()
        
        return warning_entry['warning_id']
    
    def create_case(self, case_id, user_id, moderator_id, action_type, reason):
        """Create a new case"""
        self.cases[case_id] = {
            'user_id': str(user_id),
            'moderator_id': str(moderator_id),
            'action_type': action_type,
            'reason': reason,
            'created_at': datetime.now().isoformat(),
            'evidence': []
        }
        self.save_data()
    
    @commands.command(name='warn')
    @commands.has_permissions(manage_messages=True)
    async def warn_user(self, ctx, member: discord.Member, *, reason: str):
        """Warn a user and store evidence"""
        case_id = self.generate_case_id()
        
        # Create case
        self.create_case(case_id, member.id, ctx.author.id, 'warning', reason)
        
        # Store warning
        warning_id = self.store_warning(member.id, ctx.author.id, reason, case_id)
        
        # Store evidence
        self.store_evidence(case_id, 'warning', member.id, ctx.author.id, reason)
        
        # Create embed
        embed = discord.Embed(
            title="⚠️ Warning Issued",
            color=0xffaa00,
            timestamp=datetime.now()
        )
        embed.add_field(name="User", value=member.mention, inline=True)
        embed.add_field(name="Moderator", value=ctx.author.mention, inline=True)
        embed.add_field(name="Reason", value=reason, inline=False)
        embed.add_field(name="Case ID", value=f"`{case_id}`", inline=True)
        embed.add_field(name="Warning ID", value=f"`{warning_id}`", inline=True)
        
        # Send to channel
        await ctx.send(embed=embed)
        
        # Try to DM user
        try:
            dm_embed = discord.Embed(
                title="⚠️ You have been warned",
                description=f"You received a warning in **{ctx.guild.name}**",
                color=0xffaa00,
                timestamp=datetime.now()
            )
            dm_embed.add_field(name="Reason", value=reason, inline=False)
            dm_embed.add_field(name="Moderator", value=ctx.author.display_name, inline=True)
            dm_embed.add_field(name="Case ID", value=f"`{case_id}`", inline=True)
            dm_embed.set_footer(text="Please follow the server rules to avoid further action.")
            
            await member.send(embed=dm_embed)
        except discord.Forbidden:
            await ctx.send(f"⚠️ Could not DM {member.mention} - they may have DMs disabled.")
    
    @commands.command(name='warnings')
    async def view_warnings(self, ctx, member: discord.Member = None):
        """View warnings for a user"""
        member = member or ctx.author
        user_id = str(member.id)
        
        if user_id not in self.warnings or not self.warnings[user_id]:
            await ctx.send(f"{member.mention} has no warnings on record.")
            return
        
        user_warnings = self.warnings[user_id]
        
        embed = discord.Embed(
            title=f"⚠️ Warnings for {member.display_name}",
            color=0xffaa00,
            timestamp=datetime.now()
        )
        
        # Show last 5 warnings
        recent_warnings = user_warnings[-5:]
        
        for i, warning in enumerate(recent_warnings, 1):
            moderator = self.bot.get_user(int(warning['moderator_id']))
            moderator_name = moderator.display_name if moderator else "Unknown"
            
            embed.add_field(
                name=f"Warning #{len(user_warnings) - len(recent_warnings) + i}",
                value=f"**Reason:** {warning['reason']}\n"
                      f"**Moderator:** {moderator_name}\n"
                      f"**Date:** {datetime.fromisoformat(warning['timestamp']).strftime('%Y-%m-%d %H:%M')}\n"
                      f"**ID:** `{warning['warning_id']}`",
                inline=False
            )
        
        embed.set_footer(text=f"Total warnings: {len(user_warnings)}")
        await ctx.send(embed=embed)
    
    @commands.command(name='case')
    async def view_case(self, ctx, case_id: str):
        """View evidence for a specific case"""
        case_id = case_id.upper()
        
        if case_id not in self.cases:
            await ctx.send(f"❌ Case `{case_id}` not found.")
            return
        
        case = self.cases[case_id]
        user = self.bot.get_user(int(case['user_id']))
        moderator = self.bot.get_user(int(case['moderator_id']))
        
        embed = discord.Embed(
            title=f"📋 Case #{case_id}",
            color=0x0099ff,
            timestamp=datetime.fromisoformat(case['created_at'])
        )
        
        embed.add_field(name="User", value=user.mention if user else "Unknown", inline=True)
        embed.add_field(name="Moderator", value=moderator.mention if moderator else "Unknown", inline=True)
        embed.add_field(name="Action", value=case['action_type'].title(), inline=True)
        embed.add_field(name="Reason", value=case['reason'], inline=False)
        
        # Show evidence if available
        if case_id in self.evidence:
            evidence_count = len(self.evidence[case_id])
            embed.add_field(name="Evidence Entries", value=str(evidence_count), inline=True)
        
        await ctx.send(embed=embed)
    
    @commands.command(name='evidence')
    @commands.has_permissions(manage_messages=True)
    async def add_evidence(self, ctx, case_id: str, *, evidence: str):
        """Add evidence to a case"""
        case_id = case_id.upper()
        
        if case_id not in self.cases:
            await ctx.send(f"❌ Case `{case_id}` not found.")
            return
        
        # Store evidence
        self.store_evidence(case_id, 'evidence_added', ctx.author.id, ctx.author.id, evidence)
        
        await ctx.send(f"✅ Evidence added to case `{case_id}`")
    
    @commands.command(name='cases')
    @commands.has_permissions(manage_messages=True)
    async def list_cases(self, ctx, user: discord.Member = None):
        """List cases for a user or all recent cases"""
        if user:
            user_cases = [case_id for case_id, case in self.cases.items() 
                         if case['user_id'] == str(user.id)]
            
            if not user_cases:
                await ctx.send(f"{user.mention} has no cases on record.")
                return
            
            embed = discord.Embed(
                title=f"📋 Cases for {user.display_name}",
                color=0x0099ff
            )
            
            for case_id in user_cases[-10:]:  # Show last 10 cases
                case = self.cases[case_id]
                embed.add_field(
                    name=f"Case #{case_id}",
                    value=f"**Action:** {case['action_type']}\n"
                          f"**Reason:** {case['reason'][:50]}...\n"
                          f"**Date:** {datetime.fromisoformat(case['created_at']).strftime('%Y-%m-%d')}",
                    inline=True
                )
        else:
            # Show all recent cases
            recent_cases = sorted(self.cases.items(), 
                                key=lambda x: x[1]['created_at'], 
                                reverse=True)[:10]
            
            if not recent_cases:
                await ctx.send("No cases found.")
                return
            
            embed = discord.Embed(
                title="📋 Recent Cases",
                color=0x0099ff
            )
            
            for case_id, case in recent_cases:
                user = self.bot.get_user(int(case['user_id']))
                embed.add_field(
                    name=f"Case #{case_id}",
                    value=f"**User:** {user.mention if user else 'Unknown'}\n"
                          f"**Action:** {case['action_type']}\n"
                          f"**Date:** {datetime.fromisoformat(case['created_at']).strftime('%Y-%m-%d')}",
                    inline=True
                )
        
        await ctx.send(embed=embed)
    
    @commands.command(name='clear_warnings')
    @commands.has_permissions(administrator=True)
    async def clear_warnings(self, ctx, member: discord.Member):
        """Clear all warnings for a user (admin only)"""
        user_id = str(member.id)
        
        if user_id not in self.warnings:
            await ctx.send(f"{member.mention} has no warnings to clear.")
            return
        
        warning_count = len(self.warnings[user_id])
        del self.warnings[user_id]
        self.save_data()
        
        await ctx.send(f"✅ Cleared {warning_count} warnings for {member.mention}")

async def setup(bot):
    await bot.add_cog(EvidenceSystem(bot))
