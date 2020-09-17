import json
import os
import discord
import aiohttp
import asyncio
import math
from dotenv import load_dotenv
from datetime import datetime
from discord.ext import commands
from utils import customerrors

load_dotenv()
env_write = ["TOKEN=YOUR_BOT_TOKEN",
             "OWNER_ID=YOUR_ID_HERE",
             "PG_USER=POSTGRES_USERNAME",
             "PG_PASSWORD=POSTGRES_PASSWORD",
             "PG_DATABASE=POSTGRES_DATABASE",
             "PG_HOST=POSTGRES_HOST",
             "UPDATES_CHANNEL=CHANNEL_ID_HERE",
             "LAVALINK_IP=IP_ADDR",
             "LAVALINK_PORT=PORT",
             "LAVALINK_PASSWORD=DEFAULT_STRING",
             "CAT_API=API_KEY_FROM_CAT_API",
             "IMGUR_API=API_KEY_FROM_IMGUR",
             "REDDIT_CLIENT_ID=CLIENT_ID_FROM_REDDIT_API",
             "REDDIT_CLIENT_SECRET=CLIENT_SECRET_FROM_REDDIT_API",
             "USER_AGENT=YOUR_USER_AGENT",
             "TENOR_API=API_KEY_FROM_TENOR",
             "GITHUB_TOKEN=PERSONAL_ACCESS_TOKEN"]
default_env = ["YOUR_BOT_TOKEN",
               "YOUR_ID_HERE",
               "POSTGRES_USERNAME",
               "POSTGRES_PASSWORD",
               "POSTGRES_DATABASE",
               "POSTGRES_HOST",
               "CHANNEL_ID_HERE",
               "IP_ADDR",
               "PORT",
               "DEFAULT_STRING",
               "API_KEY_FROM_CAT_API",
               "API_KEY_FROM_IMGUR",
               "CLIENT_ID_FROM_REDDIT_API",
               "CLIENT_SECRET_FROM_REDDIT_API",
               "YOUR_USER_AGENT",
               "API_KEY_FROM_TENOR",
               "PERSONAL_ACCESS_TOKEN"]


class GlobalCMDS:

    def __init__(self, bot: commands.AutoShardedBot = None):
        self.version = "v2.0.0-RC.1"
        self.bot = bot
        if bot:
            self.db = self.bot.db

    def init_env(self):
        if not os.path.exists('.env'):
            with open('./.env', 'w') as f:
                f.write("\n".join(env_write))
                return False
        return True

    def env_check(self, key: str):
        if not self.init_env() or os.getenv(key) in default_env:
            return False
        return os.getenv(key)

    async def smart_delete(self, message: discord.Message):
        if message.guild and message.guild.me.guild_permissions.manage_messages:
            try:
                await message.delete()
            except Exception:
                pass

    async def timeout(self, ctx: commands.Context, title: str, timeout: int) -> discord.Message:
        embed = discord.Embed(title=f"{title.title()} Timed Out",
                              description=f"{ctx.author.mention}, your {title} timed out after {timeout} seconds"
                              " due to inactivity",
                              color=discord.Color.dark_red())
        return await ctx.channel.send(embed=embed, delete_after=10)

    async def cancelled(self, ctx: commands.Context, title: str) -> discord.Message:
        embed = discord.Embed(title=f"{title.title()} Cancelled",
                              description=f"{ctx.author.mention}, your {title} was cancelled",
                              color=discord.Color.dark_red())
        return await ctx.channel.send(embed=embed, delete_after=10)

    async def panel_deleted(self, ctx: commands.Context, title: str) -> discord.Message:
        embed = discord.Embed(title=f"{title.title()} Cancelled",
                              description=f"{ctx.author.mention}, your {title} was cancelled because the panel was "
                              "deleted or could not be found",
                              color=discord.Color.dark_red())
        return await ctx.channel.send(embed=embed, delete_after=10)

    async def prefix(self, ctx):
        if not ctx.guild:
            return "m?"

        async with self.db.acquire() as con:
            prefix = await con.fetchval(f"SELECT custom_prefix FROM guild_mb WHERE guild_id = {ctx.guild.id}")
            return prefix

    @staticmethod
    def truncate(number: float, decimal_places: int):
        stepper = 10.0 ** decimal_places
        return math.trunc(stepper * number) / stepper
