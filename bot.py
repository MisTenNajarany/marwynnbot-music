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
import globalcommands
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


async def check_marwynnbot():
    mb_id = gcmds.env_check("MARWYNNBOT_ID")
    mb = client.get_user(int(mb_id))
    member_id_list = [(guild, [member.id for member in guild.members]) for guild in client.guilds]
    for guild, id_list in member_id_list:
        if not int(mb_id) in id_list:
            embed = discord.Embed(title="Invite MarwynnBot!",
                                  description=f"Thank you for using {client.user.mention}! I'd like to invite you to "
                                  f"use {mb.mention} as well. MarwynnBot is the main bot which this bot is ported from. "
                                  "MarwynnBot has a ton of features that aren't included in MarwynnBot Music, so please"
                                  " consider checking it out!\n\n**Invite:** https://discord.com/oauth2/authorize?"
                                  "client_id=623317451811061763&scope=bot&permissions=8",
                                  color=discord.Color.blue(),
                                  url="https://discord.com/oauth2/authorize?client_id=623317451811061763&"
                                  "scope=bot&permissions=8")
            for channel in guild.channels:
                try:
                    await channel.send(embed=embed)
                    break
                except Exception:
                    continue


async def client_ready():
    await client.wait_until_ready()
    print("Running", version)
    hostname = socket.gethostname()
    ip = socket.gethostbyname(hostname)
    print(f'Successfully logged in as {client.user}\nIP: {ip}\nHost: {str(hostname)}\nServing '
          f'{len(client.users)} users across {len(client.guilds)} servers')
    await status()
    await check_marwynnbot()


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
    elif isinstance(error, globalcommands.MBConnectedError):
            embed = discord.Embed(title="MarwynnBot is Already Connected",
                                  description=f"{ctx.author.mention}, MarwynnBot is already connected to this voice "
                                  "channel. Please disconnect MarwynnBot or have me join a different voice channel",
                                  color=discord.Color.dark_red())
            return await ctx.channel.send(embed=embed, delete_after=15)
    elif isinstance(error, commands.CheckFailure):
        pass
    else:
        raise error


@client.event
async def on_guild_join(guild):
    gcmds.json_load('db/prefixes.json', {})
    with open('db/prefixes.json', 'r') as f:
        prefixes = json.load(f)
    prefixes[str(guild.id)] = 'm?'

    with open('db/prefixes.json', 'w') as f:
        json.dump(prefixes, f, indent=4)
    
    mb_id = gcmds.env_check('MARWYNNBOT_ID')
    mb = client.get_user(int(mb_id))
    member_id_list = [member.id for member in guild.members]
    if not int(mb_id) in member_id_list:
        embed = discord.Embed(title="Invite MarwynnBot!",
                                  description=f"Thank you for using {client.user.mention}! I'd like to invite you to "
                                  f"use {mb.mention} as well. MarwynnBot is the main bot which this bot is ported from. "
                                  "MarwynnBot has a ton of features that aren't included in MarwynnBot Music, so please"
                                  " consider checking it out!\n\n**Invite:** https://discord.com/oauth2/authorize?"
                                  "client_id=623317451811061763&scope=bot&permissions=8",
                                  color=discord.Color.blue(),
                                  url="https://discord.com/oauth2/authorize?client_id=623317451811061763&"
                                  "scope=bot&permissions=8")
        for channel in guild.channels:
            try:
                await channel.send(embed=embed)
                break
            except Exception:
                continue


@client.event
async def on_guild_remove(guild):
    with open('db/prefixes.json', 'r') as f:
        prefixes = json.load(f)

    prefixes.pop(str(guild.id))

    with open('db/prefixes.json', 'w') as f:
        json.dump(prefixes, f, indent=4)


cogs = [filename[:-3] for filename in os.listdir('./cogs') if filename.endswith(".py")]
for cog in sorted(cogs):
    client.load_extension(f'cogs.{cog}')
    print(f"Cog \"{cog}\" has been loaded")


if not gcmds.init_env():
    sys.exit("Please put your bot's token inside the created .env file")
load_dotenv()
client.loop.create_task(client_ready())
token = os.getenv('TOKEN')
client.run(token)
