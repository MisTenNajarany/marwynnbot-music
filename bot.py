import json
import logging
import math
import os
import random
import socket
import sys
import re
import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv
from globalcommands import GlobalCMDS


gcmds = GlobalCMDS()
token_rx = re.compile(r'[MN]\w{23}.[\w-]{6}.[\w-]{27}')
version = f"MarwynnBot Music {gcmds.version}"

if os.path.exists('discord.log'):
    os.remove('discord.log')


async def get_prefix(client, message):
    if isinstance(message.channel, discord.DMChannel) or isinstance(message.channel, discord.GroupChannel):
        extras = ('mm ', 'mM ', 'Mm ', 'MM ', 'm?', 'M? ')
        return commands.when_mentioned_or(*extras)(client, message)
    else:
        with open('db/prefixes.json', 'r') as f:
            prefixes = json.load(f)
            extras = (
                f'{prefixes[str(message.guild.id)]}', f'{prefixes[str(message.guild.id)]} ', 'mm ', 'mM ', 'Mm ', 'MM ',
                'm?', 'M?')
            return commands.when_mentioned_or(*extras)(client, message)


client = commands.AutoShardedBot(command_prefix=get_prefix, help_command=None, shard_count=1)

logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)



async def status():
    activity = discord.Activity(name="Invite MarwynnBot!", type=discord.ActivityType.playing)
    await client.change_presence(status=discord.Status.online, activity=activity)


@client.event
async def on_ready():
    cogs = [filename[:-3] for filename in os.listdir('./cogs') if filename.endswith(".py")]
    for cog in sorted(cogs):
        client.load_extension(f'cogs.{cog}')
        print(f"Cog \"{cog}\" has been loaded")
    print("Running", version)
    hostname = socket.gethostname()
    ip = socket.gethostbyname(hostname)
    print(f'Successfully logged in as {client.user}\nIP: {ip}\nHost: {str(hostname)}\nServing '
          f'{len(client.users)} users across {len(client.guilds)} servers')
    await status()


@client.check
async def disable_dm_exec(ctx):
    if not ctx.guild:
        disabled = discord.Embed(title="Command Disabled in Non Server Channels",
                                 description=f"{ctx.author.mention}, `m!{ctx.invoked_with}` can only be accessed "
                                             f"in a server",
                                 color=discord.Color.dark_red())
        await ctx.channel.send(embed=disabled)
        return False
    else:
        return True


@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        req_arg = discord.Embed(title="Missing Required Argument",
                                description=f"{ctx.author.mention}, `[{error.param.name}]` is a required argument",
                                color=discord.Color.dark_red())
        await ctx.channel.send(embed=req_arg, delete_after=10)
    elif isinstance(error, discord.ext.commands.MissingPermissions):
        missing = discord.Embed(title="Insufficient User Permissions",
                                description=f"{ctx.author.mention}, to execute this command, you need "
                                            f"`{'` `'.join(error.missing_perms).replace('_', ' ').title()}`",
                                color=discord.Color.dark_red())
        await ctx.channel.send(embed=missing, delete_after=10)
    elif isinstance(error, discord.ext.commands.BotMissingPermissions):
        missing = discord.Embed(title="Insufficient Bot Permissions",
                                description=f"{ctx.author.mention}, to execute this command, I need "
                                            f"`{'` `'.join(error.missing_perms).replace('_', ' ').title()}`",
                                color=discord.Color.dark_red())
        await ctx.channel.send(embed=missing, delete_after=10)
    elif isinstance(error, commands.NotOwner):
        not_owner = discord.Embed(title="Insufficient User Permissions",
                                  description=f"{ctx.author.mention}, only the bot owner is authorised to use this "
                                              f"command",
                                  color=discord.Color.dark_red())
        await ctx.channel.send(embed=not_owner, delete_after=10)
    elif isinstance(error, commands.CommandNotFound):
        await gcmds.invkDelete(ctx)
        notFound = discord.Embed(title="Command Not Found",
                                 description=f"{ctx.author.mention}, `{ctx.message.content}` "
                                             f"does not exist\n\nDo `{gcmds.prefix(ctx)}help` for help",
                                 color=discord.Color.dark_red())
        await ctx.channel.send(embed=notFound, delete_after=10)
    elif isinstance(error, commands.CommandOnCooldown):
        cooldown_time_truncated = truncate(error.retry_after, 3)
        if cooldown_time_truncated < 1:
            spell = "milliseconds"
            cooldown_time_truncated *= 1000
        else:
            spell = "seconds"
        cooldown = discord.Embed(title="Command on Cooldown",
                                 description=f"{ctx.author.mention}, this command is still on cooldown for {cooldown_time_truncated} {spell}",
                                 color=discord.Color.dark_red())
        await ctx.channel.send(embed=cooldown, delete_after=math.ceil(error.retry_after))
    elif isinstance(error, commands.CheckFailure):
        pass
    else:
        raise error


def truncate(number: float, decimal_places: int):
    stepper = 10.0 ** decimal_places
    return math.trunc(stepper * number) / stepper


@client.event
async def on_guild_join(guild):
    if not os.path.exists('db/prefixes.json'):
        gcmds.json_load('db/prefixes.json', {})
    with open('db/prefixes.json', 'r') as f:
        prefixes = json.load(f)
    prefixes[str(guild.id)] = 'm!'

    with open('db/prefixes.json', 'w') as f:
        json.dump(prefixes, f, indent=4)


@client.event
async def on_guild_remove(guild):
    with open('db/prefixes.json', 'r') as f:
        prefixes = json.load(f)

    prefixes.pop(str(guild.id))

    with open('db/prefixes.json', 'w') as f:
        json.dump(prefixes, f, indent=4)


if not gcmds.init_env():
    sys.exit("Please put your bot's token inside the created .env file")
load_dotenv()
token = os.getenv('TOKEN')
client.run(token)
