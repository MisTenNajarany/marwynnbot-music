import asyncio
import json
import logging
import math
import os
import random
import re
import socket
import sys
from datetime import datetime

import asyncpg
import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv
from lavalink.exceptions import NodeException

from utils import customerrors, globalcommands

try:
    import uvloop
except ImportError:
    pass
else:
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

gcmds = globalcommands.GlobalCMDS()
ALL_CUSTOMERRORS = [
    customerrors.PremiumError,
    customerrors.MBConnectedError,
    customerrors.NoBoundChannel,
    customerrors.NotBoundChannel,
]
version = f"Running MarwynnBot Music {gcmds.version}"

if os.path.exists('discord.log'):
    os.remove('discord.log')

logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)


async def get_prefix(self: commands.AutoShardedBot, message):
    if not message.guild:
        extras = ('mbm ', 'mBm ', 'mbM', 'mBM', 'Mbm ', 'MBm ', 'MbM', 'MBM', 'm?')
    else:
        async with self.db.acquire() as con:
            prefix = await con.fetchval(f"SELECT custom_prefix from guild WHERE guild_id = {message.guild.id}")
        extras = (
            f'{prefix}', 'mbm ', 'mBm ', 'mbM', 'mBM', 'Mbm ', 'MBm ', 'MbM', 'MBM', 'm?')
    return commands.when_mentioned_or(*extras)(self, message)


async def run(uptime):
    credentials = {
        "user": os.getenv("PG_USER"),
        "password": os.getenv("PG_PASSWORD"),
        "database": os.getenv("PG_DATABASE"),
        "host": os.getenv("PG_HOST")
    }

    db = await asyncpg.create_pool(**credentials)
    await db.execute("CREATE TABLE IF NOT EXISTS guild_mb(guild_id bigint PRIMARY KEY, custom_prefix text)")

    description = "A music bot for Discord base on MarwynnBot"
    startup = discord.Activity(name="Starting Up...", type=discord.ActivityType.playing)
    intents = discord.Intents.all()
    bot = Bot(command_prefix=get_prefix, help_command=None, shard_count=1, description=description, db=db,
              fetch_offline_members=True, status=discord.Status.online, activity=startup, uptime=uptime, intents=intents)

    try:
        await bot.start(gcmds.env_check("TOKEN"))
    except KeyboardInterrupt:
        await db.close()
        await bot.close()


