import discord
from discord.ext import commands
import psutil
import time
import inspect
from datetime import datetime, timedelta

class Dashboard(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.start_time = time.time()
        self.command_count = 0
        self.error_count = 0

    def get_uptime(self):
        """Get bot uptime"""
        uptime_seconds = int(time.time() - self.start_time)
        days = uptime_seconds // 86400
        hours = (uptime_seconds % 86400) // 3600
        minutes = (uptime_seconds % 3600) // 60
        seconds = uptime_seconds % 60
        
        if days > 0:
            return f"{days}d {hours}h {minutes}m {seconds}s"
        elif hours > 0:
            return f"{hours}h {minutes}m {seconds}s"
        elif minutes > 0:
            return f"{minutes}m {seconds}s"
        else:
            return f"{seconds}s"

    def get_memory_usage(self):
        """Get memory usage"""
        process = psutil.Process()
        memory_info = process.memory_info()
        memory_mb = memory_info.rss / 1024 / 1024
        return f"{memory_mb:.1f} MB"

    def get_cpu_usage(self):
        """Get CPU usage"""
        process = psutil.Process()
        cpu_percent = process.cpu_percent()
        return f"{cpu_percent:.1f}%"

    def get_disk_usage(self):
        """Get disk usage"""
        disk_usage = psutil.disk_usage('/')
        used_gb = disk_usage.used / 1024 / 1024 / 1024
        total_gb = disk_usage.total / 1024 / 1024 / 1024
        percent = (used_gb / total_gb) * 100
        return f"{used_gb:.1f} GB / {total_gb:.1f} GB ({percent:.1f}%)"

    @commands.command(name="dashboard")
    @commands.has_permissions(administrator=True)
    async def dashboard(self, ctx: commands.Context):
        """Show comprehensive bot dashboard"""
        
        # Get bot latency
        latency = round(self.bot.latency * 1000)
        
        # Get system metrics
        uptime = self.get_uptime()
        memory = self.get_memory_usage()
        cpu = self.get_cpu_usage()
        disk = self.get_disk_usage()
        
        # Get bot statistics
        guild_count = len(self.bot.guilds)
        user_count = len(self.bot.users)
        channel_count = sum(len(guild.channels) for guild in self.bot.guilds)
        
        # Create main dashboard embed
        embed = discord.Embed(
            title="📊 Police Agent Dashboard",
            description="Real-time bot performance and statistics",
            color=0x9C84EF,
            timestamp=datetime.now()
        )
        
        # Bot Status
        embed.add_field(
            name="🤖 Bot Status",
            value=inspect.cleandoc(
                f"""
                **Status:** 🟢 Online
                **Uptime:** {uptime}
                **Latency:** {latency}ms
                **Commands:** {self.command_count}
                **Errors:** {self.error_count}
                """
            ),
            inline=True
        )
        
        # System Resources
        embed.add_field(
            name="💻 System Resources",
            value=inspect.cleandoc(
                f"""
                **Memory:** {memory}
                **CPU:** {cpu}
                **Disk:** {disk}
                **Python:** 3.11+
                **Discord.py:** 2.3.2+
                """
            ),
            inline=True
        )
        
        # Server Statistics
        embed.add_field(
            name="📈 Server Statistics",
            value=inspect.cleandoc(
                f"""
                **Servers:** {guild_count}
                **Users:** {user_count:,}
                **Channels:** {channel_count:,}
                **Shards:** {self.bot.shard_count}
                """
            ),
            inline=True
        )
        
        # Feature Status
        features = []
        features.append("✅ Moderation System")
        features.append("✅ Anti-Spam Protection")
        features.append("✅ Logging System")
        features.append("✅ Interactive UI")
        features.append("✅ Slash Commands")
        features.append("✅ Help System")
        
        embed.add_field(
            name="🛡️ Features Status",
            value="\n".join(features),
            inline=False
        )
        
        # Recent Activity (simplified)
        embed.add_field(
            name="📊 Recent Activity",
            value=inspect.cleandoc(
                f"""
                **Commands Executed:** {self.command_count}
                **Errors Encountered:** {self.error_count}
                **Success Rate:** {((self.command_count - self.error_count) / max(self.command_count, 1) * 100):.1f}%
                """
            ),
            inline=True
        )
        
        # Bot Information
        embed.add_field(
            name="ℹ️ Bot Information",
            value=inspect.cleandoc(
                f"""
                **Version:** 2.0
                **Created:** 2024
                **Developer:** [Your Name]
                **Support:** [Your Discord Server]
                """
            ),
            inline=True
        )
        
        embed.set_footer(text="Police Agent Bot Dashboard")
        embed.set_thumbnail(url=self.bot.user.avatar.url if self.bot.user.avatar else None)
        
        await ctx.send(embed=embed)

    @commands.command(name="status")
    async def status(self, ctx: commands.Context):
        """Show quick bot status"""
        
        latency = round(self.bot.latency * 1000)
        uptime = self.get_uptime()
        
        embed = discord.Embed(
            title="🟢 Bot Status",
            description=f"Police Agent is online and running!",
            color=0x00ff00
        )
        
        embed.add_field(name="Latency", value=f"{latency}ms", inline=True)
        embed.add_field(name="Uptime", value=uptime, inline=True)
        embed.add_field(name="Servers", value=str(len(self.bot.guilds)), inline=True)
        
        embed.set_footer(text="Use -dashboard for detailed information")
        
        await ctx.send(embed=embed)

    @commands.command(name="ping")
    async def ping(self, ctx: commands.Context):
        """Check bot latency"""
        
        # Send initial message
        start_time = time.time()
        message = await ctx.send("🏓 Pinging...")
        
        # Calculate latency
        end_time = time.time()
        api_latency = round((end_time - start_time) * 1000)
        websocket_latency = round(self.bot.latency * 1000)
        
        embed = discord.Embed(
            title="🏓 Pong!",
            color=0x00ff00
        )
        
        embed.add_field(name="WebSocket", value=f"{websocket_latency}ms", inline=True)
        embed.add_field(name="API", value=f"{api_latency}ms", inline=True)
        embed.add_field(name="Average", value=f"{(websocket_latency + api_latency) // 2}ms", inline=True)
        
        await message.edit(content="", embed=embed)

    @commands.Cog.listener()
    async def on_command(self, ctx):
        """Track command usage"""
        self.command_count += 1

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        """Track command errors"""
        self.error_count += 1
        
        # Log error to logging system
        logging_cog = self.bot.get_cog('LoggingSystem')
        if logging_cog:
            await logging_cog.log_system_event(
                "command_error",
                f"Command error in {ctx.channel.mention}",
                ctx.guild,
                ctx.author,
                f"Command: {ctx.command.name}\nError: {str(error)}"
            )

    @commands.command(name="health")
    @commands.has_permissions(administrator=True)
    async def health_check(self, ctx: commands.Context):
        """Perform health check on bot systems"""
        
        embed = discord.Embed(
            title="🏥 Health Check",
            description="Checking all bot systems...",
            color=0x9C84EF
        )
        
        checks = []
        
        # Check database connectivity
        try:
            # Test JSON storage
            self.bot.storage.get_prefix(ctx.guild.id)
            checks.append("✅ JSON Storage: OK")
        except:
            checks.append("❌ JSON Storage: ERROR")
        
        # Check logging system
        try:
            logging_cog = self.bot.get_cog('LoggingSystem')
            if logging_cog:
                checks.append("✅ Logging System: OK")
            else:
                checks.append("❌ Logging System: NOT LOADED")
        except:
            checks.append("❌ Logging System: ERROR")
        
        # Check anti-spam system
        try:
            antispam_cog = self.bot.get_cog('AntiSpam')
            if antispam_cog:
                checks.append("✅ Anti-Spam System: OK")
            else:
                checks.append("❌ Anti-Spam System: NOT LOADED")
        except:
            checks.append("❌ Anti-Spam System: ERROR")
        
        # Check permissions
        try:
            if ctx.guild.me.guild_permissions.manage_messages:
                checks.append("✅ Permissions: OK")
            else:
                checks.append("⚠️ Permissions: LIMITED")
        except:
            checks.append("❌ Permissions: ERROR")
        
        # Check memory usage
        try:
            memory = self.get_memory_usage()
            if float(memory.split()[0]) < 1000:  # Less than 1GB
                checks.append(f"✅ Memory Usage: {memory}")
            else:
                checks.append(f"⚠️ Memory Usage: {memory} (HIGH)")
        except:
            checks.append("❌ Memory Usage: ERROR")
        
        embed.add_field(
            name="System Checks",
            value="\n".join(checks),
            inline=False
        )
        
        # Overall status
        if all("✅" in check for check in checks):
            embed.color = 0x00ff00
            embed.add_field(name="Overall Status", value="🟢 All systems operational", inline=False)
        elif any("❌" in check for check in checks):
            embed.color = 0xff0000
            embed.add_field(name="Overall Status", value="🔴 Some systems have issues", inline=False)
        else:
            embed.color = 0xffa500
            embed.add_field(name="Overall Status", value="🟡 Some warnings detected", inline=False)
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Dashboard(bot))
