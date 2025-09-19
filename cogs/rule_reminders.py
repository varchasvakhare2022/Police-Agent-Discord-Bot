import discord
from discord.ext import commands
import json
import os
import re
from datetime import datetime, timedelta

class RuleReminderSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.rules_file = 'data/rules.json'
        self.violations_file = 'data/violations.json'
        
        # Ensure data directory exists
        os.makedirs('data', exist_ok=True)
        
        # Load rules and violations
        self.load_data()
        
        # Default rules if none exist
        if not self.rules:
            self.setup_default_rules()
    
    def load_data(self):
        """Load rules and violation tracking from JSON files"""
        # Load rules
        if os.path.exists(self.rules_file):
            try:
                with open(self.rules_file, 'r') as f:
                    self.rules = json.load(f)
            except:
                self.rules = {}
        else:
            self.rules = {}
        
        # Load violations tracking
        if os.path.exists(self.violations_file):
            try:
                with open(self.violations_file, 'r') as f:
                    self.violations = json.load(f)
            except:
                self.violations = {}
        else:
            self.violations = {}
    
    def save_data(self):
        """Save rules and violations to JSON files"""
        with open(self.rules_file, 'w') as f:
            json.dump(self.rules, f, indent=2)
        
        with open(self.violations_file, 'w') as f:
            json.dump(self.violations, f, indent=2)
    
    def setup_default_rules(self):
        """Setup default rules for common violations"""
        self.rules = {
            "spam": {
                "keywords": ["spam", "repeated", "same message", "flooding"],
                "response": "🚨 **Rule Violation: Spam**\nPlease don't spam messages. Wait before sending multiple messages.",
                "severity": "warning"
            },
            "profanity": {
                "keywords": ["bad word", "curse", "inappropriate language", "swearing"],
                "response": "🚨 **Rule Violation: Inappropriate Language**\nPlease keep language appropriate for all ages.",
                "severity": "warning"
            },
            "self_promotion": {
                "keywords": ["discord.gg", "join my server", "subscribe", "follow me", "check out my"],
                "response": "🚨 **Rule Violation: Self-Promotion**\nNo advertising or self-promotion without permission.",
                "severity": "warning"
            },
            "nsfw": {
                "keywords": ["nsfw", "adult content", "inappropriate image", "explicit"],
                "response": "🚨 **Rule Violation: NSFW Content**\nNo NSFW content allowed in this server.",
                "severity": "warning"
            },
            "harassment": {
                "keywords": ["harass", "bully", "threaten", "hate speech", "discrimination"],
                "response": "🚨 **Rule Violation: Harassment**\nHarassment, bullying, or hate speech is not tolerated.",
                "severity": "warning"
            },
            "caps": {
                "keywords": ["ALL CAPS", "excessive caps", "shouting"],
                "response": "🚨 **Rule Violation: Excessive Caps**\nPlease don't use excessive caps. It's considered shouting.",
                "severity": "warning"
            }
        }
        self.save_data()
    
    def detect_violation(self, message_content):
        """Detect rule violations in message content"""
        content_lower = message_content.lower()
        violations = []
        
        for rule_name, rule_data in self.rules.items():
            # Check keywords
            for keyword in rule_data["keywords"]:
                if keyword.lower() in content_lower:
                    violations.append({
                        "rule": rule_name,
                        "response": rule_data["response"],
                        "severity": rule_data["severity"],
                        "keyword": keyword
                    })
                    break  # Only one violation per rule
        
        # Check for caps spam (more than 70% caps)
        if len(message_content) > 10:
            caps_count = sum(1 for c in message_content if c.isupper())
            caps_percentage = (caps_count / len(message_content)) * 100
            if caps_percentage > 70:
                violations.append({
                    "rule": "caps",
                    "response": "🚨 **Rule Violation: Excessive Caps**\nPlease don't use excessive caps. It's considered shouting.",
                    "severity": "warning",
                    "keyword": "excessive caps"
                })
        
        # Check for spam (repeated characters)
        if len(message_content) > 5:
            # Check for repeated characters (like "aaaaaa" or "!!!!!!")
            repeated_pattern = re.compile(r'(.)\1{4,}')
            if repeated_pattern.search(message_content):
                violations.append({
                    "rule": "spam",
                    "response": "🚨 **Rule Violation: Spam**\nPlease don't spam repeated characters.",
                    "severity": "warning",
                    "keyword": "repeated characters"
                })
        
        return violations
    
    def track_violation(self, user_id, rule_name):
        """Track violations for rate limiting"""
        user_id = str(user_id)
        current_time = datetime.now().isoformat()
        
        if user_id not in self.violations:
            self.violations[user_id] = []
        
        self.violations[user_id].append({
            "rule": rule_name,
            "timestamp": current_time
        })
        
        # Keep only last 24 hours of violations
        cutoff_time = datetime.now() - timedelta(hours=24)
        self.violations[user_id] = [
            v for v in self.violations[user_id]
            if datetime.fromisoformat(v["timestamp"]) > cutoff_time
        ]
        
        self.save_data()
    
    def should_remind(self, user_id, rule_name):
        """Check if we should send a reminder (rate limiting)"""
        user_id = str(user_id)
        
        if user_id not in self.violations:
            return True
        
        # Count violations in last hour
        cutoff_time = datetime.now() - timedelta(hours=1)
        recent_violations = [
            v for v in self.violations[user_id]
            if datetime.fromisoformat(v["timestamp"]) > cutoff_time
        ]
        
        # Don't remind if user has 3+ violations in last hour
        return len(recent_violations) < 3
    
    @commands.Cog.listener()
    async def on_message(self, message):
        """Automatically detect rule violations"""
        # Ignore bots and empty messages
        if message.author.bot or not message.content:
            return
        
        # Detect violations
        violations = self.detect_violation(message.content)
        
        if violations:
            user_id = message.author.id
            
            for violation in violations:
                rule_name = violation["rule"]
                
                # Check if we should remind (rate limiting)
                if self.should_remind(user_id, rule_name):
                    # Track violation
                    self.track_violation(user_id, rule_name)
                    
                    # Send reminder
                    embed = discord.Embed(
                        title="⚠️ Rule Reminder",
                        description=violation["response"],
                        color=0xffaa00,
                        timestamp=datetime.now()
                    )
                    embed.add_field(
                        name="User",
                        value=message.author.mention,
                        inline=True
                    )
                    embed.add_field(
                        name="Rule",
                        value=rule_name.title(),
                        inline=True
                    )
                    embed.set_footer(text="Please follow the server rules!")
                    
                    await message.channel.send(embed=embed)
                    
                    # Only send one reminder per message
                    break
    
    @commands.command(name='add_rule')
    @commands.has_permissions(manage_messages=True)
    async def add_rule(self, ctx, rule_name: str, *, rule_config: str):
        """Add a new rule for automatic detection"""
        try:
            # Parse rule config (format: keywords|response|severity)
            parts = rule_config.split('|')
            if len(parts) != 3:
                await ctx.send("❌ Format: `keywords|response|severity`\nExample: `spam,repeated|Don't spam!|warning`")
                return
            
            keywords, response, severity = parts
            
            self.rules[rule_name.lower()] = {
                "keywords": [k.strip() for k in keywords.split(',')],
                "response": response.strip(),
                "severity": severity.strip()
            }
            
            self.save_data()
            await ctx.send(f"✅ Added rule: **{rule_name}**")
            
        except Exception as e:
            await ctx.send(f"❌ Error adding rule: {str(e)}")
    
    @commands.command(name='remove_rule')
    @commands.has_permissions(manage_messages=True)
    async def remove_rule(self, ctx, rule_name: str):
        """Remove a rule"""
        rule_name = rule_name.lower()
        
        if rule_name in self.rules:
            del self.rules[rule_name]
            self.save_data()
            await ctx.send(f"✅ Removed rule: **{rule_name}**")
        else:
            await ctx.send(f"❌ Rule **{rule_name}** not found.")
    
    @commands.command(name='list_rules')
    async def list_rules(self, ctx):
        """List all configured rules"""
        if not self.rules:
            await ctx.send("No rules configured.")
            return
        
        embed = discord.Embed(
            title="📋 Configured Rules",
            color=0x0099ff
        )
        
        for rule_name, rule_data in self.rules.items():
            keywords = ", ".join(rule_data["keywords"][:3])  # Show first 3 keywords
            if len(rule_data["keywords"]) > 3:
                keywords += "..."
            
            embed.add_field(
                name=f"Rule: {rule_name.title()}",
                value=f"**Keywords:** {keywords}\n**Severity:** {rule_data['severity']}",
                inline=True
            )
        
        await ctx.send(embed=embed)
    
    @commands.command(name='rule_violations')
    @commands.has_permissions(manage_messages=True)
    async def check_violations(self, ctx, user: discord.Member = None):
        """Check violation history for a user"""
        user = user or ctx.author
        user_id = str(user.id)
        
        if user_id not in self.violations or not self.violations[user_id]:
            await ctx.send(f"{user.mention} has no recent violations.")
            return
        
        # Get violations from last 24 hours
        cutoff_time = datetime.now() - timedelta(hours=24)
        recent_violations = [
            v for v in self.violations[user_id]
            if datetime.fromisoformat(v["timestamp"]) > cutoff_time
        ]
        
        if not recent_violations:
            await ctx.send(f"{user.mention} has no violations in the last 24 hours.")
            return
        
        embed = discord.Embed(
            title=f"⚠️ Violations for {user.display_name}",
            color=0xffaa00,
            timestamp=datetime.now()
        )
        
        # Count violations by rule
        rule_counts = {}
        for violation in recent_violations:
            rule = violation["rule"]
            rule_counts[rule] = rule_counts.get(rule, 0) + 1
        
        for rule, count in rule_counts.items():
            embed.add_field(
                name=f"Rule: {rule.title()}",
                value=f"Violations: {count}",
                inline=True
            )
        
        embed.set_footer(text=f"Total violations in last 24h: {len(recent_violations)}")
        await ctx.send(embed=embed)
    
    @commands.command(name='clear_violations')
    @commands.has_permissions(administrator=True)
    async def clear_violations(self, ctx, user: discord.Member):
        """Clear violation history for a user (admin only)"""
        user_id = str(user.id)
        
        if user_id in self.violations:
            violation_count = len(self.violations[user_id])
            del self.violations[user_id]
            self.save_data()
            await ctx.send(f"✅ Cleared {violation_count} violations for {user.mention}")
        else:
            await ctx.send(f"{user.mention} has no violations to clear.")

async def setup(bot):
    await bot.add_cog(RuleReminderSystem(bot))
