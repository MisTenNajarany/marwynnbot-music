import json
import os
import discord
import aiohttp
from discord.ext import commands
import asyncio

env_write = ["TOKEN=YOUR_BOT_TOKEN",
             "OWNER_ID=YOUR_ID_HERE",
             "LAVALINK_IP=IP_ADDR",
             "LAVALINK_PORT=PORT",
             "LAVALINK_PASSWORD=DEFAULT_STRING",
             "MARWYNNBOT_ID=MB_CLIENT_ID"]
default_env = ["YOUR_BOT_TOKEN",
               "YOUR_ID_HERE",
               "IP_ADDR",
               "PORT",
               "DEFAULT_STRING",
               "MB_CLIENT_ID"]


class MBConnectedError(commands.CommandError):
    pass


class GlobalCMDS:

    def __init__(self):
        self.version = "v1.1.4"

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

    def json_load(self, filenamepath: str, init: dict):
        if not os.path.exists(filenamepath):
            with open(filenamepath, 'w') as f:
                json.dump(init, f, indent=4)

    def prefix(self, ctx):
        if not ctx.guild:
            return "m?"

        with open('db/prefixes.json', 'r') as f:
            prefixes = json.load(f)

        return prefixes.get(str(ctx.guild.id), 'm?')