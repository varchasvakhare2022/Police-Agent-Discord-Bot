# Police Agent Discord Bot

A Discord bot for server management with features like moderation, verification, tickets, polls, and more.

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Discord Bot Token

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
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

## 🔧 Features

- **Moderation Commands**: Kick, timeout, ban users
- **Verification System**: Button-based server verification
- **Ticket System**: Create and manage support tickets
- **Self-Role Management**: Users can assign themselves roles
- **Poll System**: Create polls with reactions
- **Statistics**: Bot latency and performance stats
- **Amari Integration**: Level and XP tracking (optional)
- **Custom Prefixes**: Each server can set their own command prefix
- **User Blacklist**: Bot owners can blacklist users from using the bot

## 🛠️ Admin Commands

### Prefix Management
- `prefix` - View current prefix
- `prefix <new_prefix>` - Set custom prefix (max 10 characters)
- `prefix reset` - Reset to default prefix (`-`)

### Blacklist Management (Owner Only)
- `blacklist` - View blacklisted users
- `blacklist <user>` - Add user to blacklist
- `blacklist remove <user>` - Remove user from blacklist

## 📁 Project Structure

```
police-agent/
├── __main__.py          # Main bot file
├── json_storage.py     # JSON file storage system
├── cogs/               # Bot command modules
│   ├── admin.py        # Admin commands (prefix, blacklist)
│   ├── amari.py        # Amari bot integration
│   ├── kick.py         # Kick command
│   ├── owner.py        # Owner-only commands
│   ├── ping_slash.py   # Ping slash command
│   ├── poll_slash.py   # Poll slash command
│   ├── stats.py        # Bot statistics
│   ├── timeout.py      # Timeout command
│   └── verify.py       # Verification system
├── data/               # JSON data storage
│   ├── prefixes.json   # Custom prefixes per server
│   └── blacklist.json  # Blacklisted user IDs
├── requirements.txt    # Python dependencies
├── runtime.txt         # Python version
├── Procfile           # Heroku deployment
└── env_example.txt    # Environment variables template
```

## 🛠️ Configuration

### Required Environment Variables
- `BOT_TOKEN`: Your Discord bot token
- `APPLICATION_ID`: Your Discord application ID
- `GUILD_ID`: Discord server ID for slash commands

### Optional Environment Variables
- `AMARI_TOKEN`: Amari bot API token for level tracking

## 🚀 Deployment

### Heroku
1. Create a Heroku app
2. Set environment variables in Heroku dashboard
3. Deploy using the Procfile

### Other Platforms
The bot can be deployed on any platform that supports Python 3.11+.

## 🔒 Security Notes

- Never commit your `.env` file
- Keep your bot token secure
- Use environment variables for all sensitive data
- Regularly update dependencies

## 📝 Recent Updates

This bot has been updated from a 4-year-old codebase to work with modern Discord.py (2.3.2+) and includes:

- ✅ Updated to Discord.py 2.3.2+
- ✅ Removed hardcoded credentials
- ✅ Fixed deprecated API calls
- ✅ Updated Python version to 3.11.9
- ✅ Modernized code structure
- ✅ Added environment variable support
- ✅ Fixed discriminator usage (Discord removed discriminators)
- ✅ Updated dependencies to latest stable versions
- ✅ Replaced PostgreSQL with JSON file storage
- ✅ Added admin commands for prefix and blacklist management

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.
