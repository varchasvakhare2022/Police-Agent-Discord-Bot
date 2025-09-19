import inspect
import os
from amari import AmariClient
import discord
from discord.ext import commands





class Amari(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name="amari", aliases = ["level", "lvl"]
    )
    async def amari(self, ctx: commands.Context, member: discord.Member = None) -> None:
        """Check your amari level"""
        amari_token = os.getenv('AMARI_TOKEN')
        if not amari_token:
            await ctx.send("Amari API token not configured.")
            return
        amari = AmariClient(amari_token)
        
        if member == None:
            
            ctx_id = ctx.author.id
            guild_id = int(os.getenv('GUILD_ID', '760134264242700320'))
            ctx_user = await amari.fetch_user(guild_id, ctx_id)
        
            embed = discord.Embed(
                title=f"{ctx.author.display_name}'s Amari Rank",
                description = inspect.cleandoc(
                    f"""
                    **Level**
                    {ctx_user.level}
                    
                    **XP**
                    {ctx_user.exp}
                    
                    **Weekly XP**
                    {ctx_user.weeklyexp}
                    """
                ),
                color=0x9C84EF
            )
            await ctx.send(embed=embed)
            
        else:
            
            member_id = member.id
            guild_id = int(os.getenv('GUILD_ID', '760134264242700320'))
            member_user = await amari.fetch_user(guild_id, member_id)
            
            embed = discord.Embed(
                title=f"{member.display_name}'s Amari Rank",
                description = inspect.cleandoc(
                    f"""
                    **Level**
                    {member_user.level}
                    
                    **XP**
                    {member_user.exp}
                    
                    **Weekly XP**
                    {member_user.weeklyexp}
                    """
                ),
                color=0x9C84EF
            )
            await ctx.send(embed=embed)
        
async def setup(bot):
    await bot.add_cog(Amari(bot))

