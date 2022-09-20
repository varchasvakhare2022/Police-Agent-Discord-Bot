import inspect
from amari import AmariClient
from dotenv import load_dotenv
import os
import discord
from discord.ext import commands

load_dotenv('.env')

amcl = os.environ.get("AMARI_CLIENT")

class Amari(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name="amari", aliases = ["level", "lvl"]
    )
    async def amari(self, ctx: commands.Context, member: discord.Member = None) -> None:
        """Check your amari level"""
        amari = AmariClient(amcl)
        
        if member == None:
            
            ctx_id = ctx.author.id
            ctx_user = await amari.fetch_user(760134264242700320, ctx_id) #replace your guild id
        
            embed = discord.Embed(
                title=f"{ctx.author.name}'s Amari Rank",
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
            member_user = await amari.fetch_user(760134264242700320, member_id) #replace your guild id
            
            embed = discord.Embed(
                title=f"{member.name}'s Amari Rank",
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

