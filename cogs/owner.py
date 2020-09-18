import json
import os
import discord
from discord.ext import commands
from discord.ext.commands.errors import CommandInvokeError
from utils import globalcommands

gcmds = globalcommands.GlobalCMDS()


class Owner(commands.Cog):

    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot

    @commands.command(aliases=['l', 'ld'])
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

    @commands.command(aliases=['ul', 'uld'])
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

    @commands.command(aliases=['r', 'rl'])
    @commands.is_owner()
    async def reload(self, ctx, *, extension=None):
        if extension is None:
            print("==========================")
            for filenameReload in os.listdir('./cogs'):
                if filenameReload.endswith('.py'):
                    self.bot.reload_extension(f'cogs.{filenameReload[:-3]}')
                    print(f'Cog "{filenameReload[:-3].capitalize()}" has been reloaded')
            reloadEmbed = discord.Embed(title="Reload Success",
                                        description="Successfully reloaded all cogs",
                                        color=discord.Color.blue())
            await ctx.channel.send(embed=reloadEmbed)
            print("==========================")
        else:
            print("==========================")
            self.bot.reload_extension(f'cogs.{extension}')
            print(f'Cog "{extension}" has been reloaded')
            reloadEmbed = discord.Embed(title="Reload Success",
                                        description=f"Successfully reloaded cog `{extension}`",
                                        color=discord.Color.blue())
            await ctx.channel.send(embed=reloadEmbed)
            print("==========================")

    @commands.command(aliases=['taskkill'])
    @commands.is_owner()
    async def shutdown(self, ctx):
        shutdownEmbed = discord.Embed(title="Bot Shutdown Successful",
                                      description="Bot is logging out",
                                      color=discord.Color.blue())
        await ctx.channel.send(embed=shutdownEmbed)
        await self.bot.logout()


def setup(client):
    client.add_cog(Owner(client))
