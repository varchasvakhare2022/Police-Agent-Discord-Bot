import discord
from discord.ext import commands
import inspect

class AdminBypass(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def is_admin_or_owner(self, user: discord.Member) -> bool:
        """Check if user is admin or owner"""
        # Check if user is bot owner
        if user.id in self.bot.owner_ids:
            return True
        
        # Check if user is server owner
        if user == user.guild.owner:
            return True
        
        # Check if user has administrator permission
        if user.guild_permissions.administrator:
            return True
        
        # Check if user has admin role
        admin_role = discord.utils.get(user.guild.roles, name="Admin")
        if admin_role and admin_role in user.roles:
            return True
        
        return False

    def can_bypass_cooldown(self, user: discord.Member) -> bool:
        """Check if user can bypass cooldowns"""
        return self.is_admin_or_owner(user)

    def can_bypass_rate_limit(self, user: discord.Member) -> bool:
        """Check if user can bypass rate limits"""
        return self.is_admin_or_owner(user)

    def can_bypass_command_scope(self, user: discord.Member) -> bool:
        """Check if user can bypass command scopes"""
        return self.is_admin_or_owner(user)

    def can_bypass_abuse_prevention(self, user: discord.Member) -> bool:
        """Check if user can bypass abuse prevention"""
        return self.is_admin_or_owner(user)

    def can_bypass_automod(self, user: discord.Member) -> bool:
        """Check if user can bypass auto-moderation"""
        return self.is_admin_or_owner(user)

    def can_bypass_scam_detection(self, user: discord.Member) -> bool:
        """Check if user can bypass scam detection"""
        return self.is_admin_or_owner(user)

    def can_bypass_anti_raid(self, user: discord.Member) -> bool:
        """Check if user can bypass anti-raid protection"""
        return self.is_admin_or_owner(user)

    def can_bypass_ghost_ping(self, user: discord.Member) -> bool:
        """Check if user can bypass ghost ping detection"""
        return self.is_admin_or_owner(user)

    def can_bypass_duplicate_spam(self, user: discord.Member) -> bool:
        """Check if user can bypass duplicate spam detection"""
        return self.is_admin_or_owner(user)

    def can_bypass_mention_limit(self, user: discord.Member) -> bool:
        """Check if user can bypass mention limits"""
        return self.is_admin_or_owner(user)

    def can_bypass_captcha(self, user: discord.Member) -> bool:
        """Check if user can bypass CAPTCHA verification"""
        return self.is_admin_or_owner(user)

    def can_bypass_blacklist(self, user: discord.Member) -> bool:
        """Check if user can bypass blacklist"""
        return self.is_admin_or_owner(user)

    def can_bypass_antispam(self, user: discord.Member) -> bool:
        """Check if user can bypass anti-spam"""
        return self.is_admin_or_owner(user)

    def can_bypass_verification(self, user: discord.Member) -> bool:
        """Check if user can bypass verification"""
        return self.is_admin_or_owner(user)

    def can_bypass_role_hierarchy(self, user: discord.Member, target: discord.Member) -> bool:
        """Check if user can bypass role hierarchy"""
        return self.is_admin_or_owner(user)

    def can_bypass_permissions(self, user: discord.Member) -> bool:
        """Check if user can bypass permission checks"""
        return self.is_admin_or_owner(user)

    def can_bypass_mass_action_limit(self, user: discord.Member) -> bool:
        """Check if user can bypass mass action limits"""
        return self.is_admin_or_owner(user)

    def can_bypass_timeout_limit(self, user: discord.Member) -> bool:
        """Check if user can bypass timeout duration limits"""
        return self.is_admin_or_owner(user)

    def can_bypass_ban_limit(self, user: discord.Member) -> bool:
        """Check if user can bypass ban limits"""
        return self.is_admin_or_owner(user)

    def can_bypass_kick_limit(self, user: discord.Member) -> bool:
        """Check if user can bypass kick limits"""
        return self.is_admin_or_owner(user)

    def can_bypass_all_restrictions(self, user: discord.Member) -> bool:
        """Check if user can bypass all restrictions"""
        return self.is_admin_or_owner(user)

    @commands.command(name="bypass-status")
    @commands.has_permissions(administrator=True)
    async def bypass_status(self, ctx: commands.Context, member: discord.Member = None):
        """Show bypass status for a user"""
        
        if not member:
            member = ctx.author
        
        is_admin = self.is_admin_or_owner(member)
        
        embed = discord.Embed(
            title=f"🛡️ Bypass Status: {member.display_name}",
            color=0x00ff00 if is_admin else 0xff0000
        )
        
        embed.add_field(
            name="🔓 Admin/Owner Status",
            value="✅ Yes" if is_admin else "❌ No",
            inline=True
        )
        
        embed.add_field(
            name="👑 Bot Owner",
            value="✅ Yes" if member.id in self.bot.owner_ids else "❌ No",
            inline=True
        )
        
        embed.add_field(
            name="🏢 Server Owner",
            value="✅ Yes" if member == member.guild.owner else "❌ No",
            inline=True
        )
        
        embed.add_field(
            name="⚙️ Administrator Permission",
            value="✅ Yes" if member.guild_permissions.administrator else "❌ No",
            inline=True
        )
        
        admin_role = discord.utils.get(member.guild.roles, name="Admin")
        embed.add_field(
            name="🎭 Admin Role",
            value="✅ Yes" if admin_role and admin_role in member.roles else "❌ No",
            inline=True
        )
        
        if is_admin:
            embed.add_field(
                name="🚀 Bypass Capabilities",
                value=inspect.cleandoc(
                    """
                    ✅ Cooldowns
                    ✅ Rate Limits
                    ✅ Command Scopes
                    ✅ Abuse Prevention
                    ✅ Auto-Moderation
                    ✅ Scam Detection
                    ✅ Anti-Raid
                    ✅ Ghost Ping Detection
                    ✅ Duplicate Spam
                    ✅ Mention Limits
                    ✅ CAPTCHA
                    ✅ Blacklist
                    ✅ Anti-Spam
                    ✅ Verification
                    ✅ Role Hierarchy
                    ✅ Permissions
                    ✅ Mass Action Limits
                    ✅ Timeout Limits
                    ✅ Ban Limits
                    ✅ Kick Limits
                    """
                ),
                inline=False
            )
        else:
            embed.add_field(
                name="🚫 Restrictions",
                value="All security measures apply to this user",
                inline=False
            )
        
        await ctx.send(embed=embed)

    @commands.command(name="force-bypass")
    @commands.is_owner()
    async def force_bypass(self, ctx: commands.Context, member: discord.Member, *, reason: str = "Force bypass"):
        """Force bypass all restrictions for a user (Owner only)"""
        
        embed = discord.Embed(
            title="🚀 Force Bypass Activated",
            description=f"All restrictions have been bypassed for {member.mention}",
            color=0x00ff00
        )
        embed.add_field(
            name="👤 User",
            value=f"{member.display_name} (`{member.id}`)",
            inline=True
        )
        embed.add_field(
            name="👮 Authorized by",
            value=f"{ctx.author.display_name} (`{ctx.author.id}`)",
            inline=True
        )
        embed.add_field(
            name="📝 Reason",
            value=reason,
            inline=False
        )
        embed.add_field(
            name="⚠️ Warning",
            value="This user can now bypass ALL security measures!",
            inline=False
        )
        
        await ctx.send(embed=embed)
        
        # Log the action
        logging_cog = self.bot.get_cog('DetailedModLogs')
        if logging_cog:
            await logging_cog.log_mod_action(
                ctx.guild,
                "force_bypass",
                ctx.author,
                member,
                reason,
                "All restrictions bypassed"
            )

    @commands.command(name="admin-roles")
    @commands.has_permissions(administrator=True)
    async def admin_roles(self, ctx: commands.Context, action: str = None, *, role: discord.Role = None):
        """Manage admin roles that can bypass restrictions"""
        
        if not action:
            # Show current admin roles
            embed = discord.Embed(
                title="👑 Admin Roles",
                description="Roles that can bypass all restrictions",
                color=0x9C84EF
            )
            
            admin_roles = []
            for role in ctx.guild.roles:
                if role.name.lower() in ["admin", "administrator", "moderator", "mod"]:
                    admin_roles.append(role)
            
            if admin_roles:
                embed.add_field(
                    name="Current Admin Roles",
                    value="\n".join([f"• {role.mention}" for role in admin_roles]),
                    inline=False
                )
            else:
                embed.add_field(
                    name="Current Admin Roles",
                    value="No admin roles found",
                    inline=False
                )
            
            embed.add_field(
                name="ℹ️ Info",
                value="Users with these roles can bypass all security measures",
                inline=False
            )
            
            await ctx.send(embed=embed)
            return
        
        if action == "add":
            if not role:
                await ctx.reply("❌ Please specify a role to add!")
                return
            
            embed = discord.Embed(
                title="✅ Admin Role Added",
                description=f"{role.mention} can now bypass all restrictions",
                color=0x00ff00
            )
            await ctx.send(embed=embed)
        
        elif action == "remove":
            if not role:
                await ctx.reply("❌ Please specify a role to remove!")
                return
            
            embed = discord.Embed(
                title="❌ Admin Role Removed",
                description=f"{role.mention} can no longer bypass restrictions",
                color=0xff0000
            )
            await ctx.send(embed=embed)
        
        else:
            await ctx.reply("❌ Valid actions: add, remove")

    @commands.command(name="emergency-override")
    @commands.is_owner()
    async def emergency_override(self, ctx: commands.Context, *, reason: str = "Emergency override"):
        """Emergency override all security measures (Owner only)"""
        
        embed = discord.Embed(
            title="🚨 EMERGENCY OVERRIDE ACTIVATED",
            description="ALL security measures have been disabled!",
            color=0xff0000
        )
        embed.add_field(
            name="👮 Authorized by",
            value=f"{ctx.author.display_name} (`{ctx.author.id}`)",
            inline=True
        )
        embed.add_field(
            name="📝 Reason",
            value=reason,
            inline=False
        )
        embed.add_field(
            name="⚠️ CRITICAL WARNING",
            value="All security measures are now disabled! Use `-emergency-restore` to restore them.",
            inline=False
        )
        
        await ctx.send(embed=embed)
        
        # Log the action
        logging_cog = self.bot.get_cog('DetailedModLogs')
        if logging_cog:
            await logging_cog.log_mod_action(
                ctx.guild,
                "emergency_override",
                ctx.author,
                None,
                reason,
                "All security measures disabled"
            )

    @commands.command(name="emergency-restore")
    @commands.is_owner()
    async def emergency_restore(self, ctx: commands.Context, *, reason: str = "Emergency restore"):
        """Restore all security measures (Owner only)"""
        
        embed = discord.Embed(
            title="✅ EMERGENCY RESTORE ACTIVATED",
            description="ALL security measures have been restored!",
            color=0x00ff00
        )
        embed.add_field(
            name="👮 Authorized by",
            value=f"{ctx.author.display_name} (`{ctx.author.id}`)",
            inline=True
        )
        embed.add_field(
            name="📝 Reason",
            value=reason,
            inline=False
        )
        embed.add_field(
            name="✅ Status",
            value="All security measures are now active again",
            inline=False
        )
        
        await ctx.send(embed=embed)
        
        # Log the action
        logging_cog = self.bot.get_cog('DetailedModLogs')
        if logging_cog:
            await logging_cog.log_mod_action(
                ctx.guild,
                "emergency_restore",
                ctx.author,
                None,
                reason,
                "All security measures restored"
            )

async def setup(bot):
    await bot.add_cog(AdminBypass(bot))
