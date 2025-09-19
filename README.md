# 🚔 Police Agent Discord Bot

> **"Keeping Discord servers safe, one command at a time!"**

A powerful, feature-rich Discord moderation bot originally created for my personal public server. This bot has been battle-tested in real-world scenarios and evolved from a 4-year-old codebase into a modern, efficient moderation powerhouse.

![Bot Status](https://img.shields.io/badge/Status-Online-brightgreen)
![Python Version](https://img.shields.io/badge/Python-3.11+-blue)
![Discord.py](https://img.shields.io/badge/Discord.py-2.3.2+-purple)
![License](https://img.shields.io/badge/License-MIT-yellow)

## 🎯 **Why Police Agent?**

After managing a large Discord community, I realized I needed a bot that could handle everything from basic moderation to complex server management. Police Agent was born from this need - a comprehensive solution that combines powerful moderation tools with user-friendly features.

**What makes it special:**
- 🛡️ **Battle-tested** in real server environments
- 🔄 **Modernized** from legacy code to current standards
- 🎨 **Beautiful UI** with embeds and interactive buttons
- ⚡ **Lightning fast** responses and efficient resource usage
- 🔧 **Highly customizable** with per-server settings

## 🚀 **Quick Start**

### Prerequisites
- Python 3.11+
- Discord Bot Token
- Basic Python knowledge

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/police-agent.git
   cd police-agent
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   - Copy `env_example.txt` to `.env`
   - Fill in your configuration:
   ```env
   BOT_TOKEN=your_discord_bot_token
   APPLICATION_ID=your_discord_application_id
   GUILD_ID=your_discord_guild_id
   AMARI_TOKEN=your_amari_bot_token (optional)
   ```

4. **Run the bot**
   ```bash
   python __main__.py
   ```

## 📋 **For Users Who Want to Use This Bot**

### ⚖️ **Terms of Use**

If you want to use Police Agent in your own server, please follow these guidelines:

1. **Give Proper Credits** - Always mention that you're using Police Agent by [Your Name]
2. **Don't Claim Ownership** - This bot is not yours, respect the original creator
3. **Share Improvements** - If you make improvements, consider contributing back
4. **Respect the License** - This project is under MIT License

### 🎨 **How to Give Credits**

**In your server description:**
```
Moderation powered by Police Agent Bot by [Your Name]
```

**In bot status:**
```
Police Agent v2.0 | Created by [Your Name]
```

**In help command:**
```
Bot created by [Your Name] | Police Agent Discord Bot
```

## 🛡️ **Moderation Features**

Police Agent excels at keeping your server safe and organized:

### **🚨 Core Moderation**
- **Smart Timeout System** - Timeout users with custom durations (5s, 5m, 5h, 5d)
- **Intelligent Kick System** - Kick users with role hierarchy protection
- **Ban System** - Ban and unban users with comprehensive ban list management
- **User Blacklist** - Ban users from using the bot entirely
- **Permission Checks** - Automatic role hierarchy and permission validation
- **Comprehensive Logging** - Automatic log channel creation and management
- **Prefix Commands** - Traditional Discord prefix commands for all moderation actions
- **Abuse Prevention** - Cooldowns, rate limiting, and mass action protection

### **🛡️ Advanced Anti-Spam & Scam Protection**
- **Advanced Spam Detection** - Rate limiting and pattern recognition
- **Fake Nitro Link Detection** - Automatically detects and removes scam links
- **Scam Pattern Recognition** - Detects crypto scams, phishing attempts, and more
- **Automatic Moderation** - Auto-mute, delete, or ban based on severity
- **Whitelist System** - Protect trusted roles and channels from false positives
- **Real-time Logging** - Track all anti-spam actions in designated channels
- **Excessive Mention Protection** - Block mass pings and mention spam
- **Duplicate Spam Detection** - Detect copy-paste spam patterns
- **Anti-Raid System** - Auto-kick/ban if X new users join & spam in Y seconds
- **Ghost Ping Detection** - Detect when someone tags and deletes messages
- **CAPTCHA Verification** - Reaction-based verification for new members

### **🧠 AI-Powered Security & Behavior Scoring**
- **Behavior Scoring System** - Track user trust levels with points-based system
- **Automatic Restrictions** - Progressive penalties for low-trust users (slowmode, extra verification, mute)
- **Smart Detection** - AI-like heuristics for detecting scams, phishing, and suspicious behavior
- **Behavioral Analysis** - Account age verification, join pattern detection, and message analysis
- **Dynamic Trust Levels** - 6-tier scoring system from "Excellent" to "Severe" with automatic actions
- **Score Decay** - Inactive users gradually lose points to encourage participation
- **Pattern Recognition** - Detects crypto scams, fake Nitro, Discord invite spam, and phishing attempts
- **Confidence-Based Actions** - Actions scale with detection confidence (warn → timeout → kick)
- **Mass Join Detection** - Automatically detect and prevent coordinated bot attacks
- **Content Similarity** - Detect duplicate/copy-paste spam across messages

### **🎫 Server Management**
- **Ticket System** - Automated support ticket creation with mod-only channels
- **Enhanced Verification** - Button-based verification with auto-role management
- **Advanced Self-Role System** - Dropdown-based role selection with categories
- **Custom Prefixes** - Each server can set their own command prefix
- **Comprehensive Help System** - Paginated help with categories and search

### **📊 Community Features**
- **Interactive Poll System** - Real-time polls with buttons and live results
- **Dashboard & Statistics** - Real-time bot performance, uptime, and system metrics
- **Amari Integration** - Level and XP tracking for gaming communities
- **Rules Display** - Comprehensive server rules with beautiful embeds
- **Error Handling** - Advanced error tracking and debugging tools

### **⚡ Performance & Reliability**
- **Lightning Fast** - Optimized for speed and efficiency
- **JSON Storage** - No database required, simple file-based storage
- **Auto-Recovery** - Handles disconnections and errors gracefully
- **Resource Efficient** - Minimal memory and CPU usage

## 🎮 **Available Commands**

### **Slash Commands** (Modern Discord Interface)
- `/ping` - Check bot statistics and latency
- `/poll <question>` - Create a poll with reactions
- `/antispam <action> <value>` - Configure anti-spam system
- `/whitelist <action> <role>` - Manage anti-spam whitelist
- `/reset-warnings <member>` - Reset spam warnings for a user

### **Prefix Commands** (Traditional Commands)
- `-prefix` - View current prefix
- `-prefix <new_prefix>` - Set custom prefix (max 10 characters)
- `-prefix reset` - Reset to default prefix (`-`)
- `-blacklist` - View blacklisted users
- `-blacklist <user>` - Add user to blacklist (Owner only)
- `-blacklist remove <user>` - Remove user from blacklist (Owner only)
- `-timeout <member> <duration> <reason>` - Timeout a user
- `-untimeout <member> <reason>` - Remove timeout from user
- `-kick <member> <reason>` - Kick a user
- `-ban <member> <reason>` - Ban a user
- `-unban <user_id> <reason>` - Unban a user
- `-banlist` - View banned users
- `-stats` - View bot statistics
- `-dashboard` - Comprehensive bot dashboard
- `-status` - Quick bot status
- `-ping` - Check bot latency
- `-health` - System health check
- `-help` - Paginated help system
- `-commands` - List all commands
- `-poll <question>` - Create a poll
- `-verify` - Send verification message

### **Behavior Scoring Commands**
- `-behavior [member]` - View behavior score for a user
- `-behavior history <member>` - View behavior score history (Moderators only)
- `-behavior modify <member> <change> <reason>` - Manually modify score (Moderators only)
- `-behavior leaderboard` - View server behavior leaderboard
- `-behavior config` - View system configuration (Admins only)

### **Smart Detection Commands**
- `-smartdetect` - View smart detection system status
- `-smartdetect toggle` - Enable/disable smart detection (Admins only)
- `-smartdetect threshold <percent>` - Set confidence threshold (Admins only)
- `-smartdetect test <text>` - Test detection on provided text (Moderators only)
- `-smartdetect whitelist [action] [item]` - Manage detection whitelist (Admins only)
- `-ticket` - Send ticket creation message
- `-selfroles` - Send self-role selection
- `-rules` - Display server rules
- `-scope <command> <roles>` - Set command scopes for dangerous commands
- `-scope-reset <command>` - Reset command scope
- `-scopes` - Show all command scopes
- `-automod <setting> <value>` - Configure advanced auto-moderation
- `-verify-captcha <user>` - Send CAPTCHA verification to user
- `-captcha-verify <code>` - Verify CAPTCHA code
- `-captcha-status` - Check CAPTCHA verification status
- `-captcha-reset <user>` - Reset CAPTCHA verification
- `-captcha-stats` - Show CAPTCHA statistics

### **🔗 Slash Commands**
- `/kick <member> <reason>` - Kick a user
- `/ban <member> <reason>` - Ban a user
- `/timeout <member> <duration> <reason>` - Timeout a user
- `/untimeout <member> <reason>` - Remove timeout
- `/unban <user_id> <reason>` - Unban a user
- `/banlist` - View banned users
- `/ping` - Check bot latency
- `/poll <question>` - Create a poll
- `/antispam <action> <value>` - Configure anti-spam
- `/whitelist <action> <role>` - Manage whitelist
- `/reset-warnings <member>` - Reset spam warnings
- `-time` - Show current time
- `-amari <user>` - Check Amari bot level/XP
- `-antispam` - Configure anti-spam system
- `-antispam enable/disable` - Enable/disable anti-spam
- `-antispam threshold <number>` - Set spam threshold
- `-antispam logchannel <channel>` - Set log channel
- `-antispam whitelist <role>` - Add role to whitelist
- `-antispam unwhitelist <role>` - Remove role from whitelist
- `-antispam reset <member>` - Reset spam warnings

## 🏗️ **Project Structure**

```
police-agent/
├── __main__.py              # 🤖 Main bot file with core functionality
├── json_storage.py          # 💾 JSON file storage system
├── cogs/                    # 🔧 Bot command modules
│   ├── admin.py            # 👑 Admin commands (prefix, blacklist)
│   ├── amari.py            # 🎮 Amari bot integration
│   ├── antispam.py         # 🛡️ Anti-spam and scam detection
│   ├── antispam.py         # 🛡️ Anti-spam prefix commands
│   ├── ban.py              # 🚫 Ban and unban commands
│   ├── dashboard.py        # 📊 Bot dashboard and metrics
│   ├── error_handler.py    # 🐛 Error handling and debugging
│   ├── help_system.py      # 📖 Paginated help system
│   ├── kick.py             # 👢 Kick command
│   ├── logging.py          # 📝 Comprehensive logging system
│   ├── moderation.py       # 🔗 Moderation prefix commands
│   ├── owner.py            # 🔐 Owner-only commands
│   ├── ping.py             # 📡 Ping prefix command
│   ├── poll.py             # 📊 Poll prefix command
│   ├── polls_enhanced.py   # 🎯 Enhanced interactive polls
│   ├── selfroles_enhanced.py # 🎭 Enhanced self-role system
│   ├── stats.py            # 📈 Bot statistics
│   ├── timeout.py          # ⏰ Timeout command
│   ├── verification_enhanced.py # ✅ Enhanced verification
│   ├── abuse_prevention.py # 🛡️ Abuse prevention and cooldowns
│   ├── command_scopes.py   # 🔒 Command scopes for dangerous commands
│   ├── advanced_automod.py # 🛡️ Advanced auto-moderation system
│   ├── captcha_verification.py # 🔐 CAPTCHA verification system
│   ├── behavior_scoring.py # 🧠 User behavior scoring system
│   ├── smart_detection.py  # 🔍 AI-like spam/scam detection
│   ├── detailed_mod_logs.py # 📋 Detailed moderation logging
│   ├── mass_management.py  # ⚡ Mass management tools
│   ├── server_security.py  # 🔒 Server security features
│   └── admin_bypass.py     # 👑 Admin/owner bypass system
├── data/                    # 📁 JSON data storage
│   ├── prefixes.json       # 🏷️ Custom prefixes per server
│   ├── blacklist.json      # 🚫 Blacklisted user IDs
│   ├── antispam_config.json # 🛡️ Anti-spam configuration
│   ├── log_channels.json   # 📝 Log channel IDs per server
│   ├── command_scopes.json # 🔒 Command scopes per server
│   ├── advanced_automod.json # 🛡️ Advanced auto-moderation config
│   ├── captcha_sessions.json # 🔐 CAPTCHA verification sessions
│   ├── behavior_scores.json # 🧠 User behavior scores per server
│   ├── behavior_config.json # ⚙️ Behavior scoring system configuration
│   ├── smart_detection_config.json # 🔍 Smart detection system settings
│   ├── detection_patterns.json # 🎯 Scam/spam detection patterns
│   └── detection_whitelist.json # ✅ Detection system whitelists
├── requirements.txt         # 📦 Python dependencies
├── Procfile                # 🚀 Heroku deployment config
└── README.md               # 📖 This file
```

## 🚀 **Deployment Options**

### **☁️ Cloud Hosting (Recommended)**

**Railway** - Perfect for Police Agent:
```bash
# 1. Connect your GitHub repo to Railway
# 2. Set environment variables
# 3. Deploy automatically!
```

**Render** - Great alternative:
```bash
# 1. Connect GitHub repo
# 2. Set environment variables  
# 3. Deploy with persistent storage
```

### **🖥️ Self-Hosting**

**VPS/Cloud Server:**
```bash
git clone https://github.com/YOUR_USERNAME/police-agent.git
cd police-agent
pip install -r requirements.txt
python __main__.py
```

## ⚙️ **Configuration**

### **Required Environment Variables**
- `BOT_TOKEN` - Your Discord bot token
- `APPLICATION_ID` - Your Discord application ID  
- `GUILD_ID` - Discord server ID for bot operations

### **Optional Environment Variables**
- `AMARI_TOKEN` - Amari bot API token for level tracking

## 🔒 **Security & Best Practices**

- 🚫 **Never commit** your `.env` file
- 🔐 **Keep your bot token** secure and private
- 🌍 **Use environment variables** for all sensitive data
- 🔄 **Regularly update** dependencies for security patches
- 📊 **Monitor bot performance** and logs

## 📈 **The Evolution Story**

Police Agent started as a simple 4-year-old Discord bot and evolved into a modern moderation powerhouse:

### **🔄 Modernization Journey**
- ✅ **Updated** from Discord.py 1.x to 2.3.2+
- ✅ **Removed** hardcoded credentials for security
- ✅ **Fixed** deprecated API calls and methods
- ✅ **Upgraded** Python version to 3.11.9
- ✅ **Modernized** code structure and patterns
- ✅ **Added** environment variable support
- ✅ **Fixed** discriminator usage (Discord removed discriminators)
- ✅ **Replaced** PostgreSQL with efficient JSON storage
- ✅ **Added** comprehensive admin commands

### **🎯 Real-World Testing**
This bot has been battle-tested in:
- 🏢 **Large Discord communities** (1000+ members)
- 🎮 **Gaming servers** with active moderation needs
- 📚 **Educational servers** requiring organized management
- 🎪 **Public servers** with diverse user bases

## 🤝 **Contributing**

Want to improve Police Agent? We'd love your help!

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

## 📄 **License**

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

## 🙏 **Acknowledgments**

- **Discord.py** community for the amazing library
- **All contributors** who helped improve this bot
- **Beta testers** who provided valuable feedback
- **The Discord community** for inspiration and support

---

<div align="center">

**Made with ❤️ for the Discord community**

*Police Agent - Keeping servers safe since 2024*

[![GitHub stars](https://img.shields.io/github/stars/YOUR_USERNAME/police-agent?style=social)](https://github.com/YOUR_USERNAME/police-agent)
[![GitHub forks](https://img.shields.io/github/forks/YOUR_USERNAME/police-agent?style=social)](https://github.com/YOUR_USERNAME/police-agent)

</div>
