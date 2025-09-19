import discord
from discord.ext import commands
import traceback
import inspect
from datetime import datetime

class ErrorHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.error_count = 0
        self.error_types = defaultdict(int)

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        """Handle command errors"""
        
        self.error_count += 1
        error_type = type(error).__name__
        self.error_types[error_type] += 1
        
        # Log error to logging system
        logging_cog = self.bot.get_cog('LoggingSystem')
        if logging_cog:
            await logging_cog.log_system_event(
                "command_error",
                f"Command error in {ctx.channel.mention}",
                ctx.guild,
                ctx.author,
                f"Command: {ctx.command.name}\nError: {str(error)}\nType: {error_type}"
            )
        
        # Handle specific error types
        if isinstance(error, commands.CommandNotFound):
            return  # Ignore command not found errors
        
        elif isinstance(error, commands.MissingPermissions):
            embed = discord.Embed(
                title="❌ Missing Permissions",
                description=f"You don't have the required permissions to use `{ctx.command.name}`",
                color=0xff0000
            )
            embed.add_field(
                name="Required Permissions",
                value="\n".join([f"• {perm}" for perm in ctx.command.required_permissions]),
                inline=False
            )
            await ctx.reply(embed=embed, ephemeral=True)
        
        elif isinstance(error, commands.BotMissingPermissions):
            embed = discord.Embed(
                title="❌ Bot Missing Permissions",
                description=f"I don't have the required permissions to execute `{ctx.command.name}`",
                color=0xff0000
            )
            embed.add_field(
                name="Required Permissions",
                value="\n".join([f"• {perm}" for perm in ctx.command.bot_permissions]),
                inline=False
            )
            await ctx.reply(embed=embed, ephemeral=True)
        
        elif isinstance(error, commands.MissingRequiredArgument):
            embed = discord.Embed(
                title="❌ Missing Required Argument",
                description=f"You're missing a required argument for `{ctx.command.name}`",
                color=0xff0000
            )
            embed.add_field(
                name="Usage",
                value=f"`{ctx.prefix}{ctx.command.name} {ctx.command.signature}`",
                inline=False
            )
            await ctx.reply(embed=embed, ephemeral=True)
        
        elif isinstance(error, commands.BadArgument):
            embed = discord.Embed(
                title="❌ Invalid Argument",
                description=f"Invalid argument provided for `{ctx.command.name}`",
                color=0xff0000
            )
            embed.add_field(
                name="Usage",
                value=f"`{ctx.prefix}{ctx.command.name} {ctx.command.signature}`",
                inline=False
            )
            await ctx.reply(embed=embed, ephemeral=True)
        
        elif isinstance(error, commands.CommandOnCooldown):
            embed = discord.Embed(
                title="⏰ Command on Cooldown",
                description=f"Please wait {error.retry_after:.1f} seconds before using `{ctx.command.name}` again",
                color=0xffa500
            )
            await ctx.reply(embed=embed, ephemeral=True)
        
        elif isinstance(error, commands.MaxConcurrencyReached):
            embed = discord.Embed(
                title="🚫 Command Already Running",
                description=f"`{ctx.command.name}` is already running. Please wait for it to finish.",
                color=0xff0000
            )
            await ctx.reply(embed=embed, ephemeral=True)
        
        elif isinstance(error, commands.CheckFailure):
            embed = discord.Embed(
                title="❌ Check Failed",
                description=f"You don't meet the requirements to use `{ctx.command.name}`",
                color=0xff0000
            )
            await ctx.reply(embed=embed, ephemeral=True)
        
        elif isinstance(error, commands.CommandInvokeError):
            # Handle the actual error
            original_error = error.original
            
            if isinstance(original_error, discord.Forbidden):
                embed = discord.Embed(
                    title="❌ Permission Denied",
                    description="I don't have permission to perform this action",
                    color=0xff0000
                )
                await ctx.reply(embed=embed, ephemeral=True)
            
            elif isinstance(original_error, discord.NotFound):
                embed = discord.Embed(
                    title="❌ Not Found",
                    description="The requested resource was not found",
                    color=0xff0000
                )
                await ctx.reply(embed=embed, ephemeral=True)
            
            elif isinstance(original_error, discord.HTTPException):
                embed = discord.Embed(
                    title="❌ HTTP Error",
                    description=f"An HTTP error occurred: {original_error}",
                    color=0xff0000
                )
                await ctx.reply(embed=embed, ephemeral=True)
            
            else:
                # Log unexpected errors
                embed = discord.Embed(
                    title="❌ Unexpected Error",
                    description="An unexpected error occurred. Please try again later.",
                    color=0xff0000
                )
                await ctx.reply(embed=embed, ephemeral=True)
                
                # Log detailed error for debugging
                print(f"Unexpected error in {ctx.command.name}: {original_error}")
                traceback.print_exception(type(original_error), original_error, original_error.__traceback__)
        
        else:
            # Handle any other errors
            embed = discord.Embed(
                title="❌ Unknown Error",
                description="An unknown error occurred. Please try again later.",
                color=0xff0000
            )
            await ctx.reply(embed=embed, ephemeral=True)
            
            # Log error for debugging
            print(f"Unknown error in {ctx.command.name}: {error}")
            traceback.print_exception(type(error), error, error.__traceback__)

    @commands.command(name="error-stats")
    @commands.has_permissions(administrator=True)
    async def error_stats(self, ctx: commands.Context):
        """Show error statistics"""
        
        embed = discord.Embed(
            title="📊 Error Statistics",
            description="Bot error tracking and statistics",
            color=0x9C84EF
        )
        
        embed.add_field(
            name="Total Errors",
            value=f"**{self.error_count}** errors since startup",
            inline=True
        )
        
        embed.add_field(
            name="Error Rate",
            value=f"**{self.error_count / max(1, self.bot.command_count) * 100:.1f}%**",
            inline=True
        )
        
        # Show top error types
        if self.error_types:
            top_errors = sorted(self.error_types.items(), key=lambda x: x[1], reverse=True)[:5]
            error_list = [f"**{error_type}**: {count}" for error_type, count in top_errors]
            
            embed.add_field(
                name="Top Error Types",
                value="\n".join(error_list),
                inline=False
            )
        
        embed.set_footer(text="Use -error-reset to reset error statistics")
        
        await ctx.send(embed=embed)

    @commands.command(name="error-reset")
    @commands.has_permissions(administrator=True)
    async def error_reset(self, ctx: commands.Context):
        """Reset error statistics"""
        
        self.error_count = 0
        self.error_types.clear()
        
        embed = discord.Embed(
            title="✅ Error Statistics Reset",
            description="All error statistics have been reset",
            color=0x00ff00
        )
        
        await ctx.send(embed=embed)

    @commands.command(name="debug")
    @commands.is_owner()
    async def debug(self, ctx: commands.Context, *, command: str):
        """Debug a command (owner only)"""
        
        try:
            # Execute command with debug info
            result = await self.bot.process_commands(ctx.message)
            
            embed = discord.Embed(
                title="🐛 Debug Information",
                description=f"Command: `{command}`",
                color=0x9C84EF
            )
            
            embed.add_field(
                name="Result",
                value=f"```{result}```",
                inline=False
            )
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            embed = discord.Embed(
                title="🐛 Debug Error",
                description=f"Error executing `{command}`",
                color=0xff0000
            )
            
            embed.add_field(
                name="Error",
                value=f"```{str(e)}```",
                inline=False
            )
            
            await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(ErrorHandler(bot))
