import discord
from discord.ext import commands
import traceback
import asyncio
from datetime import datetime

class CommandErrorHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        """Handle command errors with user-friendly messages"""
        
        # Ignore if command not found
        if isinstance(error, commands.CommandNotFound):
            await self.handle_command_not_found(ctx, error)
            return
        
        # Handle missing required arguments
        if isinstance(error, commands.MissingRequiredArgument):
            await self.handle_missing_argument(ctx, error)
            return
        
        # Handle too many arguments
        if isinstance(error, commands.TooManyArguments):
            await self.handle_too_many_arguments(ctx, error)
            return
        
        # Handle bad argument conversion
        if isinstance(error, commands.BadArgument):
            await self.handle_bad_argument(ctx, error)
            return
        
        # Handle missing permissions
        if isinstance(error, commands.MissingPermissions):
            await self.handle_missing_permissions(ctx, error)
            return
        
        # Handle bot missing permissions
        if isinstance(error, commands.BotMissingPermissions):
            await self.handle_bot_missing_permissions(ctx, error)
            return
        
        # Handle command on cooldown
        if isinstance(error, commands.CommandOnCooldown):
            await self.handle_cooldown(ctx, error)
            return
        
        # Handle user not found
        if isinstance(error, commands.MemberNotFound):
            await self.handle_member_not_found(ctx, error)
            return
        
        # Handle channel not found
        if isinstance(error, commands.ChannelNotFound):
            await self.handle_channel_not_found(ctx, error)
            return
        
        # Handle role not found
        if isinstance(error, commands.RoleNotFound):
            await self.handle_role_not_found(ctx, error)
            return
        
        # Handle other errors
        await self.handle_generic_error(ctx, error)
    
    async def handle_command_not_found(self, ctx, error):
        """Handle when a command is not found"""
        command_name = str(error).split('"')[1] if '"' in str(error) else "unknown"
        
        # Check if it's an old underscore command
        if '_' in command_name:
            suggested_command = command_name.replace('_', ' ')
            embed = discord.Embed(
                title="❌ Command Not Found",
                description=f"The command `{command_name}` doesn't exist.",
                color=0xff6b6b,
                timestamp=datetime.now()
            )
            embed.add_field(
                name="💡 Did you mean?",
                value=f"`{ctx.prefix}{suggested_command}`",
                inline=False
            )
            embed.add_field(
                name="📖 Need help?",
                value=f"Use `{ctx.prefix}help` to see all available commands",
                inline=False
            )
            embed.set_footer(text="💡 Tip: Commands now use spaces instead of underscores!")
        else:
            embed = discord.Embed(
                title="❌ Command Not Found",
                description=f"The command `{command_name}` doesn't exist.",
                color=0xff6b6b,
                timestamp=datetime.now()
            )
            embed.add_field(
                name="📖 Available Commands",
                value=f"Use `{ctx.prefix}help` to see all available commands",
                inline=False
            )
            embed.add_field(
                name="🔍 Search Commands",
                value=f"Use `{ctx.prefix}help <command>` for specific command info",
                inline=False
            )
        
        await ctx.send(embed=embed)
    
    async def handle_missing_argument(self, ctx, error):
        """Handle missing required arguments"""
        param_name = error.param.name
        command_name = ctx.command.name
        
        embed = discord.Embed(
            title="❌ Missing Required Argument",
            description=f"The `{command_name}` command requires a `{param_name}` argument.",
            color=0xff6b6b,
            timestamp=datetime.now()
        )
        
        # Get command help
        command_help = self.get_command_help(command_name)
        if command_help:
            embed.add_field(
                name="💻 Correct Usage",
                value=f"`{ctx.prefix}{command_help['usage']}`",
                inline=False
            )
            embed.add_field(
                name="📝 Description",
                value=command_help['description'],
                inline=False
            )
            embed.add_field(
                name="📋 Example",
                value=f"`{ctx.prefix}{command_help['example']}`",
                inline=False
            )
        
        embed.add_field(
            name="📖 Need more help?",
            value=f"Use `{ctx.prefix}help {command_name}` for detailed information",
            inline=False
        )
        
        await ctx.send(embed=embed)
    
    async def handle_too_many_arguments(self, ctx, error):
        """Handle too many arguments"""
        command_name = ctx.command.name
        
        embed = discord.Embed(
            title="❌ Too Many Arguments",
            description=f"The `{command_name}` command received too many arguments.",
            color=0xff6b6b,
            timestamp=datetime.now()
        )
        
        # Get command help
        command_help = self.get_command_help(command_name)
        if command_help:
            embed.add_field(
                name="💻 Correct Usage",
                value=f"`{ctx.prefix}{command_help['usage']}`",
                inline=False
            )
            embed.add_field(
                name="📋 Example",
                value=f"`{ctx.prefix}{command_help['example']}`",
                inline=False
            )
        
        embed.add_field(
            name="📖 Need more help?",
            value=f"Use `{ctx.prefix}help {command_name}` for detailed information",
            inline=False
        )
        
        await ctx.send(embed=embed)
    
    async def handle_bad_argument(self, ctx, error):
        """Handle bad argument conversion"""
        command_name = ctx.command.name
        
        embed = discord.Embed(
            title="❌ Invalid Argument",
            description=f"One or more arguments for `{command_name}` are invalid.",
            color=0xff6b6b,
            timestamp=datetime.now()
        )
        
        # Get command help
        command_help = self.get_command_help(command_name)
        if command_help:
            embed.add_field(
                name="💻 Correct Usage",
                value=f"`{ctx.prefix}{command_help['usage']}`",
                inline=False
            )
            embed.add_field(
                name="📋 Example",
                value=f"`{ctx.prefix}{command_help['example']}`",
                inline=False
            )
        
        embed.add_field(
            name="📖 Need more help?",
            value=f"Use `{ctx.prefix}help {command_name}` for detailed information",
            inline=False
        )
        
        await ctx.send(embed=embed)
    
    async def handle_missing_permissions(self, ctx, error):
        """Handle missing user permissions"""
        missing_perms = ', '.join(error.missing_permissions)
        
        embed = discord.Embed(
            title="❌ Missing Permissions",
            description=f"You don't have the required permissions to use this command.",
            color=0xff6b6b,
            timestamp=datetime.now()
        )
        embed.add_field(
            name="🔒 Required Permissions",
            value=f"`{missing_perms}`",
            inline=False
        )
        embed.add_field(
            name="💡 How to fix",
            value="Contact a server administrator to get the required permissions.",
            inline=False
        )
        
        await ctx.send(embed=embed)
    
    async def handle_bot_missing_permissions(self, ctx, error):
        """Handle bot missing permissions"""
        missing_perms = ', '.join(error.missing_permissions)
        
        embed = discord.Embed(
            title="❌ Bot Missing Permissions",
            description=f"I don't have the required permissions to execute this command.",
            color=0xff6b6b,
            timestamp=datetime.now()
        )
        embed.add_field(
            name="🔒 Required Permissions",
            value=f"`{missing_perms}`",
            inline=False
        )
        embed.add_field(
            name="💡 How to fix",
            value="Contact a server administrator to give me the required permissions.",
            inline=False
        )
        
        await ctx.send(embed=embed)
    
    async def handle_cooldown(self, ctx, error):
        """Handle command cooldown"""
        retry_after = error.retry_after
        
        embed = discord.Embed(
            title="⏰ Command on Cooldown",
            description=f"Please wait {retry_after:.1f} seconds before using this command again.",
            color=0xffa500,
            timestamp=datetime.now()
        )
        embed.add_field(
            name="💡 Why cooldowns?",
            value="Cooldowns prevent spam and abuse of commands.",
            inline=False
        )
        
        await ctx.send(embed=embed)
    
    async def handle_member_not_found(self, ctx, error):
        """Handle member not found"""
        embed = discord.Embed(
            title="❌ Member Not Found",
            description=f"The member you specified could not be found.",
            color=0xff6b6b,
            timestamp=datetime.now()
        )
        embed.add_field(
            name="💡 How to mention users",
            value="• Use `@username` to mention a user\n• Use `@username#1234` for specific users\n• Use user ID: `<@123456789012345678>`",
            inline=False
        )
        embed.add_field(
            name="📖 Need help?",
            value=f"Use `{ctx.prefix}help {ctx.command.name}` for command details",
            inline=False
        )
        
        await ctx.send(embed=embed)
    
    async def handle_channel_not_found(self, ctx, error):
        """Handle channel not found"""
        embed = discord.Embed(
            title="❌ Channel Not Found",
            description=f"The channel you specified could not be found.",
            color=0xff6b6b,
            timestamp=datetime.now()
        )
        embed.add_field(
            name="💡 How to specify channels",
            value="• Use `#channel-name` to mention a channel\n• Use channel ID: `<#123456789012345678>`",
            inline=False
        )
        embed.add_field(
            name="📖 Need help?",
            value=f"Use `{ctx.prefix}help {ctx.command.name}` for command details",
            inline=False
        )
        
        await ctx.send(embed=embed)
    
    async def handle_role_not_found(self, ctx, error):
        """Handle role not found"""
        embed = discord.Embed(
            title="❌ Role Not Found",
            description=f"The role you specified could not be found.",
            color=0xff6b6b,
            timestamp=datetime.now()
        )
        embed.add_field(
            name="💡 How to specify roles",
            value="• Use `@role-name` to mention a role\n• Use role ID: `<@&123456789012345678>`",
            inline=False
        )
        embed.add_field(
            name="📖 Need help?",
            value=f"Use `{ctx.prefix}help {ctx.command.name}` for command details",
            inline=False
        )
        
        await ctx.send(embed=embed)
    
    async def handle_generic_error(self, ctx, error):
        """Handle generic errors"""
        embed = discord.Embed(
            title="❌ An Error Occurred",
            description="Something went wrong while executing the command.",
            color=0xff6b6b,
            timestamp=datetime.now()
        )
        embed.add_field(
            name="📖 Need help?",
            value=f"Use `{ctx.prefix}help {ctx.command.name}` for command details",
            inline=False
        )
        embed.add_field(
            name="🐛 Report Issues",
            value="If this error persists, contact a server administrator.",
            inline=False
        )
        
        await ctx.send(embed=embed)
        
        # Log the error for debugging
        print(f"Command error in {ctx.command.name}: {error}")
        traceback.print_exc()
    
    def get_command_help(self, command_name):
        """Get help information for a command"""
        # This would be populated with actual command data
        # For now, returning sample data
        command_database = {
            'bot logs': {
                'description': 'View bot logs (admin only)',
                'usage': 'bot logs [type] [limit]',
                'example': 'bot logs admin 20'
            },
            'log config': {
                'description': 'Configure logging settings (admin only)',
                'usage': 'log config <setting> <value>',
                'example': 'log config log_level detailed'
            },
            'log status': {
                'description': 'Show logging configuration (admin only)',
                'usage': 'log status',
                'example': 'log status'
            },
            'clear logs': {
                'description': 'Clear logs (admin only)',
                'usage': 'clear logs [type]',
                'example': 'clear logs all'
            },
            'duty on': {
                'description': 'Go on duty as moderator',
                'usage': 'duty on',
                'example': 'duty on'
            },
            'duty off': {
                'description': 'Go off duty as moderator',
                'usage': 'duty off',
                'example': 'duty off'
            },
            'duty status': {
                'description': 'Check duty status',
                'usage': 'duty status [@user]',
                'example': 'duty status @user'
            },
            'duty roster': {
                'description': 'Show all moderators',
                'usage': 'duty roster',
                'example': 'duty roster'
            },
            'report queue': {
                'description': 'View report queue',
                'usage': 'report queue',
                'example': 'report queue'
            },
            'resolve report': {
                'description': 'Resolve a report',
                'usage': 'resolve report <report_id>',
                'example': 'resolve report R-12345'
            },
            'duty config': {
                'description': 'Configure duty mode',
                'usage': 'duty config <setting> <value>',
                'example': 'duty config auto_assign true'
            },
            'watch user': {
                'description': 'Start watching a user',
                'usage': 'watch user @user [duration]',
                'example': 'watch user @user 1h'
            },
            'unwatch user': {
                'description': 'Stop watching a user',
                'usage': 'unwatch user @user',
                'example': 'unwatch user @user'
            },
            'watch status': {
                'description': 'Check watch status',
                'usage': 'watch status [@user]',
                'example': 'watch status @user'
            },
            'watch config': {
                'description': 'Configure watch mode',
                'usage': 'watch config <setting> <value>',
                'example': 'watch config threshold 50'
            },
            'watch alerts': {
                'description': 'View suspicious activity alerts',
                'usage': 'watch alerts',
                'example': 'watch alerts'
            },
            'police config': {
                'description': 'Configure police persona settings (admin only)',
                'usage': 'police config <setting> <value>',
                'example': 'police config persona_level high'
            },
            'police status': {
                'description': 'Show current police configuration',
                'usage': 'police status',
                'example': 'police status'
            },
            'police test': {
                'description': 'Test police responses',
                'usage': 'police test [response_type]',
                'example': 'police test rule_violations'
            },
            'police responses': {
                'description': 'View police response types',
                'usage': 'police responses',
                'example': 'police responses'
            },
            'police patrol': {
                'description': 'Police patrol announcement',
                'usage': 'police patrol',
                'example': 'police patrol'
            },
            'police arrest': {
                'description': 'Arrest with police persona',
                'usage': 'police arrest @user reason',
                'example': 'police arrest @user Breaking rules'
            },
            'police warning': {
                'description': 'Issue police warning',
                'usage': 'police warning @user reason',
                'example': 'police warning @user First warning'
            },
            'police kick': {
                'description': 'Kick with police persona',
                'usage': 'police kick @user reason',
                'example': 'police kick @user Temporary removal'
            },
            'security report': {
                'description': 'Generate security report',
                'usage': 'security report',
                'example': 'security report'
            },
            'report config': {
                'description': 'Configure reports',
                'usage': 'report config <setting> <value>',
                'example': 'report config log_channel #logs'
            },
            'report status': {
                'description': 'Show report configuration',
                'usage': 'report status',
                'example': 'report status'
            },
            'test report': {
                'description': 'Test report system',
                'usage': 'test report',
                'example': 'test report'
            },
            'add violation': {
                'description': 'Add violation',
                'usage': 'add violation <type> @user <reason>',
                'example': 'add violation spam @user Spamming messages'
            },
            'rule violations': {
                'description': 'Check violations',
                'usage': 'rule violations [@user]',
                'example': 'rule violations @user'
            },
            'clear violations': {
                'description': 'Clear violations (admin only)',
                'usage': 'clear violations @user',
                'example': 'clear violations @user'
            },
            'give reputation': {
                'description': 'Give reputation points',
                'usage': 'give reputation @user points',
                'example': 'give reputation @user 50'
            },
            'reputation': {
                'description': 'Check reputation',
                'usage': 'reputation [@user]',
                'example': 'reputation @user'
            },
            'bypass check': {
                'description': 'Check bypass permissions',
                'usage': 'bypass check @user',
                'example': 'bypass check @user'
            },
            'badge': {
                'description': 'Give Good Citizen badge',
                'usage': 'badge @user reason',
                'example': 'badge @user Helpful member'
            },
            'badges': {
                'description': 'Check badges',
                'usage': 'badges [@user]',
                'example': 'badges @user'
            },
            'leaderboard': {
                'description': 'Show badge leaderboard',
                'usage': 'leaderboard',
                'example': 'leaderboard'
            },
            'siren test': {
                'description': 'Test siren system',
                'usage': 'siren test',
                'example': 'siren test'
            },
            'command count': {
                'description': 'Show command count',
                'usage': 'command count',
                'example': 'command count'
            },
            'crime report': {
                'description': 'Generate crime report',
                'usage': 'crime report',
                'example': 'crime report'
            },
            'patrol status': {
                'description': 'Check patrol status',
                'usage': 'patrol status',
                'example': 'patrol status'
            },
            'force patrol': {
                'description': 'Force patrol message',
                'usage': 'force patrol',
                'example': 'force patrol'
            },
            'patrol test': {
                'description': 'Test patrol system',
                'usage': 'patrol test',
                'example': 'patrol test'
            },
            'start daily reports': {
                'description': 'Start daily reports',
                'usage': 'start daily reports',
                'example': 'start daily reports'
            },
            'stop daily reports': {
                'description': 'Stop daily reports',
                'usage': 'stop daily reports',
                'example': 'stop daily reports'
            }
        }
        
        return command_database.get(command_name, None)

async def setup(bot):
    await bot.add_cog(CommandErrorHandler(bot))
