import discord
from discord.ext import commands
import asyncio
import time
from datetime import datetime, timedelta
import inspect

class MassManagement(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="mass-ban")
    @commands.has_permissions(ban_members=True)
    async def mass_ban(self, ctx: commands.Context, *, reason: str = "Mass ban"):
        """Mass ban multiple users (for raids)"""
        
        # Check if user has high enough permissions
        if not ctx.author.guild_permissions.administrator:
            await ctx.reply("❌ This command requires Administrator permissions!")
            return
        
        # Get recent members (joined within last 5 minutes)
        recent_members = []
        for member in ctx.guild.members:
            if member.joined_at and (datetime.now() - member.joined_at).total_seconds() < 300:
                recent_members.append(member)
        
        if not recent_members:
            await ctx.reply("❌ No recent members found to ban!")
            return
        
        # Create confirmation embed
        embed = discord.Embed(
            title="⚠️ Mass Ban Confirmation",
            description=f"Are you sure you want to ban **{len(recent_members)}** recent members?",
            color=0xff0000
        )
        embed.add_field(
            name="📋 Details",
            value=f"**Members:** {len(recent_members)}\n**Reason:** {reason}\n**Timeframe:** Last 5 minutes",
            inline=False
        )
        embed.add_field(
            name="⚠️ Warning",
            value="This action cannot be undone!",
            inline=False
        )
        
        # Create confirmation view
        view = MassBanConfirmView(ctx, recent_members, reason)
        await ctx.send(embed=embed, view=view)

    @commands.command(name="mass-kick")
    @commands.has_permissions(kick_members=True)
    async def mass_kick(self, ctx: commands.Context, *, reason: str = "Mass kick"):
        """Mass kick multiple users (for raids)"""
        
        # Check if user has high enough permissions
        if not ctx.author.guild_permissions.administrator:
            await ctx.reply("❌ This command requires Administrator permissions!")
            return
        
        # Get recent members (joined within last 5 minutes)
        recent_members = []
        for member in ctx.guild.members:
            if member.joined_at and (datetime.now() - member.joined_at).total_seconds() < 300:
                recent_members.append(member)
        
        if not recent_members:
            await ctx.reply("❌ No recent members found to kick!")
            return
        
        # Create confirmation embed
        embed = discord.Embed(
            title="⚠️ Mass Kick Confirmation",
            description=f"Are you sure you want to kick **{len(recent_members)}** recent members?",
            color=0xffa500
        )
        embed.add_field(
            name="📋 Details",
            value=f"**Members:** {len(recent_members)}\n**Reason:** {reason}\n**Timeframe:** Last 5 minutes",
            inline=False
        )
        embed.add_field(
            name="⚠️ Warning",
            value="This action cannot be undone!",
            inline=False
        )
        
        # Create confirmation view
        view = MassKickConfirmView(ctx, recent_members, reason)
        await ctx.send(embed=embed, view=view)

    @commands.command(name="prune")
    @commands.has_permissions(kick_members=True)
    async def prune_members(self, ctx: commands.Context, days: int = 30, *, reason: str = "Inactive members"):
        """Prune inactive members"""
        
        # Check if user has high enough permissions
        if not ctx.author.guild_permissions.administrator:
            await ctx.reply("❌ This command requires Administrator permissions!")
            return
        
        if days < 1 or days > 365:
            await ctx.reply("❌ Days must be between 1 and 365!")
            return
        
        # Get inactive members
        inactive_members = []
        cutoff_date = datetime.now() - timedelta(days=days)
        
        for member in ctx.guild.members:
            if member.joined_at and member.joined_at < cutoff_date:
                # Check if member has any roles (excluding @everyone)
                if len(member.roles) <= 1:
                    inactive_members.append(member)
        
        if not inactive_members:
            await ctx.reply(f"❌ No inactive members found (inactive for {days} days)!")
            return
        
        # Create confirmation embed
        embed = discord.Embed(
            title="⚠️ Prune Confirmation",
            description=f"Are you sure you want to kick **{len(inactive_members)}** inactive members?",
            color=0xffa500
        )
        embed.add_field(
            name="📋 Details",
            value=f"**Members:** {len(inactive_members)}\n**Inactive for:** {days} days\n**Reason:** {reason}",
            inline=False
        )
        embed.add_field(
            name="⚠️ Warning",
            value="This action cannot be undone!",
            inline=False
        )
        
        # Create confirmation view
        view = PruneConfirmView(ctx, inactive_members, reason)
        await ctx.send(embed=embed, view=view)

    @commands.command(name="clear-messages")
    @commands.has_permissions(manage_messages=True)
    async def clear_messages(self, ctx: commands.Context, amount: int = 100, *, filters: str = None):
        """Clear messages with various filters"""
        
        if amount < 1 or amount > 1000:
            await ctx.reply("❌ Amount must be between 1 and 1000!")
            return
        
        # Parse filters
        user_filter = None
        keyword_filter = None
        date_filter = None
        
        if filters:
            # Simple filter parsing (can be enhanced)
            if "user:" in filters:
                user_part = filters.split("user:")[1].split()[0]
                user_filter = user_part
            
            if "keyword:" in filters:
                keyword_part = filters.split("keyword:")[1].split()[0]
                keyword_filter = keyword_part
            
            if "date:" in filters:
                date_part = filters.split("date:")[1].split()[0]
                date_filter = date_part
        
        # Get messages to delete
        messages_to_delete = []
        async for message in ctx.channel.history(limit=amount):
            if message.created_at < datetime.now() - timedelta(days=14):
                break  # Discord API limit
            
            # Apply filters
            if user_filter and user_filter.lower() not in message.author.display_name.lower():
                continue
            
            if keyword_filter and keyword_filter.lower() not in message.content.lower():
                continue
            
            if date_filter:
                # Simple date filtering (can be enhanced)
                try:
                    filter_date = datetime.strptime(date_filter, "%Y-%m-%d")
                    if message.created_at.date() != filter_date.date():
                        continue
                except:
                    pass
            
            messages_to_delete.append(message)
        
        if not messages_to_delete:
            await ctx.reply("❌ No messages found matching the filters!")
            return
        
        # Create confirmation embed
        embed = discord.Embed(
            title="⚠️ Clear Messages Confirmation",
            description=f"Are you sure you want to delete **{len(messages_to_delete)}** messages?",
            color=0xff0000
        )
        embed.add_field(
            name="📋 Details",
            value=f"**Messages:** {len(messages_to_delete)}\n**Channel:** {ctx.channel.mention}\n**Filters:** {filters or 'None'}",
            inline=False
        )
        embed.add_field(
            name="⚠️ Warning",
            value="This action cannot be undone!",
            inline=False
        )
        
        # Create confirmation view
        view = ClearMessagesConfirmView(ctx, messages_to_delete)
        await ctx.send(embed=embed, view=view)

