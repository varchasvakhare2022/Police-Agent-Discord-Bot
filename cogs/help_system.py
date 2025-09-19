import discord
from discord.ext import commands
import json
import os
from datetime import datetime

class HelpSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.help_config_file = 'data/help_config.json'
        
        # Ensure data directory exists
        os.makedirs('data', exist_ok=True)
        
        # Load help configuration
        self.load_data()
    
    def load_data(self):
        """Load help configuration from JSON file"""
        if os.path.exists(self.help_config_file):
            try:
                with open(self.help_config_file, 'r') as f:
                    self.help_config = json.load(f)
            except:
                self.help_config = {
                    'show_hidden': False,
                    'show_aliases': True,
                    'show_permissions': True,
                    'embed_color': 0x0099ff
                }
        else:
            self.help_config = {
                'show_hidden': False,
                'show_aliases': True,
                'show_permissions': True,
                'embed_color': 0x0099ff
            }
        
        self.save_data()
    
    def save_data(self):
        """Save help configuration to JSON file"""
        with open(self.help_config_file, 'w') as f:
            json.dump(self.help_config, f, indent=2)
    
    def get_command_categories(self):
        """Get all command categories"""
        return {
            '🚔 Police Features': {
                'description': 'Core police bot functionality',
                'commands': [
                    'police_config', 'police_status', 'police_test', 'police_responses',
                    'police_patrol', 'police_arrest', 'police_warning', 'police_kick'
                ],
                'color': 0xff0000
            },
            '👮‍♂️ Moderation': {
                'description': 'Moderation and enforcement tools',
                'commands': [
                    'warn', 'warnings', 'case', 'evidence', 'cases', 'clear_warnings',
                    'strike', 'strikes', 'strikeboard', 'strike_stats', 'clear_strikes'
                ],
                'color': 0xff8800
            },
            '👁️ Monitoring': {
                'description': 'User monitoring and surveillance',
                'commands': [
                    'watch_user', 'unwatch_user', 'watch_status', 'watch_config',
                    'watch_alerts', 'whois', 'history', 'note', 'notes', 'modlog'
                ],
                'color': 0x00ff00
            },
            '👮‍♂️ Duty System': {
                'description': 'Moderator duty and workload management',
                'commands': [
                    'duty_on', 'duty_off', 'duty_status', 'duty_roster',
                    'report_queue', 'resolve_report', 'duty_config'
                ],
                'color': 0x0099ff
            },
            '🛡️ Security': {
                'description': 'Security and rule enforcement',
                'commands': [
                    'security_report', 'report_config', 'report_status', 'test_report',
                    'add_violation', 'rule_violations', 'clear_violations'
                ],
                'color': 0x800080
            },
            '📋 Logging': {
                'description': 'Comprehensive logging and transparency',
                'commands': [
                    'bot_logs', 'log_config', 'log_status', 'clear_logs'
                ],
                'color': 0xffff00
            },
            '🏆 Reputation': {
                'description': 'User reputation and badge system',
                'commands': [
                    'give_reputation', 'reputation', 'bypass_check', 'badge',
                    'badges', 'leaderboard', 'siren_test', 'command_count'
                ],
                'color': 0xffd700
            },
            '📊 Reports': {
                'description': 'Crime reports and statistics',
                'commands': [
                    'crime_report', 'patrol_status', 'force_patrol', 'patrol_test',
                    'start_daily_reports', 'patrol_status'
                ],
                'color': 0xff6b6b
            }
        }
    
    @commands.command(name='help')
    async def help_command(self, ctx, *, command_name: str = None):
        """Show help information for commands"""
        if command_name:
            # Show specific command help
            embed = discord.Embed(
                title=f"📖 Help: {command_name.title()}",
                color=self.help_config['embed_color'],
                timestamp=datetime.now()
            )
            
            embed.add_field(
                name="📝 Description",
                value="Command information not available",
                inline=False
            )
            
            embed.add_field(
                name="💻 Usage",
                value=f"`!{command_name} <parameters>`",
                inline=False
            )
            
            embed.add_field(
                name="🔒 Permissions",
                value="Manage Messages",
                inline=True
            )
            
            embed.set_footer(text="Police Agent Bot Help System")
            await ctx.send(embed=embed)
        else:
            # Show main help menu
            embed = discord.Embed(
                title="🚔 Police Agent Bot - Help Menu",
                description="A comprehensive police-themed moderation bot with advanced features",
                color=self.help_config['embed_color'],
                timestamp=datetime.now()
            )
            
            embed.add_field(
                name="📖 How to Use",
                value="Use `!help <command>` to get detailed information about a specific command.\n"
                      "Use `!help_categories` to see all command categories.",
                inline=False
            )
            
            embed.add_field(
                name="🔍 Quick Search",
                value="• `!help warn` - Moderation commands\n"
                      "• `!help duty` - Duty system commands\n"
                      "• `!help police` - Police persona commands\n"
                      "• `!help watch` - Monitoring commands",
                inline=False
            )
            
            embed.add_field(
                name="📊 Bot Statistics",
                value=f"**Total Commands:** {len(self.bot.commands)}\n"
                      f"**Categories:** {len(self.get_command_categories())}\n"
                      f"**Features:** 8 major systems",
                inline=True
            )
            
            embed.add_field(
                name="🛡️ Key Features",
                value="• **Moderation Tools** - Warnings, bans, kicks\n"
                      "• **Duty System** - Workload balancing\n"
                      "• **Monitoring** - Silent watch mode\n"
                      "• **Police Persona** - Authentic responses\n"
                      "• **Reputation System** - User rewards\n"
                      "• **Comprehensive Logging** - Full transparency",
                inline=False
            )
            
            embed.set_footer(text="Use !help <command> for detailed information")
            await ctx.send(embed=embed)
    
    @commands.command(name='help_categories')
    async def help_categories_command(self, ctx):
        """Show all command categories"""
        categories = self.get_command_categories()
        
        embed = discord.Embed(
            title="📚 Command Categories",
            description="All available command categories",
            color=self.help_config['embed_color'],
            timestamp=datetime.now()
        )
        
        for category_name, category_info in categories.items():
            commands_list = ", ".join(category_info['commands'][:5])  # Show first 5 commands
            if len(category_info['commands']) > 5:
                commands_list += f" and {len(category_info['commands']) - 5} more..."
            
            embed.add_field(
                name=category_name,
                value=f"**Description:** {category_info['description']}\n"
                      f"**Commands:** {commands_list}",
                inline=False
            )
        
        embed.set_footer(text="Use !help <command> for detailed information")
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(HelpSystem(bot))