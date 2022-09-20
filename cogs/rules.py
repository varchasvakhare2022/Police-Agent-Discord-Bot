from ast import Or
import inspect

import discord
from discord.ext import commands

class Rules(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name="rules")
    async def rules(self, ctx: commands.Context) -> None:
        """Some Server Rules"""
        
        embed = discord.Embed(
            title=f'Detective Hub Rules',
            description=inspect.cleandoc(
                f"""
                **1・Discord TOS & Community Guidelines**
                All users need to follow [Discord's Terms of Service](https://discord.com/terms) and [Community Guidelines](https://discord.com/guidelines).
                Punishment - Ban
                
                **2・Bot Rules**
                As a Community server, we will enforce Bot rules.
                Punishment - Ban
                
                **3・Robbing**
                Robbing and heisting are disabled on our server. We want our server to be a safe space for anyone to use the bot without fear of losing hard-earned money. In some bots which don't offer a disable command like MafiaBot so you are not allowed to rob in these types of bot as well.
                Punishment - Warn/Mute/Ban
                
                **4・Racism**
                Any racial slurs or racist behavior/comments are NOT accepted in this server.
                Punishment - Warn/Mute/Ban
                
                **5・Channel Appropriacy**
                Please try to keep things in the right channels!
                Punishment - Mute/Warn
                
                **6・NSFW**
                NSFW content is against the rules. This includes gore, porn, and violent videos/images. It also includes conversations about sensitive and inappropriate topics.
                Punishment - Warn/Ban
                
                **7・Voice Rules**
                Ear raping, playing unreasonable sounds through a mic, or putting on inappropriate music goes against our rules. Voice chat hopping is also not allowed.
                Punishment - Mute/Warn
                
                **8・Spam**
                Spamming text, images, or emojis, is not allowed. If you spam, you will most likely be muted by auto-moderation bots.
                Punishment - Mute/Warn
                
                **9・Alternate Accounts**
                Inviting alternative accounts / using alternative accounts in the server is against our rules.
                Punishment - Warn/Ban
                
                **10・Begging**
                Begging is strictly prohibited in this server. This also includes bot currency/nitro.
                Punishment - Warn/Mute
                
                **11・Advertisement**
                Advertisements of any kinds is not allowed in this server outside of #self-advertise and Partnerships.
                Punishment - Warn/Mute
                
                **12・Common Sense**
                Since we can't include everything in a short set of rules, but using your common sense is really important. Exploiting loopholes in our rules is not allowed and you can still be punished if you have not explicitly broken a rule.
                Punishment - Depends
                
                *Don't forget to check pinned messages and channel descriptions for channel specific rules.*
                """
            ),
            color=0x111111
        )
        await ctx.send(embed=embed)
        
async def setup(bot):
    await bot.add_cog(Rules(bot))

