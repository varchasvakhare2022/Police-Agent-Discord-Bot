import discord
from discord.ext import commands
import inspect

class VerificationEnhanced(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    class VerificationView(discord.ui.View):
        def __init__(self, bot):
            super().__init__(timeout=None)
            self.bot = bot

        @discord.ui.button(
            style=discord.ButtonStyle.green,
            label="Verify",
            custom_id="verify_button",
            emoji="✅"
        )
        async def verify_button(self, interaction: discord.Interaction, button: discord.ui.Button):
            """Handle verification button click"""
            
            # Check if user is already verified
            verified_role = discord.utils.get(interaction.guild.roles, name="Verified")
            if verified_role and verified_role in interaction.user.roles:
                await interaction.response.send_message("You are already verified!", ephemeral=True)
                return
            
            try:
                # Add verified role
                if verified_role:
                    await interaction.user.add_roles(verified_role, reason="User verified themselves")
                else:
                    # Create verified role if it doesn't exist
                    verified_role = await interaction.guild.create_role(
                        name="Verified",
                        color=discord.Color.green(),
                        reason="Auto-created verified role"
                    )
                    await interaction.user.add_roles(verified_role, reason="User verified themselves")
                
                # Log the action
                logging_cog = self.bot.get_cog('LoggingSystem')
                if logging_cog:
                    await logging_cog.log_system_event("verification", f"{interaction.user.display_name} verified themselves", interaction.guild, interaction.user)
                
                # Send success message
                embed = discord.Embed(
                    title="✅ Verification Successful!",
                    description=f"Welcome to **{interaction.guild.name}**, {interaction.user.mention}!",
                    color=0x00ff00
                )
                embed.add_field(
                    name="What's Next?",
                    value="• Check out the rules channel\n• Introduce yourself\n• Have fun!",
                    inline=False
                )
                
                await interaction.response.send_message(embed=embed, ephemeral=True)
                
            except discord.Forbidden:
                await interaction.response.send_message("I don't have permission to add roles!", ephemeral=True)
            except Exception as e:
                await interaction.response.send_message(f"An error occurred during verification: {str(e)}", ephemeral=True)

    @commands.command(name="verify")
    @commands.has_permissions(administrator=True)
    async def verify(self, ctx: commands.Context):
        """Send verification message with interactive button"""
        
        embed = discord.Embed(
            title="🔐 Server Verification",
            description=inspect.cleandoc(
                """
                Welcome to **{guild_name}**!
                
                To access all channels and features, please verify yourself by clicking the button below.
                
                **What happens when you verify?**
                • You'll get access to all channels
                • You'll receive the Verified role
                • You can participate in all server activities
                
                **Need help?** Contact a moderator!
                """
            ).format(guild_name=ctx.guild.name),
            color=0x9C84EF
        )
        
        embed.set_footer(text="Police Agent Bot")
        
        view = self.VerificationView(self.bot)
        await ctx.send(embed=embed, view=view)

    @commands.command(name="setup-verification")
    @commands.has_permissions(administrator=True)
    async def setup_verification(self, ctx: commands.Context):
        """Set up verification system"""
        
        # Create verified role if it doesn't exist
        verified_role = discord.utils.get(ctx.guild.roles, name="Verified")
        if not verified_role:
            verified_role = await ctx.guild.create_role(
                name="Verified",
                color=discord.Color.green(),
                reason="Auto-created verified role for verification system"
            )
        
        # Set channel permissions
        for channel in ctx.guild.channels:
            if isinstance(channel, discord.TextChannel):
                try:
                    await channel.set_permissions(
                        ctx.guild.default_role,
                        read_messages=False
                    )
                    await channel.set_permissions(
                        verified_role,
                        read_messages=True
                    )
                except:
                    pass
        
        embed = discord.Embed(
            title="✅ Verification System Setup Complete!",
            description=inspect.cleandoc(
                f"""
                **Verified Role:** {verified_role.mention}
                **Status:** ✅ Active
                
                **What's been set up:**
                • Verified role created/updated
                • Channel permissions configured
                • Verification button ready
                
                Use `{ctx.prefix}verify` to send the verification message!
                """
            ),
            color=0x00ff00
        )
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(VerificationEnhanced(bot))
