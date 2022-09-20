import traceback
import sys

import discord
from discord.ext import commands

class Handlers(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.Cog.listener('on_command_error')
    async def error_handler(self, ctx, error):
        ignored = (
            commands.CommandNotFound
        )
        if isinstance(error, ignored):
            return

        embed = discord.Embed(
            colour=0xff0000
        )
        
        if isinstance(error, commands.MissingRequiredArgument):
            embed.description = str(error)[:4096]
            return await ctx.reply(embed=embed)
        elif isinstance(error, commands.CommandOnCooldown):
            if await self.bot.is_owner(ctx.author):
                ctx.command.reset_cooldown(ctx)
                return await ctx.reinvoke()

            embed.title = "Slow it down bro!"
            embed.description = f"Try again in {error.retry_after:.2f}s."
            await ctx.reply(embed=embed)
        elif isinstance(error, commands.NotOwner):
            embed.description = "Only my owners can use this command!"
            return await ctx.reply(embed=embed)
        elif isinstance(error, commands.NSFWChannelRequired):
            embed.description = "This command can only be used in a NSFW channel."
            return await ctx.reply(embed=embed)
        elif isinstance(error, (commands.BadArgument, commands.BadBoolArgument, commands.BadUnionArgument, commands.BadColourArgument, commands.BadInviteArgument)):
            embed.description = str(error)[:4096]
            return await ctx.reply(embed=embed)
        else:
            print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
            traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)
            embed.description = str(error)[:4096]
            await ctx.reply(embed=embed)
    
async def setup(bot):
    await bot.add_cog(Handlers(bot))