class MassBanConfirmView(discord.ui.View):
    def __init__(self, ctx, members, reason):
        super().__init__(timeout=60)
        self.ctx = ctx
        self.members = members
        self.reason = reason

    @discord.ui.button(label="✅ Confirm", style=discord.ButtonStyle.danger)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.ctx.author:
            await interaction.response.send_message("❌ Only the command author can confirm!", ephemeral=True)
            return
        
        await interaction.response.defer()
        
        # Start mass ban
        embed = discord.Embed(
            title="🚫 Mass Banning...",
            description=f"Banning {len(self.members)} members...",
            color=0xff0000
        )
        await interaction.followup.send(embed=embed)
        
        banned_count = 0
        failed_count = 0
        
        for member in self.members:
            try:
                await member.ban(reason=self.reason)
                banned_count += 1
                await asyncio.sleep(0.5)  # Rate limit protection
            except:
                failed_count += 1
        
        # Update embed
        embed.title = "✅ Mass Ban Complete"
        embed.description = f"**Banned:** {banned_count}\n**Failed:** {failed_count}"
        embed.color = 0x00ff00
        
        await interaction.edit_original_response(embed=embed)
        
        # Log the action
        logging_cog = self.ctx.bot.get_cog('DetailedModLogs')
        if logging_cog:
            await logging_cog.log_mod_action(
                self.ctx.guild,
                "mass_ban",
                self.ctx.author,
                None,
                self.reason,
                f"{banned_count} members"
            )

    @discord.ui.button(label="❌ Cancel", style=discord.ButtonStyle.secondary)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.ctx.author:
            await interaction.response.send_message("❌ Only the command author can cancel!", ephemeral=True)
            return
        
        await interaction.response.send_message("❌ Mass ban cancelled.", ephemeral=True)

