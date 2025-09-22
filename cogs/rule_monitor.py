import discord
from discord.ext import commands
import re
import asyncio
from datetime import datetime, timedelta

class RuleMonitor(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.cooldown_users = {}  # Track users to avoid spam
        self.cooldown_duration = 300  # 5 minutes cooldown per user
        
        # Define rule patterns and their corresponding rule numbers with police persona
        self.rule_patterns = {
            # Rule #1 - Discord TOS & Community Guidelines
            1: {
                'patterns': [
                    r'\b(discord\.gg|discord\.com/invite|discord\.app/invite)\b',
                    r'\b(steamcommunity\.com|steam\.com)\b',
                    r'\b(bit\.ly|tinyurl|short\.link)\b',
                    r'\b(phishing|scam|hack|exploit)\b',
                    r'\b(raid|raiding|raider)\b'
                ],
                'message': "🚨 **FREEZE!** You're violating Discord's Terms of Service! That's **Rule #1** - step away from the keyboard!"
            },
            
            # Rule #2 - Bot Rules
            2: {
                'patterns': [
                    r'\b(bot abuse|bot spam|bot farming)\b',
                    r'\b(auto|automation|script|macro)\b.*\b(bot|discord)\b',
                    r'\b(alt account|alt acc|multiple accounts)\b.*\b(bot|farming)\b'
                ],
                'message': "🚨 **HALT!** Bot abuse detected! You're under arrest for violating **Rule #2**!"
            },
            
            # Rule #3 - Robbing
            3: {
                'patterns': [
                    r'\b(rob|robbing|heist|heisting|steal|stealing)\b',
                    r'\b(take.*money|steal.*money|rob.*money)\b',
                    r'\b(mafia|mafiabot|robbery)\b'
                ],
                'message': "🚨 **STOP RIGHT THERE!** Robbing is illegal in this jurisdiction! You've broken **Rule #3**!"
            },
            
            # Rule #4 - Racism
            4: {
                'patterns': [
                    r'\b(nigger|nigga|chink|gook|kike|spic|wetback|beaner)\b',
                    r'\b(white trash|black trash|yellow trash)\b',
                    r'\b(monkey|ape|gorilla)\b.*\b(black|african)\b',
                    r'\b(terrorist|bomb|jihad)\b.*\b(muslim|arab|middle east)\b'
                ],
                'message': "🚨 **FREEZE!** That's a hate crime! Racist language violates **Rule #4** - you're under arrest!"
            },
            
            # Rule #5 - Channel Appropriacy
            5: {
                'patterns': [
                    r'\b(general|off-topic|random)\b.*\b(help|support|question)\b',
                    r'\b(help|support)\b.*\b(general|off-topic|random)\b'
                ],
                'message': "🚨 **STOP!** Wrong channel, citizen! Keep topics in their proper place - that's **Rule #5**!"
            },
            
            # Rule #6 - NSFW
            6: {
                'patterns': [
                    r'\b(porn|pornography|xxx|nsfw|nude|naked)\b',
                    r'\b(sex|sexual|fuck|fucking|fucked)\b',
                    r'\b(pussy|dick|cock|penis|vagina|boobs|tits)\b',
                    r'\b(gore|blood|violence|kill|murder|death)\b',
                    r'\b(rape|raping|molest|molesting)\b'
                ],
                'message': "🚨 **HANDS UP!** Inappropriate content detected! NSFW material violates **Rule #6** - you're busted!"
            },
            
            # Rule #7 - Voice Rules
            7: {
                'patterns': [
                    r'\b(ear rape|ear raping|loud noise|screaming)\b',
                    r'\b(music bot|play music|music spam)\b',
                    r'\b(voice hopping|vc hopping|voice chat hopping)\b',
                    r'\b(mic spam|microphone spam)\b'
                ],
                'message': "🚨 **CEASE AND DESIST!** Voice chat violations! You're disturbing the peace - **Rule #7**!"
            },
            
            # Rule #8 - Spam
            8: {
                'patterns': [
                    r'(.{1,5})\1{4,}',  # Repeated characters/words
                    r'(.)\1{10,}',     # Same character repeated 10+ times
                    r'\b(spam|spamming|spammer)\b',
                    r'(.){50,}',       # Very long messages
                    r'[!@#$%^&*()_+]{10,}'  # Excessive special characters
                ],
                'message': "🚨 **STOP SPAMMING!** You're flooding the chat! That's **Rule #8** - cease this activity immediately!"
            },
            
            # Rule #9 - Alternate Accounts
            9: {
                'patterns': [
                    r'\b(alt|alt account|alternate account|second account)\b',
                    r'\b(main|main account|primary account)\b.*\b(alt|alt account)\b',
                    r'\b(ban evasion|evading ban|circumvent ban)\b'
                ],
                'message': "🚨 **IDENTITY FRAUD DETECTED!** Using alternate accounts is against **Rule #9** - you're under investigation!"
            },
            
            # Rule #10 - Begging
            10: {
                'patterns': [
                    r'\b(beg|begging|please give|can i have|need money)\b',
                    r'\b(nitro|discord nitro|premium|vip)\b.*\b(please|give|want)\b',
                    r'\b(poor|broke|no money|need help)\b.*\b(money|coins|cash)\b',
                    r'\b(donate|donation|charity|help me)\b.*\b(money|coins|cash)\b'
                ],
                'message': "🚨 **PANHANDLING IS ILLEGAL!** Begging violates **Rule #10** - keep your hands out of others' pockets!"
            },
            
            # Rule #11 - Advertisement
            11: {
                'patterns': [
                    r'\b(join my server|my server|discord server)\b',
                    r'\b(advertise|advertisement|promote|promotion)\b',
                    r'\b(youtube|youtube\.com|youtu\.be)\b',
                    r'\b(twitch|twitch\.tv)\b',
                    r'\b(instagram|twitter|facebook|tiktok)\b',
                    r'\b(website|site|link|check out)\b.*\b(my|our|this)\b'
                ],
                'message': "🚨 **ILLEGAL ADVERTISING!** Unauthorized promotion detected! That's **Rule #11** - no soliciting!"
            },
            
            # Rule #12 - Common Sense
            12: {
                'patterns': [
                    r'\b(exploit|loophole|workaround|bypass)\b',
                    r'\b(rule break|break rules|ignore rules)\b',
                    r'\b(mod abuse|admin abuse|staff abuse)\b',
                    r'\b(harass|harassment|bully|bullying)\b'
                ],
                'message': "🚨 **CRIMINAL BEHAVIOR!** You're exploiting the system! That violates **Rule #12** - use your common sense!"
            }
        }
    
    def is_user_on_cooldown(self, user_id):
        """Check if user is on cooldown for rule reminders"""
        if user_id in self.cooldown_users:
            if datetime.now() - self.cooldown_users[user_id] < timedelta(seconds=self.cooldown_duration):
                return True
            else:
                del self.cooldown_users[user_id]
        return False
    
    def add_user_cooldown(self, user_id):
        """Add user to cooldown"""
        self.cooldown_users[user_id] = datetime.now()
    
    def check_message_for_rules(self, message_content):
        """Check message content against all rule patterns"""
        message_lower = message_content.lower()
        
        for rule_num, rule_data in self.rule_patterns.items():
            for pattern in rule_data['patterns']:
                if re.search(pattern, message_lower, re.IGNORECASE):
                    return rule_num, rule_data['message']
        
        return None, None
    
    @commands.Cog.listener()
    async def on_message(self, message):
        """Monitor all messages for rule violations"""
        # Debug: Print message content for testing
        print(f"Rule Monitor: Received message '{message.content}' from {message.author.name}")
        
        # Ignore bot messages
        if message.author.bot:
            print(f"Rule Monitor: Ignoring bot message from {message.author.name}")
            return
        
        # Ignore messages from bot owners (disabled for testing)
        # if await self.bot.is_owner(message.author):
        #     print(f"Rule Monitor: Ignoring owner message from {message.author.name}")
        #     return
        
        # Check message for rule violations first
        rule_num, rule_message = self.check_message_for_rules(message.content)
        print(f"Rule Monitor: Checked message, rule_num: {rule_num}, message: {rule_message}")
        
        if rule_num and rule_message:
            print(f"Rule Monitor: Rule violation detected! Rule #{rule_num}")
            
            # Always log the rule violation (regardless of cooldown)
            logging_cog = self.bot.get_cog('ComprehensiveLogging')
            if logging_cog:
                await logging_cog.log_rule_violation(message.author, rule_num, rule_message, message.guild, message.content, message.channel)
            
            # Check if user is on cooldown for sending reminders
            if self.is_user_on_cooldown(message.author.id):
                print(f"Rule Monitor: User {message.author.name} is on cooldown - logged but no reminder sent")
                return
            
            # Add user to cooldown
            self.add_user_cooldown(message.author.id)
            
            # Create rule reminder embed with police persona
            embed = discord.Embed(
                title="🚨 POLICE ALERT",
                description=f"{message.author.mention}, {rule_message}",
                color=0xff0000
            )
            embed.set_footer(text="This is your warning! Next violation may result in disciplinary action!")
            
            # Send the reminder
            try:
                await message.reply(embed=embed, delete_after=30)
                print(f"Rule Monitor: Sent rule reminder for Rule #{rule_num}")
            except discord.Forbidden:
                # If we can't reply, try sending to the channel
                try:
                    await message.channel.send(embed=embed, delete_after=30)
                    print(f"Rule Monitor: Sent rule reminder to channel for Rule #{rule_num}")
                except Exception as e:
                    print(f"Rule Monitor: Failed to send reminder: {e}")
        else:
            print(f"Rule Monitor: No rule violation detected in message")
    
    @commands.command(name='rulecooldown')
    @commands.has_permissions(manage_messages=True)
    async def check_rule_cooldown(self, ctx, user: discord.Member = None):
        """Check if a user is on rule reminder cooldown"""
        if user is None:
            user = ctx.author
        
        if self.is_user_on_cooldown(user.id):
            embed = discord.Embed(
                title="⏰ Rule Cooldown Active",
                description=f"{user.mention} is currently on cooldown for rule reminders.",
                color=0xff9900
            )
        else:
            embed = discord.Embed(
                title="✅ No Cooldown",
                description=f"{user.mention} is not on cooldown for rule reminders.",
                color=0x00ff00
            )
        
        await ctx.reply(embed=embed, delete_after=10)
    
    @commands.command(name='clearrulecooldown')
    @commands.has_permissions(manage_messages=True)
    async def clear_rule_cooldown(self, ctx, user: discord.Member):
        """Clear rule reminder cooldown for a user"""
        if user.id in self.cooldown_users:
            del self.cooldown_users[user.id]
            embed = discord.Embed(
                title="✅ Cooldown Cleared",
                description=f"Rule reminder cooldown cleared for {user.mention}",
                color=0x00ff00
            )
        else:
            embed = discord.Embed(
                title="ℹ️ No Cooldown Found",
                description=f"{user.mention} was not on cooldown.",
                color=0x0099ff
            )
        
        await ctx.reply(embed=embed, delete_after=10)
    
    @commands.command(name='rulepatterns')
    @commands.has_permissions(manage_messages=True)
    async def show_rule_patterns(self, ctx):
        """Show all rule monitoring patterns (for debugging)"""
        embed = discord.Embed(
            title="🔍 Rule Monitoring Patterns",
            description="Current patterns being monitored:",
            color=0x0099ff
        )
        
        for rule_num, rule_data in self.rule_patterns.items():
            patterns_text = "\n".join([f"• `{pattern}`" for pattern in rule_data['patterns'][:3]])  # Show first 3 patterns
            if len(rule_data['patterns']) > 3:
                patterns_text += f"\n• ... and {len(rule_data['patterns']) - 3} more"
            
            embed.add_field(
                name=f"Rule #{rule_num}",
                value=patterns_text,
                inline=False
            )
        
        embed.set_footer(text="Use -rulecooldown to check user cooldowns")
        await ctx.reply(embed=embed)

async def setup(bot):
    await bot.add_cog(RuleMonitor(bot))
