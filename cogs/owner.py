import os
import subprocess
import sys
from datetime import datetime
from io import BytesIO, StringIO

import discord
from asyncpg.exceptions import UniqueViolationError
from discord.ext import commands
from discord.ext.commands.errors import CommandInvokeError
from utils import customerrors, globalcommands, paginator

gcmds = GlobalCMDS()
OWNER_PERM = ["Bot Owner Only"]


class Owner(commands.Cog):

    def __init__(self, bot):
        global gcmds
        self.bot = bot
        gcmds = GlobalCMDS(self.bot)

    @commands.group(invoke_without_command=True,
                    aliases=['g'],
                    desc="Git operations",
                    usage="git [command]",
                    uperms=OWNER_PERM)
    @commands.is_owner()
    async def git(self, ctx, *, args: str):
        embed = discord.Embed(title="Git Output")
        try:
            output = subprocess.check_output(f"git {args}", stderr=subprocess.STDOUT, shell=True)
        except subprocess.CalledProcessError as e:
            output = e.output
            embed.color = discord.Color.dark_red()
        else:
            embed.color = discord.Color.blue()

        if len(output) <= 2048:
            embed.description = f"```{output.decode('utf-8') if output else f'{args} executed successfully'}```"
            return await ctx.channel.send(embed=embed)
        else:
            embed.description = "```\nSTDOUT longer than 2048 characters. See the file below:\n```"
            stdout_file = discord.File(
                BytesIO(output), filename=f"{ctx.author.display_name.upper()}{datetime.now()}.txt")
            await ctx.channel.send(embed=embed)
            return await ctx.channel.send(file=stdout_file)

    @git.command(aliases=['gpod'])
    @commands.is_owner()
    async def git_gpod(self, ctx):
        return await self.git(ctx, args="pull origin development")

    @git.command(aliases=['gpom'])
    @commands.is_owner()
    async def git_gpom(self, ctx):
        return await self.git(ctx, args="pull origin master")

    @commands.command(aliases=['l', 'ld'],
                      desc="Loads cogs",
                      usage="load [extension]",
                      uperms=OWNER_PERM)
    @commands.is_owner()
    async def load(self, ctx, extension):
        try:
            self.bot.load_extension(f'cogs.{extension}')
        except CommandInvokeError:
            title = "Cog Load Fail"
            description = f"Failed to load cog {extension}, it is already loaded"
            color = discord.Color.blue()
        else:
            print(f'Cog "{extension}" has been loaded')
            title = "Cog Load Success"
            description = f"Successfully loaded cog {extension}"
            color = discord.Color.blue()
        loadEmbed = discord.Embed(title=title,
                                  description=description,
                                  color=color)
        await ctx.channel.send(embed=loadEmbed)

    @commands.command(aliases=['ul', 'uld'],
                      desc="Unloads cogs",
                      usage="unload [extension]",
                      uperms=OWNER_PERM)
    @commands.is_owner()
    async def unload(self, ctx, extension):
        try:
            self.bot.unload_extension(f'cogs.{extension}')
        except CommandInvokeError:
            title = "Cog Unoad Fail"
            description = f"Failed to unload cog {extension}, it is already unloaded"
            color = discord.Color.blue()
        else:
            print(f'Cog "{extension}" has been unloaded')
            title = "Cog Unload Success"
            description = f"Successfully unloaded cog {extension}"
            color = discord.Color.blue()
        unloadEmbed = discord.Embed(title=title,
                                    description=description,
                                    color=color)
        await ctx.channel.send(embed=unloadEmbed)

    @commands.command(aliases=['r', 'rl'],
                      desc="Reloads cogs",
                      usage="reload (extension)",
                      uperms=OWNER_PERM)
    @commands.is_owner()
    async def reload(self, ctx, *, extension=None):
        if extension is None:
            print("==========================")
            for filenameReload in os.listdir('./cogs'):
                if filenameReload.endswith('.py'):
                    try:
                        self.bot.reload_extension(f'cogs.{filenameReload[:-3]}')
                        print(f'Cog "{filenameReload[:-3]}" has been reloaded')
                    except commands.ExtensionError:
                        self.bot.load_extension(f'cogs.{filenameReload[:-3]}')
                        print(f'Cog "{filenameReload[:-3]}" has been loaded')
            reloadEmbed = discord.Embed(title="Reload Success",
                                        description="Successfully reloaded all cogs",
                                        color=discord.Color.blue())
            await ctx.channel.send(embed=reloadEmbed)
            print("==========================")
        else:
            print("==========================")
            try:
                self.bot.reload_extension(f'cogs.{extension}')
                print(f'Cog "{extension}" has been reloaded')
            except commands.ExtensionError:
                self.bot.load_extension(f'cogs.{extension}')
                print(f'Cog "{extension}" has been loaded')
            reloadEmbed = discord.Embed(title="Reload Success",
                                        description=f"Successfully reloaded cog `{extension}`",
                                        color=discord.Color.blue())
            await ctx.channel.send(embed=reloadEmbed)
            print("==========================")

    @commands.command(aliases=['taskkill', 'sd'],
                      desc="Shuts the bot down",
                      usage="shutdown",
                      uperms=OWNER_PERM)
    @commands.is_owner()
    async def shutdown(self, ctx):
        shutdownEmbed = discord.Embed(title="Bot Shutdown Successful",
                                      description="Bot is logging out",
                                      color=discord.Color.blue())
        await ctx.channel.send(embed=shutdownEmbed)
        await self.bot.close()

    @commands.command(aliases=['fleave'],
                      desc="Forces the bot to leave a server",
                      usage="forceleave (server_id)",
                      uperms=OWNER_PERM,
                      note="If `(server_id)` is unspecified, the bot will leave the current "
                      "server the invocation context is in")
    @commands.is_owner()
    async def forceleave(self, ctx, guild_id=None):
        if guild_id is None:
            guild_id = ctx.guild.id
        await self.bot.get_guild(guild_id).leave()
        leaveEmbed = discord.Embed(title="Successfully Left Server",
                                   description=f"Left guild id: {id}",
                                   color=discord.Color.blue())
        await ctx.author.send(embed=leaveEmbed)

    @commands.group(invoke_without_command=True,
                    desc="Displays the premium message",
                    usage="premium")
    async def premium(self, ctx):
        description = ("MarwynnBot Premium is an optional, subscription based plan that will grant the subscriber complete, unrestricted "
                       "access to all of MarwynnBot's \"premium locked\" features, such as creating and saving playlists, receiving special monthly"
                       "balance crates, public tags, unlimited number of tags, a special role in the MarwynnBot Support Server, and more!\n\n"
                       "**MarwynnBot Premium is currently unavailable. This message will update when it becomes available, most likely after MarwynnBot's"
                       "v1.0.0-rc.1 release**")
        embed = discord.Embed(title="MarwynnBot Premium",
                              description=description,
                              color=discord.Color.blue())
        return await ctx.channel.send(embed=embed)


def setup(bot):
    bot.add_cog(Owner(bot))
