from typing import Optional
import os
import logging
import inspect
import asyncpg
from dotenv import load_dotenv
import asyncio
import discord
from discord.ext import commands, tasks

load_dotenv()

os.environ['JISHAKU_HIDE'] = 'True'
os.environ['JISHAKU_NO_UNDERSCORE'] = 'True'
os.environ['JISHAKU_FORCE_PAGINATOR'] = 'True'
os.environ['JISHAKU_NO_DM_TRACEBACK'] = 'True'

logging.getLogger('discord').setLevel(logging.INFO)

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
logger.addHandler(handler)

#THE BELOW SECTION IS USED ONLY IF YOU USE VERIFY & TICKET SYSTEM FOR YOUR SERVER
#OTHERWISE REMOVE THE WHOLE BELOW SECTION AND DELETE THE VERIFY AND TICKET FILES IN COGS
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
        verified=discord.utils.get(interaction.guild.roles, name="[0] Verified")
        if verified in interaction.user.roles:
            await interaction.response.send_message('Listen bud, You are already verified and remember not to waste time of Police Agents from next time.', ephemeral=True)
        else:
            await interaction.response.send_message('I have given you access to the server!', ephemeral=True)
            await interaction.user.add_roles(verified)

#---------------------------------------------------------------------------------------------------------


MY_GUILD = discord.Object(id=760134264242700320) #your guild id here

class Bot(commands.AutoShardedBot):
    def __init__(self, *, application_id: int, **kwargs) -> None:
        intents = discord.Intents.all()

        super().__init__(
            command_prefix='-', #change prefix if you want
            intents=intents,
            shard_count = 1, #change this accordingly
            owner_ids={
                868465221373665351, # varch
                748552378504052878 # pandey
                #put your id here
            },
            application_id=application_id,
            allowed_mentions=discord.AllowedMentions(
                everyone=False,
                roles=False,
                replied_user=True,
                users=True
            )
        )
    
    @property
    def token(self) -> Optional[str]:
        return os.getenv('BOT_TOKEN')
    
    @tasks.loop(minutes=10)
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
                logging.error(f"Failed to load extension {item}", exc_info=exc)
            else:
                logging.info(f"Loaded extension {item}")

        await self.change_status.start()

    async def setup_hook(self) -> None:
        self.loop.create_task(self._startup_task())
        
    def run(self):
        super().run(
            token=self.token,
            reconnect=True,
            log_handler=None
        )
