import discord
from discord.ext import commands
import json
import os
from datetime import datetime

class WarningSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.warnings_file = 'data/warnings.json'
        self._ensure_warnings_file()
    
    def _ensure_warnings_file(self):
        """Ensure the warnings JSON file exists"""
        os.makedirs('data', exist_ok=True)
        if not os.path.exists(self.warnings_file):
            with open(self.warnings_file, 'w') as f:
                json.dump({}, f)
    
    def load_warnings(self):
        """Load warnings from JSON file"""
        try:
            with open(self.warnings_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    
    def save_warnings(self, warnings_data):
        """Save warnings to JSON file"""
        with open(self.warnings_file, 'w') as f:
            json.dump(warnings_data, f, indent=4)
    
    def add_warning(self, user_id, moderator_id, reason, guild_id):
        """Add a warning for a user"""
        warnings_data = self.load_warnings()
        
        if str(guild_id) not in warnings_data:
            warnings_data[str(guild_id)] = {}
        
        if str(user_id) not in warnings_data[str(guild_id)]:
            warnings_data[str(guild_id)][str(user_id)] = []
        
        warning = {
            'id': len(warnings_data[str(guild_id)][str(user_id)]) + 1,
            'reason': reason,
            'moderator_id': moderator_id,
            'timestamp': datetime.now().isoformat(),
            'guild_id': guild_id
        }
        
        warnings_data[str(guild_id)][str(user_id)].append(warning)
        self.save_warnings(warnings_data)
        
        return warning['id']
    
    def get_user_warnings(self, user_id, guild_id):
        """Get all warnings for a user in a specific guild"""
        warnings_data = self.load_warnings()
        guild_warnings = warnings_data.get(str(guild_id), {})
        return guild_warnings.get(str(user_id), [])
    
    @commands.command(name='warn')
    @commands.has_permissions(manage_messages=True)
    async def warn_user(self, ctx, user: discord.Member, *, reason: str = None):
        """Warn a user and send them a DM notification"""
        if not reason:
            embed = discord.Embed(
                title="❌ Missing Reason",
                description="Please provide a reason for the warning.\n\n**Usage:** `-warn @user reason`",
                color=0xff0000
            )
            await ctx.reply(embed=embed, delete_after=10)
            return
        
        if user.bot:
            embed = discord.Embed(
                title="❌ Cannot Warn Bot",
                description="You cannot warn a bot!",
                color=0xff0000
            )
            await ctx.reply(embed=embed, delete_after=5)
            return
        
        if user == ctx.author:
            embed = discord.Embed(
                title="❌ Cannot Warn Yourself",
                description="You cannot warn yourself!",
                color=0xff0000
            )
            await ctx.reply(embed=embed, delete_after=5)
            return
        
        # Add warning to database
        warning_id = self.add_warning(user.id, ctx.author.id, reason, ctx.guild.id)
        
        # Send DM to user
        try:
            dm_embed = discord.Embed(
                title="⚠️ Warning Received",
                description=f"You have received a warning in **{ctx.guild.name}**",
                color=0xff9900
            )
            dm_embed.add_field(
                name="📝 Reason",
                value=reason,
                inline=False
            )
            dm_embed.add_field(
                name="👮 Moderator",
                value=f"{ctx.author.name}#{ctx.author.discriminator}",
                inline=True
            )
            dm_embed.add_field(
                name="🆔 Warning ID",
                value=f"#{warning_id}",
                inline=True
            )
            dm_embed.set_footer(text="Please follow the server rules to avoid further warnings")
            dm_embed.timestamp = datetime.now()
            
            await user.send(embed=dm_embed)
            dm_sent = True
        except discord.Forbidden:
            dm_sent = False
        
        # Send confirmation to moderator
        embed = discord.Embed(
            title="✅ Warning Issued",
            description=f"Successfully warned {user.mention}",
            color=0x00ff00
        )
        embed.add_field(
            name="📝 Reason",
            value=reason,
            inline=False
        )
        embed.add_field(
            name="🆔 Warning ID",
            value=f"#{warning_id}",
            inline=True
        )
        embed.add_field(
            name="📊 Total Warnings",
            value=f"{len(self.get_user_warnings(user.id, ctx.guild.id))}",
            inline=True
        )
        
        if not dm_sent:
            embed.add_field(
                name="⚠️ Note",
                value="Could not send DM to user (DMs disabled)",
                inline=False
            )
        
        embed.set_footer(text=f"Moderator: {ctx.author.name}")
        embed.timestamp = datetime.now()
        
        await ctx.reply(embed=embed)
    
    @warn_user.error
    async def warn_user_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            embed = discord.Embed(
                title="❌ Permission Denied",
                description="You need **Manage Messages** permission to use this command.",
                color=0xff0000
            )
            await ctx.reply(embed=embed, delete_after=10)
        elif isinstance(error, commands.MissingRequiredArgument):
            embed = discord.Embed(
                title="❌ Missing Arguments",
                description="Please mention a user and provide a reason.\n\n**Usage:** `-warn @user reason`",
                color=0xff0000
            )
            await ctx.reply(embed=embed, delete_after=10)
        elif isinstance(error, commands.BadArgument):
            embed = discord.Embed(
                title="❌ Invalid User",
                description="Please mention a valid user or provide a valid user ID.",
                color=0xff0000
            )
            await ctx.reply(embed=embed, delete_after=10)
    
    @commands.command(name='warnings')
    @commands.has_permissions(manage_messages=True)
    async def view_warnings(self, ctx, user: discord.Member = None):
        """View all warnings for a user"""
        if user is None:
            user = ctx.author
        
        warnings = self.get_user_warnings(user.id, ctx.guild.id)
        
        if not warnings:
            embed = discord.Embed(
                title="📋 Warning History",
                description=f"{user.mention} has no warnings.",
                color=0x00ff00
            )
            embed.set_footer(text="Clean record!")
            await ctx.reply(embed=embed)
            return
        
        embed = discord.Embed(
            title="📋 Warning History",
            description=f"Showing warnings for {user.mention}",
            color=0xff9900
        )
        
        # Discord embed field value limit is 1024 characters
        # We'll split warnings into multiple fields if needed
        warning_text = ""
        field_count = 0
        
        for warning in warnings:
            warning_time = datetime.fromisoformat(warning['timestamp'])
            epoch_timestamp = int(warning_time.timestamp())
            warning_entry = f"**Warning #{warning['id']}**\n📝 {warning['reason']}\n👮 Moderator: <@{warning['moderator_id']}>\n📅 <t:{epoch_timestamp}:F>\n\n"
            
            # Check if adding this warning would exceed the limit
            if len(warning_text + warning_entry) > 1000:  # Leave some buffer
                embed.add_field(
                    name=f"Warnings {field_count * 3 + 1}-{field_count * 3 + len(warning_text.split('**Warning #')) - 1}" if field_count > 0 else "Recent Warnings",
                    value=warning_text,
                    inline=False
                )
                warning_text = warning_entry
                field_count += 1
            else:
                warning_text += warning_entry
        
        # Add the remaining warnings
        if warning_text:
            field_name = f"Warnings {field_count * 3 + 1}-{len(warnings)}" if field_count > 0 else "All Warnings"
            embed.add_field(
                name=field_name,
                value=warning_text,
                inline=False
            )
        
        embed.add_field(
            name="📊 Total Warnings",
            value=str(len(warnings)),
            inline=True
        )
        
        embed.set_footer(text=f"Requested by {ctx.author.name}")
        embed.timestamp = datetime.now()
        
        await ctx.reply(embed=embed)
    
    @view_warnings.error
    async def view_warnings_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            embed = discord.Embed(
                title="❌ Permission Denied",
                description="You need **Manage Messages** permission to use this command.",
                color=0xff0000
            )
            await ctx.reply(embed=embed, delete_after=10)
        elif isinstance(error, commands.BadArgument):
            embed = discord.Embed(
                title="❌ Invalid User",
                description="Please mention a valid user or provide a valid user ID.",
                color=0xff0000
            )
            await ctx.reply(embed=embed, delete_after=10)
    
    @commands.command(name='clearwarnings')
    @commands.has_permissions(manage_messages=True)
    async def clear_warnings(self, ctx, user: discord.Member):
        """Clear all warnings for a user"""
        warnings_data = self.load_warnings()
        
        if str(ctx.guild.id) not in warnings_data:
            warnings_data[str(ctx.guild.id)] = {}
        
        if str(user.id) not in warnings_data[str(ctx.guild.id)]:
            embed = discord.Embed(
                title="📋 No Warnings Found",
                description=f"{user.mention} has no warnings to clear.",
                color=0xff9900
            )
            await ctx.reply(embed=embed, delete_after=10)
            return
        
        # Count warnings before clearing
        warning_count = len(warnings_data[str(ctx.guild.id)][str(user.id)])
        
        # Clear warnings
        warnings_data[str(ctx.guild.id)][str(user.id)] = []
        self.save_warnings(warnings_data)
        
        embed = discord.Embed(
            title="✅ Warnings Cleared",
            description=f"Successfully cleared **{warning_count}** warnings for {user.mention}",
            color=0x00ff00
        )
        embed.set_footer(text=f"Moderator: {ctx.author.name}")
        embed.timestamp = datetime.now()
        
        await ctx.reply(embed=embed)
    
    @clear_warnings.error
    async def clear_warnings_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            embed = discord.Embed(
                title="❌ Permission Denied",
                description="You need **Manage Messages** permission to use this command.",
                color=0xff0000
            )
            await ctx.reply(embed=embed, delete_after=10)
        elif isinstance(error, commands.MissingRequiredArgument):
            embed = discord.Embed(
                title="❌ Missing User",
                description="Please mention a user to clear their warnings.\n\n**Usage:** `-clearwarnings @user`",
                color=0xff0000
            )
            await ctx.reply(embed=embed, delete_after=10)
        elif isinstance(error, commands.BadArgument):
            embed = discord.Embed(
                title="❌ Invalid User",
                description="Please mention a valid user or provide a valid user ID.",
                color=0xff0000
            )
            await ctx.reply(embed=embed, delete_after=10)

async def setup(bot):
    await bot.add_cog(WarningSystem(bot))
