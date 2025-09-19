import discord
from discord.ext import commands, tasks
import json
import re
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Tuple
import os
import aiohttp
from collections import defaultdict, deque

class SmartDetection(commands.Cog):
    """AI-like heuristics for spam/scam detection and suspicious patterns"""
    
    def __init__(self, bot):
        self.bot = bot
        self.config_file = "data/smart_detection_config.json"
        self.patterns_file = "data/detection_patterns.json"
        self.whitelist_file = "data/detection_whitelist.json"
        self.config = self._load_config()
        self.patterns = self._load_patterns()
        self.whitelist = self._load_whitelist()
        
        # Runtime tracking
        self.user_join_times = defaultdict(deque)  # Track join patterns
        self.message_history = defaultdict(lambda: defaultdict(deque))  # User message history per guild
        self.suspicious_ips = set()  # Track suspicious IP addresses
        self.scam_domains = self._load_scam_domains()
        
        # Start background tasks
        self.cleanup_tracking.start()
        self.update_scam_domains.start()
    
    def _load_config(self) -> Dict:
        """Load smart detection configuration"""
        default_config = {
            "enabled": True,
            "confidence_threshold": 75,  # Minimum confidence to take action
            "actions": {
                "low_confidence": "warn",      # 50-74%
                "medium_confidence": "timeout", # 75-89%
                "high_confidence": "kick"      # 90%+
            },
            "timeouts": {
                "low": 300,     # 5 minutes
                "medium": 1800, # 30 minutes
                "high": 3600    # 1 hour
            },
            "detection_modules": {
                "crypto_scam": True,
                "phishing": True,
                "fake_nitro": True,
                "suspicious_links": True,
                "discord_invites": True,
                "mass_join_detection": True,
                "behavioral_analysis": True,
                "duplicate_content": True
            },
            "thresholds": {
                "mass_join_count": 5,      # Users joining in timeframe
                "mass_join_window": 30,    # Seconds
                "spam_rate_messages": 5,   # Messages in timeframe
                "spam_rate_window": 10,    # Seconds
                "similarity_threshold": 85, # % similarity for duplicate detection
                "new_account_days": 7,     # Consider account "new" if < X days old
                "min_message_length": 3    # Minimum length to avoid false positives
            },
            "whitelist_bypass": {
                "trusted_roles": [],  # Role IDs that bypass detection
                "trusted_users": []   # User IDs that bypass detection
            }
        }
        
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    loaded_config = json.load(f)
                    # Merge with defaults
                    for key, value in default_config.items():
                        if key not in loaded_config:
                            loaded_config[key] = value
                    return loaded_config
            except (json.JSONDecodeError, FileNotFoundError):
                pass
        
        # Save default config
        os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
        with open(self.config_file, 'w') as f:
            json.dump(default_config, f, indent=2)
        
        return default_config
    
    def _load_patterns(self) -> Dict:
        """Load detection patterns"""
        default_patterns = {
            "crypto_scam": [
                r"(?i)\b(?:free|claim|airdrop|giveaway)\s+(?:bitcoin|btc|ethereum|eth|crypto|nft)\b",
                r"(?i)\b(?:double|triple)\s+your\s+(?:bitcoin|crypto|money)\b",
                r"(?i)\b(?:send|deposit)\s+(?:\d+\.?\d*\s*)?(?:btc|eth|bitcoin|ethereum)\b",
                r"(?i)\bmining\s+(?:pool|farm|rig)\s+(?:free|bonus|profit)\b",
                r"(?i)\b(?:wallet|private\s+key|seed\s+phrase)\s+(?:generator|stealer)\b"
            ],
            "phishing": [
                r"(?i)\b(?:verify|confirm|update)\s+your\s+(?:account|discord|steam|paypal)\b",
                r"(?i)\b(?:click|visit)\s+(?:here|link|below)\s+(?:to|for)\s+(?:claim|verify|get)\b",
                r"(?i)\b(?:urgent|immediate)\s+action\s+required\b",
                r"(?i)\byour\s+account\s+(?:will\s+be|has\s+been)\s+(?:suspended|deleted|banned)\b",
                r"(?i)\b(?:security|suspicious)\s+activity\s+detected\b"
            ],
            "fake_nitro": [
                r"(?i)\b(?:free|gift|claim)\s+(?:discord\s+)?nitro\b",
                r"(?i)\bdiscord\.(?:gift|nitro|com/gifts?)\b",
                r"(?i)\bnitro\s+(?:generator|giveaway|for\s+free)\b",
                r"(?i)\b(?:3\s+months?|year)\s+(?:of\s+)?nitro\s+free\b",
                r"(?i)\bget\s+nitro\s+(?:here|now|free)\b"
            ],
            "suspicious_links": [
                r"(?i)\b(?:bit\.ly|tinyurl|t\.co|short\.link|ow\.ly)\b",
                r"(?i)\b(?:click|visit|go\s+to|check\s+out)\s+(?:this\s+)?link\b",
                r"(?i)\b(?:amazing|incredible|unbelievable)\s+(?:deal|offer|opportunity)\b",
                r"(?i)\b(?:limited\s+time|act\s+fast|hurry\s+up|don't\s+miss)\b",
                r"(?i)\b(?:make\s+money|earn\s+cash|get\s+rich)\s+(?:fast|quick|easy)\b"
            ],
            "general_spam": [
                r"(?i)\b(?:buy|sell|cheap|discount|sale)\s+(?:followers|likes|views|subscribers)\b",
                r"(?i)\b(?:dm|private\s+message)\s+me\s+for\s+(?:more|details|info)\b",
                r"(?i)\b(?:join|visit)\s+my\s+(?:server|discord|channel)\b",
                r"(?i)\b(?:sub4sub|follow4follow|like4like)\b",
                r"(?i)\b(?:self\s+promo|self\s+promotion|shameless\s+plug)\b"
            ]
        }
        
        if os.path.exists(self.patterns_file):
            try:
                with open(self.patterns_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                pass
        
        # Save default patterns
        os.makedirs(os.path.dirname(self.patterns_file), exist_ok=True)
        with open(self.patterns_file, 'w') as f:
            json.dump(default_patterns, f, indent=2)
        
        return default_patterns
    
    def _load_whitelist(self) -> Dict:
        """Load whitelisted domains and patterns"""
        default_whitelist = {
            "domains": [
                "discord.com", "discord.gg", "discordapp.com", "discord.app",
                "youtube.com", "youtu.be", "twitch.tv", "github.com",
                "stackoverflow.com", "reddit.com", "twitter.com", "imgur.com"
            ],
            "patterns": [
                r"(?i)\b(?:official|verified)\s+(?:discord|server|bot)\b",
                r"(?i)\b(?:help|support|tutorial|guide)\b",
                r"(?i)\b(?:documentation|docs|wiki)\b"
            ],
            "invite_whitelist": []  # Whitelisted Discord invite codes
        }
        
        if os.path.exists(self.whitelist_file):
            try:
                with open(self.whitelist_file, 'r') as f:
                    loaded_whitelist = json.load(f)
                    # Merge with defaults
                    for key, value in default_whitelist.items():
                        if key not in loaded_whitelist:
                            loaded_whitelist[key] = value
                    return loaded_whitelist
            except (json.JSONDecodeError, FileNotFoundError):
                pass
        
        # Save default whitelist
        os.makedirs(os.path.dirname(self.whitelist_file), exist_ok=True)
        with open(self.whitelist_file, 'w') as f:
            json.dump(default_whitelist, f, indent=2)
        
        return default_whitelist
    
    def _load_scam_domains(self) -> Set[str]:
        """Load known scam domains"""
        # This would typically be loaded from an external API or updated database
        return {
            "discord-nitro.com", "discоrd.com", "disc0rd.com", "discordnitro.net",
            "steam-community.ru", "steamcommunlty.com", "steam-wallet.com",
            "paypal-verification.net", "paypaI.com", "paypa1.com"
        }
    
    async def _check_admin_bypass(self, user: discord.Member) -> bool:
        """Check if user should bypass all detection"""
        admin_bypass = self.bot.get_cog('AdminBypass')
        if admin_bypass and admin_bypass.is_admin_or_owner(user):
            return True
        
        # Check trusted roles/users
        user_roles = [role.id for role in user.roles]
        if any(role_id in self.config["whitelist_bypass"]["trusted_roles"] for role_id in user_roles):
            return True
        
        if user.id in self.config["whitelist_bypass"]["trusted_users"]:
            return True
        
        return False
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two texts (simple implementation)"""
        # Simple character-based similarity
        text1, text2 = text1.lower(), text2.lower()
        
        if not text1 or not text2:
            return 0.0
        
        # Remove extra whitespace and normalize
        text1 = ' '.join(text1.split())
        text2 = ' '.join(text2.split())
        
        if text1 == text2:
            return 100.0
        
        # Calculate Jaccard similarity on character level
        set1, set2 = set(text1), set(text2)
        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))
        
        return (intersection / union * 100) if union > 0 else 0.0
    
    def _analyze_message_content(self, message: discord.Message) -> Tuple[int, List[str]]:
        """Analyze message content for suspicious patterns"""
        if not self.config["enabled"]:
            return 0, []
        
        content = message.content.lower()
        confidence = 0
        detections = []
        
        # Skip very short messages to avoid false positives
        if len(content.strip()) < self.config["thresholds"]["min_message_length"]:
            return 0, []
        
        # Check whitelist patterns first
        for pattern in self.whitelist["patterns"]:
            if re.search(pattern, content):
                return 0, []  # Whitelisted content
        
        # Check against detection patterns
        for category, patterns in self.patterns.items():
            if not self.config["detection_modules"].get(category, True):
                continue
            
            category_matches = 0
            for pattern in patterns:
                if re.search(pattern, content):
                    category_matches += 1
            
            if category_matches > 0:
                # Calculate confidence based on number of matches
                category_confidence = min(30 + (category_matches * 20), 80)
                confidence += category_confidence
                detections.append(f"{category}: {category_matches} matches")
        
        # Check for suspicious domains
        if self.config["detection_modules"].get("suspicious_links", True):
            urls = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', content)
            for url in urls:
                domain = re.findall(r'://([^/]+)', url)
                if domain:
                    domain = domain[0].lower()
                    if domain in self.scam_domains:
                        confidence += 90
                        detections.append(f"Known scam domain: {domain}")
                    elif domain not in self.whitelist["domains"]:
                        confidence += 20
                        detections.append(f"Unknown domain: {domain}")
        
        # Check for Discord invites
        if self.config["detection_modules"].get("discord_invites", True):
            invite_pattern = r'discord\.gg/([a-zA-Z0-9]+)|discord\.com/invite/([a-zA-Z0-9]+)'
            invites = re.findall(invite_pattern, content)
            for invite_match in invites:
                invite_code = invite_match[0] or invite_match[1]
                if invite_code not in self.whitelist["invite_whitelist"]:
                    confidence += 30
                    detections.append(f"Unauthorized Discord invite: {invite_code}")
        
        return min(confidence, 100), detections
    
    def _analyze_user_behavior(self, user: discord.Member, guild: discord.Guild) -> Tuple[int, List[str]]:
        """Analyze user behavior patterns"""
        confidence = 0
        detections = []
        
        # Check account age
        account_age = (datetime.now(user.created_at.tzinfo) - user.created_at).days
        if account_age < self.config["thresholds"]["new_account_days"]:
            confidence += 25
            detections.append(f"New account ({account_age} days old)")
        
        # Check join time patterns (mass join detection)
        if self.config["detection_modules"].get("mass_join_detection", True):
            guild_id = guild.id
            current_time = datetime.now()
            
            # Clean old entries
            while (self.user_join_times[guild_id] and 
                   current_time - self.user_join_times[guild_id][0] > 
                   timedelta(seconds=self.config["thresholds"]["mass_join_window"])):
                self.user_join_times[guild_id].popleft()
            
            # Add current join
            self.user_join_times[guild_id].append(current_time)
            
            # Check if mass join threshold exceeded
            if len(self.user_join_times[guild_id]) >= self.config["thresholds"]["mass_join_count"]:
                confidence += 40
                detections.append(f"Mass join pattern detected ({len(self.user_join_times[guild_id])} users)")
        
        # Check message spam patterns
        if self.config["detection_modules"].get("behavioral_analysis", True):
            user_messages = self.message_history[guild.id][user.id]
            recent_messages = []
            current_time = datetime.now()
            
            # Get recent messages
            for msg_time, content in user_messages:
                if current_time - msg_time <= timedelta(seconds=self.config["thresholds"]["spam_rate_window"]):
                    recent_messages.append(content)
            
            if len(recent_messages) >= self.config["thresholds"]["spam_rate_messages"]:
                confidence += 35
                detections.append(f"Spam rate exceeded ({len(recent_messages)} messages)")
                
                # Check for duplicate content
                if self.config["detection_modules"].get("duplicate_content", True):
                    duplicates = 0
                    for i, msg1 in enumerate(recent_messages):
                        for msg2 in recent_messages[i+1:]:
                            similarity = self._calculate_similarity(msg1, msg2)
                            if similarity >= self.config["thresholds"]["similarity_threshold"]:
                                duplicates += 1
                    
                    if duplicates > 0:
                        confidence += 25
                        detections.append(f"Duplicate content detected ({duplicates} pairs)")
        
        return min(confidence, 100), detections
    
    async def _take_action(self, message: discord.Message, confidence: int, detections: List[str]):
        """Take appropriate action based on confidence level"""
        if confidence < 50:  # Below threshold, just log
            return
        
        action = None
        timeout_duration = None
        
        if confidence >= 90:
            action = self.config["actions"]["high_confidence"]
            timeout_duration = self.config["timeouts"]["high"]
        elif confidence >= 75:
            action = self.config["actions"]["medium_confidence"]
            timeout_duration = self.config["timeouts"]["medium"]
        else:  # 50-74
            action = self.config["actions"]["low_confidence"]
            timeout_duration = self.config["timeouts"]["low"]
        
        # Delete the message first
        try:
            await message.delete()
        except discord.NotFound:
            pass  # Message already deleted
        except discord.Forbidden:
            pass  # No permission to delete
        
        # Take action on user
        reason = f"Smart detection: {confidence}% confidence. Detections: {', '.join(detections[:3])}"
        
        try:
            if action == "warn":
                # Send warning
                embed = discord.Embed(
                    title="⚠️ Suspicious Content Detected",
                    description="Your message was flagged by our detection system.",
                    color=discord.Color.orange()
                )
                embed.add_field(name="Confidence", value=f"{confidence}%", inline=True)
                embed.add_field(name="Action", value="Warning issued", inline=True)
                
                try:
                    await message.author.send(embed=embed)
                except discord.Forbidden:
                    pass  # Can't DM user
                
            elif action == "timeout" and timeout_duration:
                until = datetime.now() + timedelta(seconds=timeout_duration)
                await message.author.timeout(until, reason=reason)
                
            elif action == "kick":
                await message.author.kick(reason=reason)
        
        except discord.Forbidden:
            pass  # No permission for action
        except Exception as e:
            print(f"Error taking action: {e}")
        
        # Update behavior score
        behavior_cog = self.bot.get_cog('BehaviorScoring')
        if behavior_cog:
            score_penalty = min(-50, -(confidence // 2))  # Higher confidence = more penalty
            behavior_cog.modify_score(
                message.author.id, 
                message.guild.id, 
                score_penalty, 
                f"Smart detection triggered ({confidence}% confidence)"
            )
        
        # Log the action
        logging_cog = self.bot.get_cog('LoggingSystem')
        if logging_cog:
            await logging_cog.log_system_event(
                "smart_detection",
                f"Smart detection triggered: {action} taken",
                message.guild,
                self.bot.user,
                f"User: {message.author.mention}\nConfidence: {confidence}%\nDetections: {', '.join(detections)}\nContent: {message.content[:100]}..."
            )
    
    # Event listeners
    @commands.Cog.listener()
    async def on_message(self, message):
        """Analyze incoming messages for suspicious content"""
        if message.author.bot or not message.guild:
            return
        
        # Check admin bypass
        if await self._check_admin_bypass(message.author):
            return
        
        # Track message for behavioral analysis
        if self.config["detection_modules"].get("behavioral_analysis", True):
            self.message_history[message.guild.id][message.author.id].append(
                (datetime.now(), message.content)
            )
            
            # Keep only last 20 messages per user
            if len(self.message_history[message.guild.id][message.author.id]) > 20:
                self.message_history[message.guild.id][message.author.id].popleft()
        
        # Analyze content
        content_confidence, content_detections = self._analyze_message_content(message)
        
        # Analyze behavior
        behavior_confidence, behavior_detections = self._analyze_user_behavior(message.author, message.guild)
        
        # Combine confidences (weighted average)
        total_confidence = int((content_confidence * 0.7) + (behavior_confidence * 0.3))
        all_detections = content_detections + behavior_detections
        
        # Take action if confidence exceeds threshold
        if total_confidence >= self.config["confidence_threshold"]:
            await self._take_action(message, total_confidence, all_detections)
    
    @commands.Cog.listener()
    async def on_member_join(self, member):
        """Track member joins for mass join detection"""
        if await self._check_admin_bypass(member):
            return
        
        # Analyze new member
        behavior_confidence, behavior_detections = self._analyze_user_behavior(member, member.guild)
        
        # Check if immediate action needed
        if behavior_confidence >= 80:  # High confidence of suspicious join
            try:
                reason = f"Suspicious join pattern: {', '.join(behavior_detections)}"
                await member.kick(reason=reason)
                
                # Log the action
                logging_cog = self.bot.get_cog('LoggingSystem')
                if logging_cog:
                    await logging_cog.log_system_event(
                        "suspicious_join",
                        f"Member kicked on join due to suspicious patterns",
                        member.guild,
                        self.bot.user,
                        f"Member: {member.mention}\nReason: {reason}"
                    )
            except discord.Forbidden:
                pass
    
    # Background tasks
    @tasks.loop(hours=1)
    async def cleanup_tracking(self):
        """Clean up old tracking data"""
        current_time = datetime.now()
        cutoff_time = current_time - timedelta(hours=24)
        
        # Clean message history
        for guild_id in self.message_history:
            for user_id in self.message_history[guild_id]:
                user_messages = self.message_history[guild_id][user_id]
                while user_messages and user_messages[0][0] < cutoff_time:
                    user_messages.popleft()
        
        # Clean join times
        for guild_id in self.user_join_times:
            join_times = self.user_join_times[guild_id]
            while join_times and current_time - join_times[0] > timedelta(hours=1):
                join_times.popleft()
    
    @tasks.loop(hours=6)
    async def update_scam_domains(self):
        """Update scam domains from external sources"""
        try:
            # This would typically fetch from a maintained list
            # For now, we'll use a static update
            new_domains = {
                "discord-nitro.com", "discоrd.com", "disc0rd.com", "discordnitro.net",
                "steam-community.ru", "steamcommunlty.com", "steam-wallet.com",
                "paypal-verification.net", "paypaI.com", "paypa1.com",
                "discord-app.net", "free-nitro.com", "nitro-gen.com"
            }
            self.scam_domains.update(new_domains)
        except Exception as e:
            print(f"Error updating scam domains: {e}")
    
    @cleanup_tracking.before_loop
    @update_scam_domains.before_loop
    async def before_tasks(self):
        """Wait until bot is ready"""
        await self.bot.wait_until_ready()
    
    # Commands for managing smart detection
    @commands.group(name="smartdetect", aliases=["detect"], invoke_without_command=True)
    @commands.has_permissions(administrator=True)
    async def smart_detect(self, ctx):
        """Smart detection system management"""
        embed = discord.Embed(
            title="🔍 Smart Detection System",
            color=discord.Color.blue()
        )
        
        status = "🟢 Enabled" if self.config["enabled"] else "🔴 Disabled"
        embed.add_field(name="Status", value=status, inline=True)
        embed.add_field(name="Confidence Threshold", value=f"{self.config['confidence_threshold']}%", inline=True)
        
        # Show enabled modules
        enabled_modules = [name for name, enabled in self.config["detection_modules"].items() if enabled]
        embed.add_field(name="Active Modules", value=", ".join(enabled_modules) or "None", inline=False)
        
        embed.add_field(name="Commands", 
                       value="`smartdetect toggle` - Enable/disable system\n"
                             "`smartdetect threshold <percent>` - Set confidence threshold\n"
                             "`smartdetect test <text>` - Test detection on text\n"
                             "`smartdetect whitelist` - Manage whitelists\n"
                             "`smartdetect stats` - View detection statistics",
                       inline=False)
        
        await ctx.send(embed=embed)
    
    @smart_detect.command(name="toggle")
    @commands.has_permissions(administrator=True)
    async def smart_detect_toggle(self, ctx):
        """Toggle smart detection system"""
        self.config["enabled"] = not self.config["enabled"]
        
        # Save config
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
        
        status = "enabled" if self.config["enabled"] else "disabled"
        embed = discord.Embed(
            title="Smart Detection Updated",
            description=f"Smart detection system has been **{status}**",
            color=discord.Color.green() if self.config["enabled"] else discord.Color.red()
        )
        
        await ctx.send(embed=embed)
    
    @smart_detect.command(name="threshold")
    @commands.has_permissions(administrator=True)
    async def smart_detect_threshold(self, ctx, threshold: int):
        """Set confidence threshold for taking action"""
        if not 25 <= threshold <= 95:
            await ctx.send("❌ Threshold must be between 25% and 95%!")
            return
        
        old_threshold = self.config["confidence_threshold"]
        self.config["confidence_threshold"] = threshold
        
        # Save config
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
        
        embed = discord.Embed(
            title="Threshold Updated",
            description=f"Confidence threshold changed from {old_threshold}% to {threshold}%",
            color=discord.Color.green()
        )
        
        await ctx.send(embed=embed)
    
    @smart_detect.command(name="test")
    @commands.has_permissions(moderate_members=True)
    async def smart_detect_test(self, ctx, *, text: str):
        """Test smart detection on provided text"""
        # Create a mock message object
        class MockMessage:
            def __init__(self, content, author, guild):
                self.content = content
                self.author = author
                self.guild = guild
        
        mock_message = MockMessage(text, ctx.author, ctx.guild)
        confidence, detections = self._analyze_message_content(mock_message)
        
        embed = discord.Embed(
            title="🔍 Detection Test Results",
            color=discord.Color.blue()
        )
        
        embed.add_field(name="Text", value=f"```{text[:500]}```", inline=False)
        embed.add_field(name="Confidence", value=f"{confidence}%", inline=True)
        
        action = "No action"
        if confidence >= 90:
            action = self.config["actions"]["high_confidence"]
        elif confidence >= 75:
            action = self.config["actions"]["medium_confidence"]
        elif confidence >= 50:
            action = self.config["actions"]["low_confidence"]
        
        embed.add_field(name="Action", value=action.title(), inline=True)
        
        if detections:
            embed.add_field(name="Detections", value="\n".join(detections), inline=False)
        else:
            embed.add_field(name="Detections", value="None", inline=False)
        
        await ctx.send(embed=embed)
    
    @smart_detect.command(name="whitelist")
    @commands.has_permissions(administrator=True)
    async def smart_detect_whitelist(self, ctx, action: str = None, *, item: str = None):
        """Manage detection whitelist"""
        if action is None:
            # Show current whitelist
            embed = discord.Embed(
                title="Detection Whitelist",
                color=discord.Color.blue()
            )
            
            embed.add_field(name="Domains", 
                           value="\n".join(self.whitelist["domains"][:10]) or "None", 
                           inline=True)
            embed.add_field(name="Invite Codes", 
                           value="\n".join(self.whitelist["invite_whitelist"][:10]) or "None", 
                           inline=True)
            
            embed.add_field(name="Commands",
                           value="`whitelist add_domain <domain>` - Add domain\n"
                                 "`whitelist remove_domain <domain>` - Remove domain\n"
                                 "`whitelist add_invite <code>` - Add invite code\n"
                                 "`whitelist remove_invite <code>` - Remove invite code",
                           inline=False)
            
            await ctx.send(embed=embed)
            return
        
        if not item:
            await ctx.send("❌ Please provide an item to add/remove!")
            return
        
        success = False
        
        if action == "add_domain":
            if item not in self.whitelist["domains"]:
                self.whitelist["domains"].append(item)
                success = True
        elif action == "remove_domain":
            if item in self.whitelist["domains"]:
                self.whitelist["domains"].remove(item)
                success = True
        elif action == "add_invite":
            if item not in self.whitelist["invite_whitelist"]:
                self.whitelist["invite_whitelist"].append(item)
                success = True
        elif action == "remove_invite":
            if item in self.whitelist["invite_whitelist"]:
                self.whitelist["invite_whitelist"].remove(item)
                success = True
        
        if success:
            # Save whitelist
            with open(self.whitelist_file, 'w') as f:
                json.dump(self.whitelist, f, indent=2)
            
            await ctx.send(f"✅ Successfully {action.replace('_', ' ')} `{item}`")
        else:
            await ctx.send(f"❌ Invalid action or item already exists/doesn't exist!")

async def setup(bot):
    await bot.add_cog(SmartDetection(bot))