class MassKickConfirmView(discord.ui.View):
    def __init__(self, ctx, members, reason):
        super().__init__(timeout=60)
        self.ctx = ctx
        self.members = members
        self.reason = reason

    @discord.ui.button(label="✅ Confirm", style=discord.ButtonStyle.danger)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.ctx.author:
            await interaction.response.send_message("❌ Only the command author can confirm!", ephemeral=True)
            return
        
        await interaction.response.defer()
        
        # Start mass kick
        embed = discord.Embed(
            title="👢 Mass Kicking...",
            description=f"Kicking {len(self.members)} members...",
            color=0xffa500
        )
        await interaction.followup.send(embed=embed)
        
        kicked_count = 0
        failed_count = 0
        
        for member in self.members:
            try:
                await member.kick(reason=self.reason)
                kicked_count += 1
                await asyncio.sleep(0.5)  # Rate limit protection
            except:
                failed_count += 1
        
        # Update embed
        embed.title = "✅ Mass Kick Complete"
        embed.description = f"**Kicked:** {kicked_count}\n**Failed:** {failed_count}"
        embed.color = 0x00ff00
        
        await interaction.edit_original_response(embed=embed)
        
        # Log the action
        logging_cog = self.ctx.bot.get_cog('DetailedModLogs')
        if logging_cog:
            await logging_cog.log_mod_action(
                self.ctx.guild,
                "mass_kick",
                self.ctx.author,
                None,
                self.reason,
                f"{kicked_count} members"
            )

    @discord.ui.button(label="❌ Cancel", style=discord.ButtonStyle.secondary)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.ctx.author:
            await interaction.response.send_message("❌ Only the command author can cancel!", ephemeral=True)
            return
        
        await interaction.response.send_message("❌ Mass kick cancelled.", ephemeral=True)

class PruneConfirmView(discord.ui.View):
    def __init__(self, ctx, members, reason):
        super().__init__(timeout=60)
        self.ctx = ctx
        self.members = members
        self.reason = reason

    @discord.ui.button(label="✅ Confirm", style=discord.ButtonStyle.danger)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.ctx.author:
            await interaction.response.send_message("❌ Only the command author can confirm!", ephemeral=True)
            return
        
        await interaction.response.defer()
        
        # Start pruning
        embed = discord.Embed(
            title="🧹 Pruning...",
            description=f"Kicking {len(self.members)} inactive members...",
            color=0xffa500
        )
        await interaction.followup.send(embed=embed)
        
        pruned_count = 0
        failed_count = 0
        
        for member in self.members:
            try:
                await member.kick(reason=self.reason)
                pruned_count += 1
                await asyncio.sleep(0.5)  # Rate limit protection
            except:
                failed_count += 1
        
        # Update embed
        embed.title = "✅ Prune Complete"
        embed.description = f"**Pruned:** {pruned_count}\n**Failed:** {failed_count}"
        embed.color = 0x00ff00
        
        await interaction.edit_original_response(embed=embed)
        
        # Log the action
        logging_cog = self.ctx.bot.get_cog('DetailedModLogs')
        if logging_cog:
            await logging_cog.log_mod_action(
                self.ctx.guild,
                "prune",
                self.ctx.author,
                None,
                self.reason,
                f"{pruned_count} members"
            )

    @discord.ui.button(label="❌ Cancel", style=discord.ButtonStyle.secondary)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.ctx.author:
            await interaction.response.send_message("❌ Only the command author can cancel!", ephemeral=True)
            return
        
        await interaction.response.send_message("❌ Prune cancelled.", ephemeral=True)

class ClearMessagesConfirmView(discord.ui.View):
    def __init__(self, ctx, messages):
        super().__init__(timeout=60)
        self.ctx = ctx
        self.messages = messages

    @discord.ui.button(label="✅ Confirm", style=discord.ButtonStyle.danger)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.ctx.author:
            await interaction.response.send_message("❌ Only the command author can confirm!", ephemeral=True)
            return
        
        await interaction.response.defer()
        
        # Start clearing messages
        embed = discord.Embed(
            title="🗑️ Clearing Messages...",
            description=f"Deleting {len(self.messages)} messages...",
            color=0xff0000
        )
        await interaction.followup.send(embed=embed)
        
        deleted_count = 0
        failed_count = 0
        
        # Delete messages in batches
        for i in range(0, len(self.messages), 100):
            batch = self.messages[i:i+100]
            try:
                await self.ctx.channel.delete_messages(batch)
                deleted_count += len(batch)
                await asyncio.sleep(1)  # Rate limit protection
            except:
                failed_count += len(batch)
        
        # Update embed
        embed.title = "✅ Clear Complete"
        embed.description = f"**Deleted:** {deleted_count}\n**Failed:** {failed_count}"
        embed.color = 0x00ff00
        
        await interaction.edit_original_response(embed=embed)
        
        # Log the action
        logging_cog = self.ctx.bot.get_cog('DetailedModLogs')
        if logging_cog:
            await logging_cog.log_mod_action(
                self.ctx.guild,
                "clear_messages",
                self.ctx.author,
                None,
                f"Cleared {deleted_count} messages",
                f"Channel: {self.ctx.channel.name}"
            )

    @discord.ui.button(label="❌ Cancel", style=discord.ButtonStyle.secondary)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.ctx.author:
            await interaction.response.send_message("❌ Only the command author can cancel!", ephemeral=True)
            return
        
        await interaction.response.send_message("❌ Clear messages cancelled.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(MassManagement(bot))
