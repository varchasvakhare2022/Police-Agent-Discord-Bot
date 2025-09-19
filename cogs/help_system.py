import discord
from discord.ext import commands
import json
import os
from datetime import datetime

class HelpMenuView(discord.ui.View):
    def __init__(self, bot, prefix):
        super().__init__(timeout=300)
        self.bot = bot
        self.prefix = prefix
        self.current_page = 0
        self.categories = [
            '🚔 Police Features',
            '👮‍♂️ Moderation', 
            '👁️ Monitoring',
            '👮‍♂️ Duty System',
            '🛡️ Security',
            '📋 Logging',
            '🏆 Reputation',
            '📊 Reports'
        ]
        
    async def get_main_embed(self):
        embed = discord.Embed(
            title="🚔 Police Agent Bot - Help Menu",
            description="A comprehensive police-themed moderation bot with advanced features for server management, user monitoring, and law enforcement simulation.",
            color=0x0099ff,
            timestamp=datetime.now()
        )
        
        embed.add_field(
            name="📖 How to Use",
            value=f"Use `{self.prefix}help <command>` to get detailed information about a specific command.\n"
                  f"Click the buttons below to browse different command categories.",
            inline=False
        )
        
        embed.add_field(
            name="🔍 Quick Search",
            value=f"• `{self.prefix}help warn` - Moderation commands\n"
                  f"• `{self.prefix}help duty` - Duty system commands\n"
                  f"• `{self.prefix}help police` - Police persona commands\n"
                  f"• `{self.prefix}help watch` - Monitoring commands",
            inline=False
        )
        
        embed.add_field(
            name="📊 Bot Statistics",
            value=f"**Total Commands:** {len(self.bot.commands)}\n"
                  f"**Categories:** {len(self.categories)}\n"
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
        
        embed.set_footer(text=f"Use {self.prefix}help <command> for detailed information")
        return embed
    
    async def get_category_embed(self, category_name):
        category_commands = self.get_category_commands(category_name)
        
        embed = discord.Embed(
            title=f"{category_name} Commands",
            description=f"All available commands in the {category_name} category",
            color=0x0099ff,
            timestamp=datetime.now()
        )
        
        if category_commands:
            for command in category_commands[:10]:  # Limit to 10 commands per page
                embed.add_field(
                    name=f"`{self.prefix}{command['name']}`",
                    value=f"{command['description']}\n**Usage:** `{self.prefix}{command['usage']}`",
                    inline=False
                )
        else:
            embed.add_field(
                name="No Commands Found",
                value="This category doesn't have any commands yet.",
                inline=False
            )
        
        embed.set_footer(text=f"Page {self.current_page + 1} of {len(self.categories)}")
        return embed
    
    def get_category_commands(self, category_name):
        # This would be populated with actual command data
        # For now, returning sample data
        sample_commands = {
            '🚔 Police Features': [
                {'name': 'police_config', 'description': 'Configure police persona settings', 'usage': 'police_config <setting> <value>'},
                {'name': 'police_status', 'description': 'Show current police configuration', 'usage': 'police_status'},
                {'name': 'police_test', 'description': 'Test police responses', 'usage': 'police_test [response_type]'},
                {'name': 'police_patrol', 'description': 'Police patrol announcement', 'usage': 'police_patrol'},
                {'name': 'police_arrest', 'description': 'Arrest with police persona', 'usage': 'police_arrest @user reason'},
                {'name': 'police_warning', 'description': 'Issue police warning', 'usage': 'police_warning @user reason'},
                {'name': 'police_kick', 'description': 'Kick with police persona', 'usage': 'police_kick @user reason'}
            ],
            '👮‍♂️ Moderation': [
                {'name': 'warn', 'description': 'Issue a warning to a user', 'usage': 'warn @user reason'},
                {'name': 'warnings', 'description': 'View warning history', 'usage': 'warnings [@user]'},
                {'name': 'case', 'description': 'View case evidence', 'usage': 'case <case_id>'},
                {'name': 'evidence', 'description': 'Add evidence to case', 'usage': 'evidence <case_id> <evidence>'},
                {'name': 'cases', 'description': 'List cases', 'usage': 'cases [@user]'},
                {'name': 'clear_warnings', 'description': 'Clear all warnings (admin)', 'usage': 'clear_warnings @user'}
            ],
            '👁️ Monitoring': [
                {'name': 'watch_user', 'description': 'Start watching a user', 'usage': 'watch_user @user [duration]'},
                {'name': 'unwatch_user', 'description': 'Stop watching a user', 'usage': 'unwatch_user @user'},
                {'name': 'watch_status', 'description': 'Check watch status', 'usage': 'watch_status [@user]'},
                {'name': 'watch_config', 'description': 'Configure watch mode', 'usage': 'watch_config <setting> <value>'},
                {'name': 'watch_alerts', 'description': 'View suspicious activity alerts', 'usage': 'watch_alerts'},
                {'name': 'whois', 'description': 'Get comprehensive user information', 'usage': 'whois @user'},
                {'name': 'history', 'description': 'Get moderation history', 'usage': 'history @user'},
                {'name': 'note', 'description': 'Add private note', 'usage': 'note @user reason'},
                {'name': 'notes', 'description': 'View private notes', 'usage': 'notes @user'}
            ],
            '👮‍♂️ Duty System': [
                {'name': 'duty_on', 'description': 'Go on duty as moderator', 'usage': 'duty_on'},
                {'name': 'duty_off', 'description': 'Go off duty as moderator', 'usage': 'duty_off'},
                {'name': 'duty_status', 'description': 'Check duty status', 'usage': 'duty_status [@user]'},
                {'name': 'duty_roster', 'description': 'Show all moderators', 'usage': 'duty_roster'},
                {'name': 'report_queue', 'description': 'View report queue', 'usage': 'report_queue'},
                {'name': 'resolve_report', 'description': 'Resolve a report', 'usage': 'resolve_report <report_id>'},
                {'name': 'duty_config', 'description': 'Configure duty mode', 'usage': 'duty_config <setting> <value>'}
            ],
            '🛡️ Security': [
                {'name': 'security_report', 'description': 'Generate security report', 'usage': 'security_report'},
                {'name': 'report_config', 'description': 'Configure reports', 'usage': 'report_config <setting> <value>'},
                {'name': 'report_status', 'description': 'Show report configuration', 'usage': 'report_status'},
                {'name': 'test_report', 'description': 'Test report system', 'usage': 'test_report'},
                {'name': 'add_violation', 'description': 'Add violation', 'usage': 'add_violation <type> @user <reason>'},
                {'name': 'rule_violations', 'description': 'Check violations', 'usage': 'rule_violations [@user]'},
                {'name': 'clear_violations', 'description': 'Clear violations (admin)', 'usage': 'clear_violations @user'}
            ],
            '📋 Logging': [
                {'name': 'bot_logs', 'description': 'View bot logs', 'usage': 'bot_logs [type] [limit]'},
                {'name': 'log_config', 'description': 'Configure logging', 'usage': 'log_config <setting> <value>'},
                {'name': 'log_status', 'description': 'Show logging configuration', 'usage': 'log_status'},
                {'name': 'clear_logs', 'description': 'Clear logs (admin)', 'usage': 'clear_logs [type]'}
            ],
            '🏆 Reputation': [
                {'name': 'give_reputation', 'description': 'Give reputation points', 'usage': 'give_reputation @user points'},
                {'name': 'reputation', 'description': 'Check reputation', 'usage': 'reputation [@user]'},
                {'name': 'bypass_check', 'description': 'Check bypass permissions', 'usage': 'bypass_check @user'},
                {'name': 'badge', 'description': 'Give Good Citizen badge', 'usage': 'badge @user reason'},
                {'name': 'badges', 'description': 'Check badges', 'usage': 'badges [@user]'},
                {'name': 'leaderboard', 'description': 'Show badge leaderboard', 'usage': 'leaderboard'},
                {'name': 'siren_test', 'description': 'Test siren system', 'usage': 'siren_test'},
                {'name': 'command_count', 'description': 'Show command count', 'usage': 'command_count'}
            ],
            '📊 Reports': [
                {'name': 'crime_report', 'description': 'Generate crime report', 'usage': 'crime_report'},
                {'name': 'patrol_status', 'description': 'Check patrol status', 'usage': 'patrol_status'},
                {'name': 'force_patrol', 'description': 'Force patrol message', 'usage': 'force_patrol'},
                {'name': 'patrol_test', 'description': 'Test patrol system', 'usage': 'patrol_test'},
                {'name': 'start_daily_reports', 'description': 'Start daily reports', 'usage': 'start_daily_reports'}
            ]
        }
        
        return sample_commands.get(category_name, [])
    
    @discord.ui.button(label="🏠 Home", style=discord.ButtonStyle.primary, row=0)
    async def home_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = await self.get_main_embed()
        await interaction.response.edit_message(embed=embed, view=self)
    
    @discord.ui.button(label="⬅️ Previous", style=discord.ButtonStyle.secondary, row=0)
    async def previous_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current_page = (self.current_page - 1) % len(self.categories)
        embed = await self.get_category_embed(self.categories[self.current_page])
        await interaction.response.edit_message(embed=embed, view=self)
    
    @discord.ui.button(label="➡️ Next", style=discord.ButtonStyle.secondary, row=0)
    async def next_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current_page = (self.current_page + 1) % len(self.categories)
        embed = await self.get_category_embed(self.categories[self.current_page])
        await interaction.response.edit_message(embed=embed, view=self)
    
    @discord.ui.button(label="🚔 Police", style=discord.ButtonStyle.success, row=1)
    async def police_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current_page = 0
        embed = await self.get_category_embed(self.categories[0])
        await interaction.response.edit_message(embed=embed, view=self)
    
    @discord.ui.button(label="👮‍♂️ Moderation", style=discord.ButtonStyle.success, row=1)
    async def moderation_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current_page = 1
        embed = await self.get_category_embed(self.categories[1])
        await interaction.response.edit_message(embed=embed, view=self)
    
    @discord.ui.button(label="👁️ Monitoring", style=discord.ButtonStyle.success, row=1)
    async def monitoring_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current_page = 2
        embed = await self.get_category_embed(self.categories[2])
        await interaction.response.edit_message(embed=embed, view=self)
    
    @discord.ui.button(label="👮‍♂️ Duty", style=discord.ButtonStyle.success, row=2)
    async def duty_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current_page = 3
        embed = await self.get_category_embed(self.categories[3])
        await interaction.response.edit_message(embed=embed, view=self)
    
    @discord.ui.button(label="🛡️ Security", style=discord.ButtonStyle.success, row=2)
    async def security_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current_page = 4
        embed = await self.get_category_embed(self.categories[4])
        await interaction.response.edit_message(embed=embed, view=self)
    
    @discord.ui.button(label="📋 Logging", style=discord.ButtonStyle.success, row=2)
    async def logging_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current_page = 5
        embed = await self.get_category_embed(self.categories[5])
        await interaction.response.edit_message(embed=embed, view=self)
    
    @discord.ui.button(label="🏆 Reputation", style=discord.ButtonStyle.success, row=3)
    async def reputation_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current_page = 6
        embed = await self.get_category_embed(self.categories[6])
        await interaction.response.edit_message(embed=embed, view=self)
    
    @discord.ui.button(label="📊 Reports", style=discord.ButtonStyle.success, row=3)
    async def reports_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current_page = 7
        embed = await self.get_category_embed(self.categories[7])
        await interaction.response.edit_message(embed=embed, view=self)
    
    @discord.ui.button(label="❌ Close", style=discord.ButtonStyle.danger, row=3)
    async def close_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(content="Help menu closed.", embed=None, view=None)

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
    
    def get_prefix(self, ctx):
        """Get the correct prefix for the guild"""
        if ctx.guild:
            return self.bot.storage.get_prefix(ctx.guild.id) if hasattr(self.bot, 'storage') else '-'
        return '-'
    
    def get_command_info(self, command_name):
        """Get detailed information about a specific command"""
        command_database = {
            'police_config': {
                'description': 'Configure police persona settings (admin only)',
                'usage': 'police_config <setting> <value>',
                'permissions': 'Administrator',
                'example': 'police_config persona_level high'
            },
            'police_status': {
                'description': 'Show current police configuration',
                'usage': 'police_status',
                'permissions': 'None',
                'example': 'police_status'
            },
            'police_test': {
                'description': 'Test police responses',
                'usage': 'police_test [response_type]',
                'permissions': 'Manage Messages',
                'example': 'police_test rule_violations'
            },
            'police_patrol': {
                'description': 'Police patrol announcement',
                'usage': 'police_patrol',
                'permissions': 'None',
                'example': 'police_patrol'
            },
            'police_arrest': {
                'description': 'Arrest with police persona',
                'usage': 'police_arrest @user reason',
                'permissions': 'Manage Messages',
                'example': 'police_arrest @user Breaking rules'
            },
            'police_warning': {
                'description': 'Issue police warning',
                'usage': 'police_warning @user reason',
                'permissions': 'Manage Messages',
                'example': 'police_warning @user First warning'
            },
            'police_kick': {
                'description': 'Kick with police persona',
                'usage': 'police_kick @user reason',
                'permissions': 'Manage Messages',
                'example': 'police_kick @user Temporary removal'
            },
            'warn': {
                'description': 'Issue a warning to a user',
                'usage': 'warn @user reason',
                'permissions': 'Manage Messages',
                'example': 'warn @user Spamming messages'
            },
            'warnings': {
                'description': 'View warning history',
                'usage': 'warnings [@user]',
                'permissions': 'None',
                'example': 'warnings @user'
            },
            'case': {
                'description': 'View case evidence',
                'usage': 'case <case_id>',
                'permissions': 'None',
                'example': 'case C-12345'
            },
            'evidence': {
                'description': 'Add evidence to case',
                'usage': 'evidence <case_id> <evidence>',
                'permissions': 'Manage Messages',
                'example': 'evidence C-12345 User was spamming'
            },
            'cases': {
                'description': 'List cases',
                'usage': 'cases [@user]',
                'permissions': 'None',
                'example': 'cases @user'
            },
            'clear_warnings': {
                'description': 'Clear all warnings (admin only)',
                'usage': 'clear_warnings @user',
                'permissions': 'Administrator',
                'example': 'clear_warnings @user'
            },
            'watch_user': {
                'description': 'Start watching a user',
                'usage': 'watch_user @user [duration]',
                'permissions': 'Manage Messages',
                'example': 'watch_user @user 1h'
            },
            'unwatch_user': {
                'description': 'Stop watching a user',
                'usage': 'unwatch_user @user',
                'permissions': 'Manage Messages',
                'example': 'unwatch_user @user'
            },
            'watch_status': {
                'description': 'Check watch status',
                'usage': 'watch_status [@user]',
                'permissions': 'None',
                'example': 'watch_status @user'
            },
            'watch_config': {
                'description': 'Configure watch mode',
                'usage': 'watch_config <setting> <value>',
                'permissions': 'Administrator',
                'example': 'watch_config threshold 50'
            },
            'watch_alerts': {
                'description': 'View suspicious activity alerts',
                'usage': 'watch_alerts',
                'permissions': 'Manage Messages',
                'example': 'watch_alerts'
            },
            'whois': {
                'description': 'Get comprehensive user information',
                'usage': 'whois @user',
                'permissions': 'None',
                'example': 'whois @user'
            },
            'history': {
                'description': 'Get moderation history',
                'usage': 'history @user',
                'permissions': 'None',
                'example': 'history @user'
            },
            'note': {
                'description': 'Add private note',
                'usage': 'note @user reason',
                'permissions': 'Manage Messages',
                'example': 'note @user Suspicious behavior'
            },
            'notes': {
                'description': 'View private notes',
                'usage': 'notes @user',
                'permissions': 'None',
                'example': 'notes @user'
            },
            'duty_on': {
                'description': 'Go on duty as moderator',
                'usage': 'duty_on',
                'permissions': 'Manage Messages',
                'example': 'duty_on'
            },
            'duty_off': {
                'description': 'Go off duty as moderator',
                'usage': 'duty_off',
                'permissions': 'Manage Messages',
                'example': 'duty_off'
            },
            'duty_status': {
                'description': 'Check duty status',
                'usage': 'duty_status [@user]',
                'permissions': 'None',
                'example': 'duty_status @user'
            },
            'duty_roster': {
                'description': 'Show all moderators',
                'usage': 'duty_roster',
                'permissions': 'None',
                'example': 'duty_roster'
            },
            'report_queue': {
                'description': 'View report queue',
                'usage': 'report_queue',
                'permissions': 'Manage Messages',
                'example': 'report_queue'
            },
            'resolve_report': {
                'description': 'Resolve a report',
                'usage': 'resolve_report <report_id>',
                'permissions': 'Manage Messages',
                'example': 'resolve_report R-12345'
            },
            'duty_config': {
                'description': 'Configure duty mode',
                'usage': 'duty_config <setting> <value>',
                'permissions': 'Administrator',
                'example': 'duty_config auto_assign true'
            },
            'security_report': {
                'description': 'Generate security report',
                'usage': 'security_report',
                'permissions': 'Administrator',
                'example': 'security_report'
            },
            'report_config': {
                'description': 'Configure reports',
                'usage': 'report_config <setting> <value>',
                'permissions': 'Administrator',
                'example': 'report_config log_channel #logs'
            },
            'report_status': {
                'description': 'Show report configuration',
                'usage': 'report_status',
                'permissions': 'None',
                'example': 'report_status'
            },
            'test_report': {
                'description': 'Test report system',
                'usage': 'test_report',
                'permissions': 'Administrator',
                'example': 'test_report'
            },
            'add_violation': {
                'description': 'Add violation',
                'usage': 'add_violation <type> @user <reason>',
                'permissions': 'Manage Messages',
                'example': 'add_violation spam @user Spamming messages'
            },
            'rule_violations': {
                'description': 'Check violations',
                'usage': 'rule_violations [@user]',
                'permissions': 'None',
                'example': 'rule_violations @user'
            },
            'clear_violations': {
                'description': 'Clear violations (admin only)',
                'usage': 'clear_violations @user',
                'permissions': 'Administrator',
                'example': 'clear_violations @user'
            },
            'bot_logs': {
                'description': 'View bot logs',
                'usage': 'bot_logs [type] [limit]',
                'permissions': 'Administrator',
                'example': 'bot_logs admin 20'
            },
            'log_config': {
                'description': 'Configure logging',
                'usage': 'log_config <setting> <value>',
                'permissions': 'Administrator',
                'example': 'log_config log_level detailed'
            },
            'log_status': {
                'description': 'Show logging configuration',
                'usage': 'log_status',
                'permissions': 'None',
                'example': 'log_status'
            },
            'clear_logs': {
                'description': 'Clear logs (admin only)',
                'usage': 'clear_logs [type]',
                'permissions': 'Administrator',
                'example': 'clear_logs all'
            },
            'give_reputation': {
                'description': 'Give reputation points',
                'usage': 'give_reputation @user points',
                'permissions': 'Manage Messages',
                'example': 'give_reputation @user 50'
            },
            'reputation': {
                'description': 'Check reputation',
                'usage': 'reputation [@user]',
                'permissions': 'None',
                'example': 'reputation @user'
            },
            'bypass_check': {
                'description': 'Check bypass permissions',
                'usage': 'bypass_check @user',
                'permissions': 'None',
                'example': 'bypass_check @user'
            },
            'badge': {
                'description': 'Give Good Citizen badge',
                'usage': 'badge @user reason',
                'permissions': 'Manage Messages',
                'example': 'badge @user Helpful member'
            },
            'badges': {
                'description': 'Check badges',
                'usage': 'badges [@user]',
                'permissions': 'None',
                'example': 'badges @user'
            },
            'leaderboard': {
                'description': 'Show badge leaderboard',
                'usage': 'leaderboard',
                'permissions': 'None',
                'example': 'leaderboard'
            },
            'siren_test': {
                'description': 'Test siren system',
                'usage': 'siren_test',
                'permissions': 'Administrator',
                'example': 'siren_test'
            },
            'command_count': {
                'description': 'Show command count',
                'usage': 'command_count',
                'permissions': 'None',
                'example': 'command_count'
            },
            'crime_report': {
                'description': 'Generate crime report',
                'usage': 'crime_report',
                'permissions': 'Administrator',
                'example': 'crime_report'
            },
            'patrol_status': {
                'description': 'Check patrol status',
                'usage': 'patrol_status',
                'permissions': 'None',
                'example': 'patrol_status'
            },
            'force_patrol': {
                'description': 'Force patrol message',
                'usage': 'force_patrol',
                'permissions': 'Manage Messages',
                'example': 'force_patrol'
            },
            'patrol_test': {
                'description': 'Test patrol system',
                'usage': 'patrol_test',
                'permissions': 'Administrator',
                'example': 'patrol_test'
            },
            'start_daily_reports': {
                'description': 'Start daily reports',
                'usage': 'start_daily_reports',
                'permissions': 'Administrator',
                'example': 'start_daily_reports'
            }
        }
        
        return command_database.get(command_name, {
            'description': 'Command information not available',
            'usage': f'{command_name} <parameters>',
            'permissions': 'Unknown',
            'example': f'{command_name} example'
        })
    
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
        prefix = self.get_prefix(ctx)
        
        if command_name:
            # Show specific command help
            command_info = self.get_command_info(command_name.lower())
            
            embed = discord.Embed(
                title=f"📖 Help: {command_name.title()}",
                color=self.help_config['embed_color'],
                timestamp=datetime.now()
            )
            
            embed.add_field(
                name="📝 Description",
                value=command_info['description'],
                inline=False
            )
            
            embed.add_field(
                name="💻 Usage",
                value=f"`{prefix}{command_info['usage']}`",
                inline=False
            )
            
            embed.add_field(
                name="🔒 Permissions",
                value=command_info['permissions'],
                inline=True
            )
            
            embed.add_field(
                name="📋 Example",
                value=f"`{prefix}{command_info['example']}`",
                inline=False
            )
            
            embed.set_footer(text="Police Agent Bot Help System")
            await ctx.send(embed=embed)
        else:
            # Show main help menu with interactive buttons
            view = HelpMenuView(self.bot, prefix)
            embed = await view.get_main_embed()
            await ctx.send(embed=embed, view=view)
    
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