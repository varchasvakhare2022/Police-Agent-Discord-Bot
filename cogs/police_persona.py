import discord
from discord.ext import commands
import json
import os
import random
from datetime import datetime

class PolicePersona(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.persona_config_file = 'data/persona_config.json'
        self.police_responses_file = 'data/police_responses.json'
        
        # Ensure data directory exists
        os.makedirs('data', exist_ok=True)
        
        # Load data
        self.load_data()
    
    def load_data(self):
        """Load persona configuration and police responses from JSON files"""
        # Load persona config
        if os.path.exists(self.persona_config_file):
            try:
                with open(self.persona_config_file, 'r') as f:
                    self.persona_config = json.load(f)
            except:
                self.persona_config = {
                    'enabled': True,
                    'persona_level': 'medium',  # low, medium, high
                    'bot_name': 'Officer Bot',
                    'badge_number': 'POL-001'
                }
        else:
            self.persona_config = {
                'enabled': True,
                'persona_level': 'medium',
                'bot_name': 'Officer Bot',
                'badge_number': 'POL-001'
            }
        
        # Load police responses
        if os.path.exists(self.police_responses_file):
            try:
                with open(self.police_responses_file, 'r') as f:
                    self.police_responses = json.load(f)
            except:
                self.police_responses = self.get_default_responses()
        else:
            self.police_responses = self.get_default_responses()
        
        self.save_data()
    
    def save_data(self):
        """Save persona configuration and police responses to JSON files"""
        with open(self.persona_config_file, 'w') as f:
            json.dump(self.persona_config, f, indent=2)
        
        with open(self.police_responses_file, 'w') as f:
            json.dump(self.police_responses, f, indent=2)
    
    def get_default_responses(self):
        """Get default police responses"""
        return {
            'rule_violations': {
                'low': [
                    "🚔 Please follow the rules, citizen.",
                    "👮‍♂️ That's against the rules, please stop.",
                    "🚓 Rule violation detected. Please comply."
                ],
                'medium': [
                    "🚨 FREEZE! You broke Rule #{rule_number}.",
                    "👮‍♂️ STOP RIGHT THERE! Rule violation in progress!",
                    "🚔 HANDS UP! You're in violation of Rule #{rule_number}.",
                    "🚓 THIS IS THE POLICE! You broke Rule #{rule_number}.",
                    "👮‍♀️ FREEZE! Rule #{rule_number} violation detected!",
                    "🚨 STOP! You're under arrest for Rule #{rule_number}!"
                ],
                'high': [
                    "🚨🚨🚨 FREEZE! YOU'RE UNDER ARREST! Rule #{rule_number} violation! 🚨🚨🚨",
                    "👮‍♂️🚔 STOP RIGHT THERE! THIS IS THE POLICE! Rule #{rule_number}! 🚔👮‍♂️",
                    "🚓🚨 HANDS UP! YOU'RE IN VIOLATION! Rule #{rule_number}! 🚨🚓",
                    "👮‍♀️🚔 FREEZE! POLICE! Rule #{rule_number} violation! 🚔👮‍♀️",
                    "🚨🚓 THIS IS THE POLICE! YOU'RE UNDER ARREST! Rule #{rule_number}! 🚓🚨"
                ]
            },
            'warnings': {
                'low': [
                    "⚠️ Warning issued, citizen.",
                    "👮‍♂️ Please be more careful next time.",
                    "🚓 First warning - please follow the rules."
                ],
                'medium': [
                    "🚨 WARNING! This is your first offense!",
                    "👮‍♂️ FREEZE! Warning issued for rule violation!",
                    "🚔 STOP! Warning #1 - don't let it happen again!",
                    "🚓 HANDS UP! Warning issued - comply with the rules!",
                    "👮‍♀️ FREEZE! Warning delivered - stay in line!"
                ],
                'high': [
                    "🚨🚨🚨 WARNING ISSUED! THIS IS THE POLICE! 🚨🚨🚨",
                    "👮‍♂️🚔 FREEZE! WARNING #1! DON'T MOVE! 🚔👮‍♂️",
                    "🚓🚨 HANDS UP! WARNING DELIVERED! 🚨🚓",
                    "👮‍♀️🚔 STOP! WARNING ISSUED! COMPLY! 🚔👮‍♀️"
                ]
            },
            'bans': {
                'low': [
                    "🚫 User banned for rule violation.",
                    "👮‍♂️ Banned from the server.",
                    "🚓 User removed for breaking rules."
                ],
                'medium': [
                    "🚨 BANNED! You're out of here!",
                    "👮‍♂️ FREEZE! You're banned!",
                    "🚔 STOP! Banned for rule violation!",
                    "🚓 HANDS UP! You're banned!",
                    "👮‍♀️ FREEZE! Banned from the server!"
                ],
                'high': [
                    "🚨🚨🚨 BANNED! YOU'RE UNDER ARREST! 🚨🚨🚨",
                    "👮‍♂️🚔 FREEZE! BANNED! DON'T COME BACK! 🚔👮‍♂️",
                    "🚓🚨 HANDS UP! BANNED! OUT OF HERE! 🚨🚓",
                    "👮‍♀️🚔 STOP! BANNED! COMPLY! 🚔👮‍♀️"
                ]
            },
            'kicks': {
                'low': [
                    "👢 User kicked for rule violation.",
                    "👮‍♂️ Kicked from the server.",
                    "🚓 User removed temporarily."
                ],
                'medium': [
                    "🚨 KICKED! You're out!",
                    "👮‍♂️ FREEZE! You're kicked!",
                    "🚔 STOP! Kicked for rule violation!",
                    "🚓 HANDS UP! You're kicked!",
                    "👮‍♀️ FREEZE! Kicked from the server!"
                ],
                'high': [
                    "🚨🚨🚨 KICKED! YOU'RE UNDER ARREST! 🚨🚨🚨",
                    "👮‍♂️🚔 FREEZE! KICKED! DON'T MOVE! 🚔👮‍♂️",
                    "🚓🚨 HANDS UP! KICKED! OUT OF HERE! 🚨🚓",
                    "👮‍♀️🚔 STOP! KICKED! COMPLY! 🚔👮‍♀️"
                ]
            },
            'general': {
                'low': [
                    "👮‍♂️ Police bot reporting for duty.",
                    "🚓 Officer on patrol.",
                    "🚔 Law enforcement active."
                ],
                'medium': [
                    "🚨 POLICE! Officer {bot_name} reporting!",
                    "👮‍♂️🚔 THIS IS THE POLICE! Badge #{badge_number}!",
                    "🚓🚨 OFFICER ON DUTY! {bot_name} here!",
                    "👮‍♀️🚔 POLICE! Badge #{badge_number} reporting!"
                ],
                'high': [
                    "🚨🚨🚨 POLICE! OFFICER {bot_name}! BADGE #{badge_number}! 🚨🚨🚨",
                    "👮‍♂️🚔🚓 THIS IS THE POLICE! OFFICER {bot_name}! 🚓🚔👮‍♂️",
                    "🚨🚓👮‍♀️ OFFICER ON DUTY! {bot_name}! BADGE #{badge_number}! 👮‍♀️🚓🚨"
                ]
            }
        }
    
    def get_police_response(self, response_type, rule_number=None):
        """Get a random police response based on type and persona level"""
        persona_level = self.persona_config['persona_level']
        
        if response_type not in self.police_responses:
            response_type = 'general'
        
        responses = self.police_responses[response_type].get(persona_level, [])
        
        if not responses:
            responses = self.police_responses[response_type].get('medium', [])
        
        response = random.choice(responses)
        
        # Replace placeholders
        response = response.replace('{rule_number}', str(rule_number) if rule_number else 'X')
        response = response.replace('{bot_name}', self.persona_config['bot_name'])
        response = response.replace('{badge_number}', self.persona_config['badge_number'])
        
        return response
    
    def format_police_message(self, response, user_mention=None, reason=None):
        """Format a police message with proper structure"""
        if not self.persona_config['enabled']:
            return response
        
        # Add police header
        header = f"🚔 **{self.persona_config['bot_name']}** - Badge #{self.persona_config['badge_number']}\n"
        
        # Add user mention if provided
        if user_mention:
            header += f"**Suspect:** {user_mention}\n"
        
        # Add reason if provided
        if reason:
            header += f"**Charge:** {reason}\n"
        
        # Add separator
        header += "─" * 30 + "\n"
        
        return header + response
    
    @commands.command(name='police config')
    @commands.has_permissions(administrator=True)
    async def police_config_command(self, ctx, setting: str, *, value: str):
        """Configure police persona settings (admin only)"""
        if setting.lower() == 'enabled':
            self.persona_config['enabled'] = value.lower() in ['true', 'yes', '1', 'on']
            await ctx.send(f"✅ Police persona enabled: {self.persona_config['enabled']}")
        
        elif setting.lower() == 'persona_level':
            if value.lower() in ['low', 'medium', 'high']:
                self.persona_config['persona_level'] = value.lower()
                await ctx.send(f"✅ Persona level set to: {self.persona_config['persona_level']}")
            else:
                await ctx.send("❌ Invalid persona level. Use: low, medium, high")
        
        elif setting.lower() == 'bot_name':
            self.persona_config['bot_name'] = value
            await ctx.send(f"✅ Bot name set to: {self.persona_config['bot_name']}")
        
        elif setting.lower() == 'badge_number':
            self.persona_config['badge_number'] = value
            await ctx.send(f"✅ Badge number set to: {self.persona_config['badge_number']}")
        
        else:
            await ctx.send("❌ Invalid setting. Available: enabled, persona_level, bot_name, badge_number")
        
        self.save_data()
    
    @commands.command(name='police status')
    async def police_status_command(self, ctx):
        """Show current police persona configuration"""
        embed = discord.Embed(
            title="🚔 Police Persona Configuration",
            color=0x0099ff,
            timestamp=datetime.now()
        )
        
        embed.add_field(
            name="🔄 Status",
            value="✅ Enabled" if self.persona_config['enabled'] else "❌ Disabled",
            inline=True
        )
        
        embed.add_field(
            name="🎭 Persona Level",
            value=self.persona_config['persona_level'].title(),
            inline=True
        )
        
        embed.add_field(
            name="👮‍♂️ Bot Name",
            value=self.persona_config['bot_name'],
            inline=True
        )
        
        embed.add_field(
            name="🏷️ Badge Number",
            value=self.persona_config['badge_number'],
            inline=True
        )
        
        # Show example response
        example_response = self.get_police_response('rule_violations', 2)
        embed.add_field(
            name="📝 Example Response",
            value=example_response,
            inline=False
        )
        
        await ctx.send(embed=embed)
    
    @commands.command(name='police test')
    @commands.has_permissions(manage_messages=True)
    async def police_test_command(self, ctx, response_type: str = 'general'):
        """Test police persona responses"""
        if response_type not in self.police_responses:
            response_type = 'general'
        
        response = self.get_police_response(response_type, 2)
        formatted_response = self.format_police_message(response, ctx.author.mention, "Testing police persona")
        
        await ctx.send(formatted_response)
    
    @commands.command(name='police responses')
    @commands.has_permissions(manage_messages=True)
    async def police_responses_command(self, ctx, response_type: str = None):
        """View available police responses"""
        if response_type:
            if response_type in self.police_responses:
                responses = self.police_responses[response_type]
                embed = discord.Embed(
                    title=f"🚔 Police Responses: {response_type.title()}",
                    color=0x0099ff
                )
                
                for level, level_responses in responses.items():
                    embed.add_field(
                        name=f"{level.title()} Level",
                        value="\n".join(level_responses[:3]),  # Show first 3
                        inline=False
                    )
                
                await ctx.send(embed=embed)
            else:
                await ctx.send(f"❌ Invalid response type. Available: {', '.join(self.police_responses.keys())}")
        else:
            embed = discord.Embed(
                title="🚔 Available Police Response Types",
                color=0x0099ff
            )
            
            for response_type in self.police_responses.keys():
                embed.add_field(
                    name=response_type.title(),
                    value=f"Use `/police_responses {response_type}` to view",
                    inline=True
                )
            
            await ctx.send(embed=embed)
    
    @commands.command(name='police patrol')
    async def police_patrol_command(self, ctx):
        """Police patrol announcement"""
        response = self.get_police_response('general')
        formatted_response = self.format_police_message(response)
        
        await ctx.send(formatted_response)
    
    @commands.command(name='police arrest')
    @commands.has_permissions(manage_messages=True)
    async def police_arrest_command(self, ctx, member: discord.Member, *, reason: str):
        """Arrest a user with police persona"""
        response = self.get_police_response('bans', 1)
        formatted_response = self.format_police_message(response, member.mention, reason)
        
        await ctx.send(formatted_response)
    
    @commands.command(name='police warning')
    @commands.has_permissions(manage_messages=True)
    async def police_warning_command(self, ctx, member: discord.Member, *, reason: str):
        """Issue a police warning"""
        response = self.get_police_response('warnings', 1)
        formatted_response = self.format_police_message(response, member.mention, reason)
        
        await ctx.send(formatted_response)
    
    @commands.command(name='police_kick')
    @commands.has_permissions(manage_messages=True)
    async def police_kick_command(self, ctx, member: discord.Member, *, reason: str):
        """Kick a user with police persona"""
        response = self.get_police_response('kicks', 1)
        formatted_response = self.format_police_message(response, member.mention, reason)
        
        await ctx.send(formatted_response)

async def setup(bot):
    await bot.add_cog(PolicePersona(bot))
