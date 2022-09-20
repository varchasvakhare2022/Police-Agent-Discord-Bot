from ast import Or
import inspect

import discord
from discord.ext import commands

class SelfRole(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name="selfroles")
    @commands.check_any(
        commands.has_any_role(903238046323998720),
        commands.has_permissions(administrator=True)
    )
    async def selfroles(self, ctx: commands.Context) -> None:
        """ping roles"""
        class SelfRoles(discord.ui.View):
            @discord.ui.button(
                style = discord.ButtonStyle.green,
                label = 'Giveaways Access',
                custom_id = 'gaw_access',
                emoji = '<:gaw:971001484261064726>'
            )
            async def gaw_access_button(
                self,
                interaction: discord.Interaction,
                button: discord.ui.button
            ):
                gaw_access = discord.utils.get(ctx.guild.roles, name="Giveaway Access")
                gaw_bl = discord.utils.get(ctx.guild.roles, name = 'Giveaway Blacklist')
                
                if gaw_bl in interaction.user.roles:
                    await interaction.response.send_message('Hold on bro! You are blacklisted from giveaways so i cant hand over this role to you.', ephemeral=True)
                elif gaw_access in interaction.user.roles:
                    await interaction.response.send_message(f'I have removed {gaw_access.mention} from you', ephemeral=True)
                    await interaction.user.remove_roles(gaw_access)
                else:
                    await interaction.response.send_message(f'I have added {gaw_access.mention} to you', ephemeral=True)
                    await interaction.user.add_roles(gaw_access)
                      
            @discord.ui.button(
                style=discord.ButtonStyle.green,
                label='Event Access',
                custom_id='event_access',
                emoji='<:event:971001579593428992>'
            )
            async def event_access_button(
                self,
                interaction: discord.Interaction,
                button: discord.ui.Button
            ):
                event_access = discord.utils.get(ctx.guild.roles, name="Event Access")
                event_bl = discord.utils.get(ctx.guild.roles, name = 'Event Blacklist')
                
                if event_bl in interaction.user.roles:
                    await interaction.response.send_message('Hold on bro! You are blacklisted from events so i cant hand over this role to you.', ephemeral=True)
                elif event_access in interaction.user.roles:
                    await interaction.response.send_message(f'I have removed {event_access.mention} from you', ephemeral=True)
                    await interaction.user.remove_roles(event_access)
                else:
                    await interaction.response.send_message(f'I have added {event_access.mention} to you', ephemeral=True)
                    await interaction.user.add_roles(event_access)
            
            @discord.ui.button(
                style=discord.ButtonStyle.green,
                label='Bot Channel Access',
                custom_id='bot_access',
                emoji='<:bota:971001648786837564>'
            )
            async def bot_access_button(
                self,
                interaction: discord.Interaction,
                button: discord.ui.Button
            ):
                bot_access = discord.utils.get(ctx.guild.roles, name="Bots Access")
                
                if bot_access in interaction.user.roles:
                    await interaction.response.send_message(f'I have removed {bot_access.mention} from you', ephemeral=True)
                    await interaction.user.remove_roles(bot_access)
                else:
                    await interaction.response.send_message(f'I have added {bot_access.mention} to you', ephemeral=True)
                    await interaction.user.add_roles(bot_access)
                    
            @discord.ui.button(
                style=discord.ButtonStyle.blurple,
                label='Announcements',
                custom_id='announcements',
                emoji='<:announcements:970937379839967332>',
                row=2
            )
            async def announcements_button(
                self,
                interaction: discord.Interaction,
                button: discord.ui.Button
            ):
                announcements = discord.utils.get(ctx.guild.roles, name="• ❯ Announcements")
                
                if announcements in interaction.user.roles:
                    await interaction.response.send_message(f'I have removed {announcements.mention} from you', ephemeral=True)
                    await interaction.user.remove_roles(announcements)
                else:
                    await interaction.response.send_message(f'I have added {announcements.mention} to you', ephemeral=True)
                    await interaction.user.add_roles(announcements)
                    
            @discord.ui.button(
                style=discord.ButtonStyle.blurple,
                label='Status',
                custom_id='status',
                emoji='<a:Signal:971011415710261278>',
                row=2
            )
            async def status_button(
                self,
                interaction: discord.Interaction,
                button: discord.ui.Button
            ):
                status = discord.utils.get(ctx.guild.roles, name="• ❯ Status")
                
                if status in interaction.user.roles:
                    await interaction.response.send_message(f'I have removed {status.mention} from you', ephemeral=True)
                    await interaction.user.remove_roles(status)
                else:
                    await interaction.response.send_message(f'I have added {status.mention} to you', ephemeral=True)
                    await interaction.user.add_roles(status)
            
            @discord.ui.button(
                style=discord.ButtonStyle.blurple,
                label='Partnership',
                custom_id='partnership',
                emoji='<a:partner:971010741761081404>',
                row=2
            )
            async def partnership_button(
                self,
                interaction: discord.Interaction,
                button: discord.ui.Button
            ):
                partnership = discord.utils.get(ctx.guild.roles, name="• ❯ Partnerships")
                
                if partnership in interaction.user.roles:
                    await interaction.response.send_message(f'I have removed {partnership.mention} from you', ephemeral=True)
                    await interaction.user.remove_roles(partnership)
                else:
                    await interaction.response.send_message(f'I have added {partnership.mention} to you', ephemeral=True)
                    await interaction.user.add_roles(partnership)
            
            @discord.ui.button(
                style=discord.ButtonStyle.blurple,
                label='Giveaways',
                custom_id='giveaways',
                emoji='<a:giveaways:970959495708676146>',
                row=3
            )
            async def giveaways_button(
                self,
                interaction: discord.Interaction,
                button: discord.ui.Button
            ):
                giveaways = discord.utils.get(ctx.guild.roles, name="• ❯ Giveaways")
                gaw_access = discord.utils.get(ctx.guild.roles, name="Giveaway Access")
                
                if gaw_access in interaction.user.roles:
                    if giveaways in interaction.user.roles:
                        await interaction.response.send_message(f'I have removed {giveaways.mention} from you', ephemeral=True)
                        await interaction.user.remove_roles(giveaways)
                    else:
                        await interaction.response.send_message(f'I have added {giveaways.mention} to you', ephemeral=True)
                        await interaction.user.add_roles(giveaways)
                else:
                    await interaction.response.send_message(f'You need the {gaw_access.mention} to get this role', ephemeral=True)
          
            @discord.ui.button(
                style=discord.ButtonStyle.blurple,
                label='Events',
                custom_id='events',
                emoji='<a:events:971012368245067826>',
                row=3
            )
            async def events_button(
                self,
                interaction: discord.Interaction,
                button: discord.ui.Button
            ):
                events = discord.utils.get(ctx.guild.roles, name="• ❯ Events")
                event_access = discord.utils.get(ctx.guild.roles, name="Event Access")
                
                if event_access in interaction.user.roles:
                    if events in interaction.user.roles:
                        await interaction.response.send_message(f'I have removed {events.mention} from you', ephemeral=True)
                        await interaction.user.remove_roles(events)
                    else:
                        await interaction.response.send_message(f'I have added {events.mention} to you', ephemeral=True)
                        await interaction.user.add_roles(events)
                else:
                    await interaction.response.send_message(f'You need the {event_access.mention} to get this role', ephemeral=True)
            
            @discord.ui.button(
                style=discord.ButtonStyle.blurple,
                label='Polls',
                custom_id='polls',
                emoji='<a:polls:971013012838297651>',
                row=2
            )
            async def polls_button(
                self,
                interaction: discord.Interaction,
                button: discord.ui.Button
            ):
                polls = discord.utils.get(ctx.guild.roles, name="• ❯ Polls")
                
                if polls in interaction.user.roles:
                    await interaction.response.send_message(f'I have removed {polls.mention} from you', ephemeral=True)
                    await interaction.user.remove_roles(polls)
                else:
                    await interaction.response.send_message(f'I have added {polls.mention} to you', ephemeral=True)
                    await interaction.user.add_roles(polls)

                
                
        embed = discord.Embed(
            #title=f'Ping roles below dummy',
            description=inspect.cleandoc(
                f"""
                **Access Roles -**
                
                ・Giveaway Access - Access to giveaway channels
                ・Event Access - Access to event channels
                ・Bot Access - Access to all bot channels
                
                **Ping Roles -**
                
                ・Announcements - Get notified on any server updates, staff applications etc
                ・Status - Get notified on bot's uptime and downtime
                ・Partnership - Get pinged whenever we partner with a server
                ・Polls - Get notified to react in polls
                ・Giveaways - Get pinged on any ongoing giveaway
                ・Events - Get notified on any ongoing event
                """
            ),
            color=0xfcf55f
        )
        await ctx.send(embed=embed, view=SelfRoles())
        
async def setup(bot):
    await bot.add_cog(SelfRole(bot))

