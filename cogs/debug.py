import os
from datetime import datetime, timedelta

import discord
import psutil
from discord.ext import commands
from utils import GlobalCMDS

gcmds = GlobalCMDS()
updates_reaction = ['✅', '📝', '🛑']


class Debug(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    async def timeout(self, ctx, message: discord.Message) -> discord.Message:
        embed = discord.Embed(title="Report Update Cancelled",
                              description=f"{ctx.author.mention}, your report update request timed out",
                              color=discord.Color.dark_red())
        try:
            return await message.edit(embed=embed)
        except (discord.NotFound, discord.HTTPError, discord.Forbidden):
            return await ctx.author.send(embed=embed)

    async def cancel(self, ctx, message: discord.Message) -> discord.Message:
        embed = discord.Embed(title="Report Update Cancelled",
                              description=f"{ctx.author.mention}, your report update request was cancelled",
                              color=discord.Color.dark_red())
        try:
            return await message.edit(embed=embed)
        except (discord.NotFound, discord.HTTPError, discord.Forbidden):
            return await ctx.author.send(embed=embed)

    @commands.command(desc="Displays MarwynnBot Music's ping in milliseconds (ms)",
                      usage="ping")
    async def ping(self, ctx):
        ping = discord.Embed(title='Ping', color=discord.Color.blue())
        ping.set_thumbnail(url='https://cdn1.iconfinder.com/data/icons/travel-and-leisure-vol-1/512/16-512.png')
        ping.add_field(name="MarwynnBot Music", value=f'{round(self.bot.latency * 1000)}ms')
        await ctx.send(embed=ping)

    @commands.command(aliases=['mb', 'selfinfo', 'about', 'me'],
                      desc="Get info about me! Mostly for debug purposes though",
                      usage="marwynnbot")
    async def marwynnbot(self, ctx):
        async with self.bot.db.acquire() as con:
            command_amount = await con.fetchval("SELECT SUM (amount) FROM global_counters")
        current_process = psutil.Process(os.getpid())
        mem = psutil.virtual_memory()
        mem_used = current_process.memory_full_info().uss
        swap = psutil.swap_memory()
        swap_used = getattr(current_process.memory_full_info(), "swap", swap.used)
        disk = psutil.disk_usage("/")
        time_now = int(datetime.now().timestamp())
        complete_command_list = [command for cog in self.bot.cogs
                                 for command in self.bot.get_cog(cog).walk_commands()]
        td = timedelta(seconds=time_now - self.bot.uptime)
        description = (f"Hi there! I am a Discord Music Bot made by <@{self.bot.owner_id}> "
                       "written in Python using the `discord.py` API wrapper. Here are some of my stats:")
        stats = (f"Servers Joined: {len(self.bot.guilds)}",
                 f"Users Served: {len(self.bot.users)}",
                 f"Commands: {len(self.bot.commands)}",
                 f"Commands Including Subcommands: {len(complete_command_list)}",
                 f"Aliases: {len([alias for command in self.bot.commands for alias in command.aliases if command.aliases])}",
                 f"Commands Processed: {command_amount}",
                 f"Uptime: {str(td)}")
        cpu_stats = "```{}```".format(
            "\n".join(
                    [f"Core {counter}: {round(freq, 2)}%"
                     for counter, freq in enumerate(psutil.cpu_percent(percpu=True))]
            )
        )
        memory_stats = "```{}```".format(
            "\n".join(
                [f"Total: {round((mem.total / 1000000), 2)} MB",
                 f"Available: {round((mem.available / 1000000), 2)} MB",
                 f"Used: {round((mem_used / 1000000), 2)} MB",
                 f"Percent: {round(100 * (mem_used / mem.total), 2)}%"]
            )
        )
        swap_stats = "```{}```".format(
            "\n".join(
                [f"Total: {round((swap.total / 1000000))} MB",
                 f"Free: {round((swap.free / 1000000), 2)} MB",
                 f"Used: {round((swap_used / 1000000), 2)} MB",
                 f"Percentage: {round(100 * (swap_used / swap.total), 2)}%"]
            )
        )
        disk_stats = "```{}```".format(
            "\n".join(
                [f"Total: {round((disk.total / 1000000000), 2)} GB",
                 f"Used: {round((disk.used / 1000000000), 2)} GB",
                 f"Free: {round((disk.free / 1000000000), 2)} GB",
                 f"Percentage: {round((100 * disk.used / disk.total), 2)}%"]
            )
        )
        nv = [
            ("Stats", "```{}```".format("\n".join(stats))),
            ("CPU Info", cpu_stats),
            ("Memory Info", memory_stats),
            ("Swap Info", swap_stats),
            ("Disk Info", disk_stats)
        ]
        embed = discord.Embed(title="Info About Me!", description=description, color=discord.Color.blue())
        for name, value in nv:
            embed.add_field(name=name, value=value, inline=False)
        return await ctx.channel.send(embed=embed)

    @commands.command(desc="Displays what MarwynnBot Music shard is connected to your server",
                      usage="shard (flag)",
                      note="If `(flag)` is \"count\", it will display the total number of shards")
    async def shard(self, ctx, option=None):
        if option != 'count':
            shardDesc = f"This server is running on shard: {ctx.guild.shard_id}"
        else:
            shardDesc = f"**Shards:** {self.bot.shard_count}"
        shardEmbed = discord.Embed(title="Shard Info",
                                   description=shardDesc,
                                   color=discord.Color.blue())
        await ctx.channel.send(embed=shardEmbed)


def setup(bot):
    bot.add_cog(Debug(bot))
