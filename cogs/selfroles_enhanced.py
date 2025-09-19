import discord
from discord.ext import commands
import inspect

class SelfRolesEnhanced(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    class RoleSelectView(discord.ui.View):
        def __init__(self, bot, role_categories):
            super().__init__(timeout=None)
            self.bot = bot
            self.role_categories = role_categories
            
            # Create dropdowns for each category
            for category_name, roles in role_categories.items():
                dropdown = RoleSelectDropdown(category_name, roles)
                self.add_item(dropdown)

    class RoleSelectDropdown(discord.ui.Select):
        def __init__(self, category_name, roles):
            self.category_name = category_name
            self.roles = roles
            
            options = []
            for role_name, role_info in roles.items():
                options.append(discord.SelectOption(
                    label=role_name,
                    description=role_info.get("description", ""),
                    emoji=role_info.get("emoji", "🔹")
                ))
            
            super().__init__(
                placeholder=f"Select {category_name} roles...",
                min_values=0,
                max_values=len(options),
                options=options
            )

        async def callback(self, interaction: discord.Interaction):
            """Handle role selection"""
            
            added_roles = []
            removed_roles = []
            
            for option in self.options:
                role_name = option.label
                role = discord.utils.get(interaction.guild.roles, name=role_name)
                
                if not role:
                    continue
                
                if option.value in self.values:  # Role selected
                    if role not in interaction.user.roles:
                        try:
                            await interaction.user.add_roles(role, reason="Self-role selection")
                            added_roles.append(role_name)
                        except:
                            pass
                else:  # Role not selected
                    if role in interaction.user.roles:
                        try:
                            await interaction.user.remove_roles(role, reason="Self-role selection")
                            removed_roles.append(role_name)
                        except:
                            pass
            
            # Create response embed
            embed = discord.Embed(
                title="🎭 Role Selection Updated",
                color=0x9C84EF
            )
            
            if added_roles:
                embed.add_field(
                    name="✅ Added Roles",
                    value="\n".join([f"• {role}" for role in added_roles]),
                    inline=False
                )
            
            if removed_roles:
                embed.add_field(
                    name="❌ Removed Roles",
                    value="\n".join([f"• {role}" for role in removed_roles]),
                    inline=False
                )
            
            if not added_roles and not removed_roles:
                embed.description = "No changes made to your roles."
            
            await interaction.response.send_message(embed=embed, ephemeral=True)

    @commands.command(name="selfroles")
    @commands.has_permissions(administrator=True)
    async def selfroles(self, ctx: commands.Context):
        """Send self-role selection with interactive dropdowns"""
        
        # Define role categories (customize these for your server)
        role_categories = {
            "Access Roles": {
                "Giveaway Access": {
                    "description": "Get notified about giveaways",
                    "emoji": "🎁"
                },
                "Event Access": {
                    "description": "Get notified about events",
                    "emoji": "🎉"
                },
                "Bot Access": {
                    "description": "Access to bot channels",
                    "emoji": "🤖"
                }
            },
            "Ping Roles": {
                "Announcements": {
                    "description": "Get notified about announcements",
                    "emoji": "📢"
                },
                "Status": {
                    "description": "Get notified about bot status",
                    "emoji": "📊"
                },
                "Partnership": {
                    "description": "Get notified about partnerships",
                    "emoji": "🤝"
                },
                "Polls": {
                    "description": "Get notified about polls",
                    "emoji": "📊"
                }
            },
            "Gaming Roles": {
                "Minecraft": {
                    "description": "Minecraft player",
                    "emoji": "⛏️"
                },
                "Among Us": {
                    "description": "Among Us player",
                    "emoji": "👤"
                },
                "Valorant": {
                    "description": "Valorant player",
                    "emoji": "🔫"
                }
            }
        }
        
        embed = discord.Embed(
            title="🎭 Self-Role Selection",
            description=inspect.cleandoc(
                """
                Choose your roles using the dropdowns below!
                
                **How it works:**
                • Select roles you want to have
                • Deselect roles you want to remove
                • Click outside the dropdown to confirm
                
                **Role Categories:**
                • **Access Roles** - Channel access and permissions
                • **Ping Roles** - Notification preferences
                • **Gaming Roles** - Game-specific roles
                """
            ),
            color=0x9C84EF
        )
        
        embed.set_footer(text="Police Agent Bot")
        
        view = self.RoleSelectView(self.bot, role_categories)
        await ctx.send(embed=embed, view=view)

    @commands.command(name="setup-selfroles")
    @commands.has_permissions(administrator=True)
    async def setup_selfroles(self, ctx: commands.Context):
        """Set up self-role system"""
        
        # Create roles if they don't exist
        roles_to_create = [
            "Giveaway Access", "Event Access", "Bot Access",
            "Announcements", "Status", "Partnership", "Polls",
            "Minecraft", "Among Us", "Valorant"
        ]
        
        created_roles = []
        existing_roles = []
        
        for role_name in roles_to_create:
            role = discord.utils.get(ctx.guild.roles, name=role_name)
            if not role:
                try:
                    role = await ctx.guild.create_role(
                        name=role_name,
                        color=discord.Color.blue(),
                        reason="Auto-created role for self-role system"
                    )
                    created_roles.append(role_name)
                except:
                    pass
            else:
                existing_roles.append(role_name)
        
        embed = discord.Embed(
            title="✅ Self-Role System Setup Complete!",
            description=inspect.cleandoc(
                f"""
                **Created Roles:** {len(created_roles)}
                **Existing Roles:** {len(existing_roles)}
                
                **What's been set up:**
                • Self-role categories configured
                • Interactive dropdowns ready
                • Role management system active
                
                Use `{ctx.prefix}selfroles` to send the self-role message!
                """
            ),
            color=0x00ff00
        )
        
        if created_roles:
            embed.add_field(
                name="New Roles Created",
                value="\n".join([f"• {role}" for role in created_roles]),
                inline=False
            )
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(SelfRolesEnhanced(bot))
