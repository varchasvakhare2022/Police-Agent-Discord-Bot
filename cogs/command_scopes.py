import discord
from discord.ext import commands
import json
import os

class CommandScopes(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.scopes_file = "data/command_scopes.json"
        self.load_scopes()

    def load_scopes(self):
        """Load command scopes from JSON file"""
        try:
            if os.path.exists(self.scopes_file):
                with open(self.scopes_file, 'r') as f:
                    self.scopes = json.load(f)
            else:
                self.scopes = {}
                self.save_scopes()
        except Exception as e:
            print(f"Error loading command scopes: {e}")
            self.scopes = {}

    def save_scopes(self):
        """Save command scopes to JSON file"""
        try:
            os.makedirs("data", exist_ok=True)
            with open(self.scopes_file, 'w') as f:
                json.dump(self.scopes, f, indent=2)
        except Exception as e:
            print(f"Error saving command scopes: {e}")

    def get_command_scope(self, guild_id: int, command_name: str) -> list:
        """Get allowed roles for a command in a guild"""
        guild_key = str(guild_id)
        if guild_key not in self.scopes:
            return []
        return self.scopes[guild_key].get(command_name, [])

    def set_command_scope(self, guild_id: int, command_name: str, roles: list):
        """Set allowed roles for a command in a guild"""
        guild_key = str(guild_id)
        if guild_key not in self.scopes:
            self.scopes[guild_key] = {}
        
        self.scopes[guild_key][command_name] = roles
        self.save_scopes()

    def check_command_scope(self, ctx: commands.Context, command_name: str) -> bool:
        """Check if user has permission to use a scoped command"""
        if not ctx.guild:
            return True  # Allow in DMs
        
        allowed_roles = self.get_command_scope(ctx.guild.id, command_name)
        if not allowed_roles:
            return True  # No scope set, allow all
        
        user_roles = [role.id for role in ctx.author.roles]
        return any(role_id in user_roles for role_id in allowed_roles)

    @commands.command(name="scope")
    @commands.has_permissions(administrator=True)
    async def scope_command(self, ctx: commands.Context, command_name: str, *, roles: str = None):
        """Set command scopes for dangerous commands"""
        
        dangerous_commands = ['kick', 'ban', 'timeout', 'unban', 'blacklist']
        
        if command_name not in dangerous_commands:
            await ctx.reply(f"❌ `{command_name}` is not a dangerous command that can be scoped!")
            return
        
        if not roles:
            # Show current scope
            current_roles = self.get_command_scope(ctx.guild.id, command_name)
            if not current_roles:
                await ctx.reply(f"✅ `{command_name}` has no scope restrictions (anyone can use it)")
                return
            
            role_names = []
            for role_id in current_roles:
                role = ctx.guild.get_role(role_id)
                if role:
                    role_names.append(role.name)
            
            embed = discord.Embed(
                title=f"🔒 Command Scope: {command_name}",
                description=f"**Allowed Roles:**\n" + "\n".join([f"• {name}" for name in role_names]),
                color=0x9C84EF
            )
            await ctx.reply(embed=embed)
            return
        
        # Parse roles
        role_ids = []
        role_names = []
        
        for role_mention in roles.split():
            if role_mention.startswith('<@&') and role_mention.endswith('>'):
                role_id = int(role_mention[3:-1])
                role = ctx.guild.get_role(role_id)
                if role:
                    role_ids.append(role_id)
                    role_names.append(role.name)
            elif role_mention.startswith('@'):
                role_name = role_mention[1:]
                role = discord.utils.get(ctx.guild.roles, name=role_name)
                if role:
                    role_ids.append(role.id)
                    role_names.append(role.name)
        
        if not role_ids:
            await ctx.reply("❌ No valid roles found! Use role mentions or @role_name")
            return
        
        # Set scope
        self.set_command_scope(ctx.guild.id, command_name, role_ids)
        
        embed = discord.Embed(
            title="✅ Command Scope Updated",
            description=f"**Command:** `{command_name}`\n**Allowed Roles:**\n" + "\n".join([f"• {name}" for name in role_names]),
            color=0x00ff00
        )
        
        await ctx.reply(embed=embed)

    @commands.command(name="scope-reset")
    @commands.has_permissions(administrator=True)
    async def scope_reset(self, ctx: commands.Context, command_name: str):
        """Reset command scope (allow everyone)"""
        
        dangerous_commands = ['kick', 'ban', 'timeout', 'unban', 'blacklist']
        
        if command_name not in dangerous_commands:
            await ctx.reply(f"❌ `{command_name}` is not a dangerous command!")
            return
        
        self.set_command_scope(ctx.guild.id, command_name, [])
        
        embed = discord.Embed(
            title="✅ Command Scope Reset",
            description=f"`{command_name}` can now be used by anyone with the required permissions",
            color=0x00ff00
        )
        
        await ctx.reply(embed=embed)

    @commands.command(name="scopes")
    @commands.has_permissions(administrator=True)
    async def show_scopes(self, ctx: commands.Context):
        """Show all command scopes"""
        
        dangerous_commands = ['kick', 'ban', 'timeout', 'unban', 'blacklist']
        
        embed = discord.Embed(
            title="🔒 Command Scopes",
            description="Current scope restrictions for dangerous commands",
            color=0x9C84EF
        )
        
        for command in dangerous_commands:
            allowed_roles = self.get_command_scope(ctx.guild.id, command)
            if allowed_roles:
                role_names = []
                for role_id in allowed_roles:
                    role = ctx.guild.get_role(role_id)
                    if role:
                        role_names.append(role.name)
                
                embed.add_field(
                    name=f"`{command}`",
                    value="\n".join([f"• {name}" for name in role_names]),
                    inline=True
                )
            else:
                embed.add_field(
                    name=f"`{command}`",
                    value="No restrictions",
                    inline=True
                )
        
        await ctx.reply(embed=embed)

async def setup(bot):
    await bot.add_cog(CommandScopes(bot))
