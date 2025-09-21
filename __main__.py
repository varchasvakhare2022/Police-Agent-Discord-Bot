from ast import mod
import logging
import random
import os
from re import sub
import traceback
import sys
import asyncio
import inspect
import logging

import discord
from discord.ext import commands, tasks
import os
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
APPLICATION_ID = int(os.getenv('APPLICATION_ID', '919149033820418059'))
GUILD_ID = int(os.getenv('GUILD_ID', '760134264242700320'))

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN environment variable is required")

async def _prefix_callable(bot: commands.AutoShardedBot, message: discord.Message):
    if not message.guild:
        return ['-']
    
    # Load prefixes from JSON file
    try:
        with open('data/prefixes.json', 'r') as f:
            prefixes = json.load(f)
        prefix = prefixes.get(str(message.guild.id), '-')
    except (FileNotFoundError, json.JSONDecodeError):
        prefix = '-'
    
    base = [
        f'<@{bot.user.id}>',
        f'<@!{bot.user.id}>',
        prefix
    ]
    
    return base
#BUTTON CLASS FOR PERSISTANCE-------------------------------------------------------------------------
class Ticket(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    @discord.ui.button(style=discord.ButtonStyle.green, label='Create a Ticket', custom_id='ticket', emoji='<:mail:970204846579933204>')
    async def ticket_create_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        category = discord.utils.get(interaction.guild.categories, name='⪻ᚔᚓᚒᚑ᚜hub᚛ᚑᚒᚓᚔ⪼')
        mod=discord.utils.get(interaction.guild.roles, name="Moderation Team")
                
        ticket = await interaction.guild.create_text_channel(
            category=category,
            topic=interaction.user.id,
            name=f"Ticket-{interaction.user.name}",
            overwrites={
                interaction.guild.default_role: discord.PermissionOverwrite(view_channel=False),
                interaction.user: discord.PermissionOverwrite(view_channel=True),
                mod: discord.PermissionOverwrite(view_channel=True)
            }
        )
        embed = discord.Embed(
            description=inspect.cleandoc(
                """
                • Type your issue as soon as possible
                • You can ping any online mod if no one responds in 10 minutes
                """
            )
        )
        class TicketClose(discord.ui.View):
            def __init__(self):
                super().__init__(timeout=None)
            @discord.ui.button(style=discord.ButtonStyle.gray, label='Close', custom_id='ticket_close', emoji='<:closed:970208866728022106>')
            async def ticket_close_button(self, interaction: discord.Interaction, button: discord.ui.Button):
                
                if mod in interaction.user.roles:
                    await interaction.response.send_message("This ticket will be deleted in <a:5secs:970384338413842512> seconds")
                    await asyncio.sleep(5)
                    await ticket.delete()
                else:
                    await interaction.response.send_message("You Don't have the permissions to do this", ephemeral=True)
        await ticket.send(f'{interaction.user.mention}', embed=embed, view=TicketClose())
        await interaction.response.send_message(f'ticket created in <#{ticket.id}>', ephemeral=True)

class TicketClose(discord.ui.View):
    
    def __init__(self):
        super().__init__(timeout=None)
    @discord.ui.button(style=discord.ButtonStyle.gray, label='Close', custom_id='ticket_close', emoji='<:closed:970208866728022106>')
    async def ticket_close_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        mod=discord.utils.get(interaction.guild.roles, name="Moderation Team")
        if mod in interaction.user.roles:
            await interaction.response.send_message("This ticket will be deleted in <a:5secs:970384338413842512> seconds")
            await asyncio.sleep(5)
            await interaction.channel.delete()
        else:
            await interaction.response.send_message("You Don't have the permissions to do this", ephemeral=True)

class Verify(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    
    @discord.ui.button(style=discord.ButtonStyle.green, label='Verify', custom_id='verify', emoji='<:DiscordVerified:970932623734104095>')
    async def verification_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Get the captcha verification cog
        captcha_cog = interaction.client.get_cog('CaptchaVerification')
        if captcha_cog:
            await captcha_cog.handle_verification_attempt(interaction, interaction.user)
        else:
            # Fallback to old system if captcha cog is not loaded
            verified = interaction.guild.get_role(903238068910309398)
            if verified and verified in interaction.user.roles:
                await interaction.response.send_message('Listen bud, You are already verified and remember not to waste time of Police Agents from next time.', ephemeral=True)
            else:
                await interaction.response.send_message('I have given you access to the server!', ephemeral=True)
                await interaction.user.add_roles(verified)

class SelfRoles(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
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
        gaw_access = discord.utils.get(interaction.guild.roles, name="Giveaway Access")
        gaw_bl = discord.utils.get(interaction.guild.roles, name = 'Giveaway Blacklist')
                
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
        event_access = discord.utils.get(interaction.guild.roles, name="Event Access")
        event_bl = discord.utils.get(interaction.guild.roles, name = 'Event Blacklist')
                
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
        bot_access = discord.utils.get(interaction.guild.roles, name="Bots Access")
                
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
        announcements = discord.utils.get(interaction.guild.roles, name="• ❯ Announcements")
                
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
        status = discord.utils.get(interaction.guild.roles, name="• ❯ Status")
                
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
        partnership = discord.utils.get(interaction.guild.roles, name="• ❯ Partnerships")
                
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
        giveaways = discord.utils.get(interaction.guild.roles, name="• ❯ Giveaways")
        gaw_access = discord.utils.get(interaction.guild.roles, name="Giveaway Access")
                
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
        events = discord.utils.get(interaction.guild.roles, name="• ❯ Events")
        event_access = discord.utils.get(interaction.guild.roles, name="Event Access")
                
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
        polls = discord.utils.get(interaction.guild.roles, name="• ❯ Polls")
                
        if polls in interaction.user.roles:
            await interaction.response.send_message(f'I have removed {polls.mention} from you', ephemeral=True)
            await interaction.user.remove_roles(polls)
        else:
            await interaction.response.send_message(f'I have added {polls.mention} to you', ephemeral=True)
            await interaction.user.add_roles(polls)
#---------------------------------------------------------------------------------------------------------

os.environ['JISHAKU_HIDE'] = 'True'
os.environ['JISHAKU_NO_UNDERSCORE'] = 'True'
os.environ['JISHAKU_FORCE_PAGINATOR'] = 'True'
os.environ['JISHAKU_NO_DM_TRACEBACK'] = 'True'

class Bot(commands.AutoShardedBot):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(
            command_prefix=_prefix_callable,
            shard_count=1, 
            intents=intents,
            case_insensitive=True,
            strip_after_prefix=True,
            owner_ids=[
                868465221373665351,
                748552378504052878 # pandey
            ]
        )
        self.add_check(self.blacklisted_check)
    
    async def blacklisted_check(self, ctx: commands.Context):
        # bot owners bypass this
        if await bot.is_owner(ctx.author):
            return True

        # Load blacklist from JSON file
        try:
            with open('data/blacklist.json', 'r') as f:
                blacklist = json.load(f)
            if str(ctx.author.id) in blacklist:
                delete_after: int = 7
                
                embed = discord.Embed(
                    description='Unfortunately, you have been blacklisted from the bot. If you wish to know why or appeal, please join **[this server](https://discord.gg/xRquATkezz)**.'
                )
                await ctx.reply(
                    embed=embed,
                    delete_after=delete_after
                )
                await ctx.message.delete(delay=delete_after)

                return False
            else: # everything is normal, not blacklisted
                return True
        except (FileNotFoundError, json.JSONDecodeError):
            # If blacklist file doesn't exist or is invalid, allow the command
            return True
    
    @tasks.loop(minutes=1)
    async def change_status(self):
        await self.change_presence(
            status=discord.Status.dnd,
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name='Silently! Be Careful.'
            )
        )
        

    @change_status.before_loop
    async def _before_change_status(self):
        await self.wait_until_ready()

    async def _startup_task(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print('------')

        extensions = [
            'jishaku',
            *[
                f'cogs.{extension[:-3]}'
                for extension in os.listdir('./cogs')
                if extension.endswith('.py')
            ]
        ]

        for item in extensions:
            try:
                await self.load_extension(item)
            except Exception as exc:
                print(f"Failed to load extension {item}")
                traceback.print_exc()

        self.change_status.start()
    
    async def _create_data_files(self):
        """Create necessary data files if they don't exist"""
        import os
        
        # Create data directory if it doesn't exist
        os.makedirs('data', exist_ok=True)
        
        # Create prefixes.json if it doesn't exist
        if not os.path.exists('data/prefixes.json'):
            with open('data/prefixes.json', 'w') as f:
                json.dump({}, f)
        
        # Create blacklist.json if it doesn't exist
        if not os.path.exists('data/blacklist.json'):
            with open('data/blacklist.json', 'w') as f:
                json.dump([], f)
        
        # Create captcha_data.json if it doesn't exist
        if not os.path.exists('data/captcha_data.json'):
            with open('data/captcha_data.json', 'w') as f:
                json.dump({}, f)
        
        # Create verification_cooldown.json if it doesn't exist
        if not os.path.exists('data/verification_cooldown.json'):
            with open('data/verification_cooldown.json', 'w') as f:
                json.dump({}, f)
        
        # Create warnings.json if it doesn't exist
        if not os.path.exists('data/warnings.json'):
            with open('data/warnings.json', 'w') as f:
                json.dump({}, f)
        
        print('Data files initialized.')

    async def setup_hook(self) -> None:
        asyncio.create_task(self._startup_task())
        await self._create_data_files()
        self.add_view(Verify())
        self.add_view(Ticket())
        self.add_view(TicketClose())
        self.add_view(SelfRoles())
        
    def run(self):
        super().run(
            token=BOT_TOKEN,
            reconnect=True
        )
intents = discord.Intents.all()

if __name__ == '__main__':
    bot = Bot(intents=intents)
    bot.run()
