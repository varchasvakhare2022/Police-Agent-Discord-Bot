import discord
from discord.ext import commands
import inspect
from datetime import datetime, timedelta

class PollsEnhanced(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    class PollView(discord.ui.View):
        def __init__(self, poll_id, options, duration_minutes=60):
            super().__init__(timeout=duration_minutes * 60)
            self.poll_id = poll_id
            self.options = options
            self.votes = {option: set() for option in options}
            self.voters = set()
            
            # Create buttons for each option
            for i, option in enumerate(options):
                button = PollButton(
                    label=option,
                    custom_id=f"poll_{poll_id}_{i}",
                    style=discord.ButtonStyle.secondary
                )
                self.add_item(button)

        async def on_timeout(self):
            """Handle poll timeout"""
            # Update poll to show results
            await self.update_poll_embed()

        async def update_poll_embed(self):
            """Update poll embed with current results"""
            if not self.children:
                return
            
            # Get the message
            message = None
            for item in self.children:
                if hasattr(item, 'message'):
                    message = item.message
                    break
            
            if not message:
                return
            
            # Calculate results
            total_votes = len(self.voters)
            results = []
            
            for option in self.options:
                votes = len(self.votes[option])
                percentage = (votes / total_votes * 100) if total_votes > 0 else 0
                bar = "█" * int(percentage / 10) + "░" * (10 - int(percentage / 10))
                results.append(f"**{option}**\n{bar} {votes} votes ({percentage:.1f}%)")
            
            # Update embed
            embed = message.embeds[0]
            embed.clear_fields()
            embed.add_field(
                name="📊 Poll Results",
                value="\n\n".join(results),
                inline=False
            )
            embed.add_field(
                name="📈 Statistics",
                value=f"**Total Votes:** {total_votes}\n**Poll ID:** {self.poll_id}",
                inline=False
            )
            
            # Disable all buttons
            for item in self.children:
                item.disabled = True
            
            try:
                await message.edit(embed=embed, view=self)
            except:
                pass

    class PollButton(discord.ui.Button):
        def __init__(self, label, custom_id, style):
            super().__init__(label=label, custom_id=custom_id, style=style)
            self.option = label

        async def callback(self, interaction: discord.Interaction):
            """Handle poll vote"""
            view = self.view
            
            # Check if user already voted
            if interaction.user.id in view.voters:
                await interaction.response.send_message("You have already voted in this poll!", ephemeral=True)
                return
            
            # Add vote
            view.votes[self.option].add(interaction.user.id)
            view.voters.add(interaction.user.id)
            
            # Update poll embed
            await view.update_poll_embed()
            
            await interaction.response.send_message(f"✅ Voted for **{self.option}**!", ephemeral=True)

    @commands.command(name="poll")
    @commands.has_permissions(manage_messages=True)
    async def poll(self, ctx: commands.Context, duration: str = "60m", *, question_and_options: str):
        """Create an interactive poll with buttons"""
        
        # Parse duration
        time_convert = {"s": 1, "m": 60, "h": 3600, "d": 86400}
        try:
            duration_minutes = int(duration[:-1]) * time_convert.get(duration[-1], 60) / 60
        except:
            duration_minutes = 60
        
        # Parse question and options
        parts = question_and_options.split("|")
        if len(parts) < 3:
            await ctx.reply("Please provide a question and at least 2 options separated by |\nExample: `-poll 30m What's your favorite color? | Red | Blue | Green`")
            return
        
        question = parts[0].strip()
        options = [option.strip() for option in parts[1:]]
        
        if len(options) > 10:
            await ctx.reply("Maximum 10 options allowed!")
            return
        
        # Create poll ID
        poll_id = f"{ctx.guild.id}_{int(datetime.now().timestamp())}"
        
        # Create embed
        embed = discord.Embed(
            title=f"📊 Poll: {question}",
            description=f"**Duration:** {duration}\n**Created by:** {ctx.author.mention}",
            color=0x9C84EF,
            timestamp=datetime.now()
        )
        
        embed.add_field(
            name="📝 Options",
            value="\n".join([f"{i+1}. {option}" for i, option in enumerate(options)]),
            inline=False
        )
        
        embed.set_footer(text=f"Poll ID: {poll_id}")
        
        # Create view with buttons
        view = self.PollView(poll_id, options, duration_minutes)
        
        # Send poll
        message = await ctx.send(embed=embed, view=view)
        
        # Store message reference in buttons
        for item in view.children:
            item.message = message

    @commands.command(name="quickpoll")
    @commands.has_permissions(manage_messages=True)
    async def quickpoll(self, ctx: commands.Context, *, question: str):
        """Create a quick yes/no poll"""
        
        poll_id = f"{ctx.guild.id}_{int(datetime.now().timestamp())}"
        
        embed = discord.Embed(
            title=f"📊 Quick Poll: {question}",
            description=f"**Duration:** 10 minutes\n**Created by:** {ctx.author.mention}",
            color=0x9C84EF,
            timestamp=datetime.now()
        )
        
        embed.set_footer(text=f"Poll ID: {poll_id}")
        
        # Create view with yes/no buttons
        view = self.PollView(poll_id, ["Yes", "No"], 10)
        
        message = await ctx.send(embed=embed, view=view)
        
        # Store message reference
        for item in view.children:
            item.message = message

    @commands.command(name="poll-results")
    @commands.has_permissions(manage_messages=True)
    async def poll_results(self, ctx: commands.Context, poll_id: str):
        """Get results for a specific poll"""
        
        # This would require storing poll data persistently
        # For now, just show a message
        await ctx.reply("Poll results feature coming soon! For now, polls show results automatically when they end.")

async def setup(bot):
    await bot.add_cog(PollsEnhanced(bot))
