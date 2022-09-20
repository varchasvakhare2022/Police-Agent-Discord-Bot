import inspect
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
        amari = AmariClient("e5e71cc6daa28c3d9bc848ee.435561.0813a19d4b9746eacf0d4e68857")
        
        if member == None:
            
            ctx_id = ctx.author.id
            ctx_user = await amari.fetch_user(760134264242700320, ctx_id)
        
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
            member_user = await amari.fetch_user(760134264242700320, member_id)
            
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

