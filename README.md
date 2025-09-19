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
- **User Blacklist** - Ban users from using the bot entirely
- **Permission Checks** - Automatic role hierarchy and permission validation

### **🎫 Server Management**
- **Ticket System** - Automated support ticket creation with mod-only channels
- **Verification System** - One-click server verification with custom roles
- **Self-Role Management** - Users can assign themselves roles via buttons
- **Custom Prefixes** - Each server can set their own command prefix

### **📊 Community Features**
- **Poll System** - Create interactive polls with custom reactions
- **Statistics Tracking** - Real-time bot performance and server stats
- **Amari Integration** - Level and XP tracking for gaming communities
- **Rules Display** - Comprehensive server rules with beautiful embeds

### **⚡ Performance & Reliability**
- **Lightning Fast** - Optimized for speed and efficiency
- **JSON Storage** - No database required, simple file-based storage
- **Auto-Recovery** - Handles disconnections and errors gracefully
- **Resource Efficient** - Minimal memory and CPU usage

## 🎮 **Available Commands**

### **Slash Commands** (Modern Discord Interface)
- `/ping` - Check bot statistics and latency
- `/poll <question>` - Create a poll with reactions

### **Prefix Commands** (Traditional Commands)
- `-prefix` - View current prefix
- `-prefix <new_prefix>` - Set custom prefix (max 10 characters)
- `-prefix reset` - Reset to default prefix (`-`)
- `-blacklist` - View blacklisted users
- `-blacklist <user>` - Add user to blacklist (Owner only)
- `-blacklist remove <user>` - Remove user from blacklist (Owner only)
- `-timeout <member> <duration> <reason>` - Timeout a user
- `-kick <member> <reason>` - Kick a user
- `-stats` - View bot statistics
- `-poll <question>` - Create a poll
- `-verify` - Send verification message
- `-ticket` - Send ticket creation message
- `-selfroles` - Send self-role selection
- `-rules` - Display server rules
- `-time` - Show current time
- `-amari <user>` - Check Amari bot level/XP

## 🏗️ **Project Structure**

```
police-agent/
├── __main__.py              # 🤖 Main bot file with core functionality
├── json_storage.py          # 💾 JSON file storage system
├── cogs/                    # 🔧 Bot command modules
│   ├── admin.py            # 👑 Admin commands (prefix, blacklist)
│   ├── amari.py            # 🎮 Amari bot integration
│   ├── kick.py             # 👢 Kick command
│   ├── owner.py            # 🔐 Owner-only commands
│   ├── ping_slash.py       # 📡 Ping slash command
│   ├── poll_slash.py       # 📊 Poll slash command
│   ├── stats.py            # 📈 Bot statistics
│   ├── timeout.py          # ⏰ Timeout command
│   └── verify.py           # ✅ Verification system
├── data/                    # 📁 JSON data storage
│   ├── prefixes.json       # 🏷️ Custom prefixes per server
│   └── blacklist.json      # 🚫 Blacklisted user IDs
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
- `GUILD_ID` - Discord server ID for slash commands

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