class Bot(commands.AutoShardedBot):
    def __init__(self, **kwargs):
        global gcmds
        super().__init__(
            command_prefix=kwargs['command_prefix'],
            help_command=kwargs["help_command"],
            shard_count=kwargs['shard_count'],
            description=kwargs["description"],
            fetch_offline_members=kwargs['fetch_offline_members'],
            status=kwargs['status'],
            activity=kwargs['activity'],
            intents=kwargs['intents']
        )
        self.uptime = kwargs['uptime']
        self.db = kwargs.pop("db")
        gcmds = globalcommands.GlobalCMDS(bot=self)
        func_checks = (self.check_blacklist, self.disable_dm_exec)
        func_listen = (self.on_message, self.on_command_error, self.on_guild_join)
        for func in func_checks:
            self.add_check(func)
        for func in func_listen:
            self.event(func)
        cogs = [filename[:-3] for filename in os.listdir('./cogs') if filename.endswith(".py")]
        for cog in sorted(cogs):
            self.load_extension(f'cogs.{cog}')
            print(f"Cog \"{cog}\" has been loaded")
        self.loop.create_task(self.all_loaded())

    @tasks.loop(seconds=120)
    async def status(self):
        await self.wait_until_ready()
        at = await self.get_aliases()
        activity1 = discord.Activity(name="m?h for help!", type=discord.ActivityType.listening)
        activity2 = discord.Activity(name="Invite MarwynnBot!", type=discord.ActivityType.playing)
        activity3 = discord.Activity(name=f"MarwynnBot Music {gcmds.version}", type=discord.ActivityType.playing)
        activityList = [activity1, activity2, activity3]
        activity = random.choice(activityList)
        await self.change_presence(status=discord.Status.online, activity=activity)

    async def on_message(self, message):
        await self.wait_until_ready()
        await self.process_commands(message)

    async def check_blacklist(self, ctx):
        if not ctx.guild:
            return True

        async with self.db.acquire() as con:
            blist = await con.fetch(f"SELECT type FROM blacklist WHERE id = {ctx.author.id} OR id = {ctx.guild.id}")
        if blist:
            for item in blist:
                if 'user' == item['type']:
                    blacklisted = discord.Embed(title="You Are Blacklisted",
                                                description=f"{ctx.author.mention}, you are blacklisted from using this bot. "
                                                            f"Please contact `MS Arranges#3060` if you believe this is a mistake",
                                                color=discord.Color.dark_red())
                    await ctx.channel.send(embed=blacklisted)
                if 'guild' == item['type']:
                    blacklisted = discord.Embed(title="Guild is Blacklisted",
                                                description=f"{ctx.guild.name} is blacklisted from using this bot. "
                                                            f"Please contact `MS Arranges#3060` if you believe this is a mistake",
                                                color=discord.Color.dark_red())
                    await ctx.channel.send(embed=blacklisted)
                    await ctx.guild.leave()
                    return False

        return False if blist else True

    async def disable_dm_exec(self, ctx):
        if not ctx.guild:
            disabled = discord.Embed(title="DM Commands Disabled",
                                     description=f"{ctx.author.mention}, `m?{ctx.invoked_with}` can only be accessed "
                                     f"in a server",
                                     color=discord.Color.dark_red())
            await ctx.channel.send(embed=disabled)
            return False
        else:
            return True

    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            req_arg = discord.Embed(title="Missing Required Argument",
                                    description=f"{ctx.author.mention}, `[{error.param.name}]` is a required argument",
                                    color=discord.Color.dark_red())
            return await ctx.channel.send(embed=req_arg)
        elif isinstance(error, commands.MissingPermissions):
            missing = discord.Embed(title="Insufficient User Permissions",
                                    description=f"{ctx.author.mention}, to execute this command, you need "
                                                f"`{'` `'.join(error.missing_perms).replace('_', ' ').title()}`",
                                    color=discord.Color.dark_red())
            return await ctx.channel.send(embed=missing)
        elif isinstance(error, commands.BotMissingPermissions):
            missing = discord.Embed(title="Insufficient Bot Permissions",
                                    description=f"{ctx.author.mention}, to execute this command, I need "
                                                f"`{'` `'.join(error.missing_perms).replace('_', ' ').title()}`",
                                    color=discord.Color.dark_red())
            return await ctx.channel.send(embed=missing)
        elif isinstance(error, commands.NotOwner):
            not_owner = discord.Embed(title="Insufficient User Permissions",
                                      description=f"{ctx.author.mention}, only the bot owner is authorised to use this "
                                      f"command",
                                      color=discord.Color.dark_red())
            return await ctx.channel.send(embed=not_owner)
        elif isinstance(error, commands.CommandNotFound):
            notFound = discord.Embed(title="Command Not Found",
                                     description=f"{ctx.author.mention}, `{ctx.message.content}` "
                                     f"does not exist\n\nDo `{await gcmds.prefix(ctx)}help` for help",
                                     color=discord.Color.dark_red())
            return await ctx.channel.send(embed=notFound)
        elif isinstance(error, commands.CommandOnCooldown):
            cooldown_time_truncated = gcmds.truncate(error.retry_after, 3)
            if cooldown_time_truncated < 1:
                spell = "milliseconds"
                cooldown_time_truncated *= 1000
            else:
                spell = "seconds"
            cooldown = discord.Embed(title="Command on Cooldown",
                                     description=f"{ctx.author.mention}, this command is still on cooldown for {cooldown_time_truncated} {spell}",
                                     color=discord.Color.dark_red())
            return await ctx.channel.send(embed=cooldown)
        elif hasattr(error, "original"):
            if isinstance(error.original, NodeException):
                embed = discord.Embed(title="Music Error",
                                      description="NodeException: " + str(error.original),
                                      color=discord.Color.dark_red())
                return await ctx.channel.send(embed=embed)
            elif isinstance(error.original, discord.Forbidden):
                forbidden = discord.Embed(title="403 Forbidden",
                                          description=f"{ctx.author.mention}, I cannot execute this command because I lack "
                                          f"the permissions to do so, or my role is lower in the hierarchy.",
                                          color=discord.Color.dark_red())
                return await ctx.channel.send(embed=forbidden)
            else:
                raise error
        else:
            for error_type in ALL_CUSTOMERRORS:
                if isinstance(error, error_type):
                    if hasattr(error, "embed"):
                        return await ctx.channel.send(embed=error.embed)
                    else:
                        pass
                    break
                else:
                    continue
            else:
                if isinstance(error, commands.CheckFailure):
                    pass
                else:
                    raise error

    async def on_guild_join(self, guild):
        async with self.db.acquire() as con:
            # Checks blacklist table
            result = await con.fetch(f"SELECT * FROM blacklist WHERE id = {guild.id} AND type='guild'")
            if result:
                await guild.leave()
            else:
                await con.execute(f"INSERT INTO guild_mb (guild_id, custom_prefix) VALUES ('{guild.id}', 'm?')")

    async def all_loaded(self):
        await self.wait_until_ready()
        globalcommands.start_time = int(datetime.now().timestamp())
        hostname = socket.gethostname()
        ip = socket.gethostbyname(hostname)
        users = len(self.users)
        guilds = len(self.guilds)
        ct = len(self.commands)
        at = await self.get_aliases()
        print(f'Successfully logged in as {self.user}\nIP: {ip}\nHost: {str(hostname)}\nServing '
              f'{users} users across {guilds} servers\nCommands: {ct}\nAliases: {at}\n{version}')
        self.status.start()

    async def get_aliases(self):
        at = 0
        for command in self.commands:
            if command.aliases:
                for alias in command.aliases:
                    at += 1
        return at


uptime = int(datetime.now().timestamp())
loop = asyncio.get_event_loop()
loop.run_until_complete(run(uptime))
