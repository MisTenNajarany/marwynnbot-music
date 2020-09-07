import json
import os
import discord
from discord.ext import commands
from discord.ext.commands.errors import CommandInvokeError
from globalcommands import GlobalCMDS

gcmds = GlobalCMDS()


class Owner(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.command(aliases=['l', 'ld'])
    @commands.is_owner()
    async def load(self, ctx, extension):
        await gcmds.invkDelete(ctx)
        try:
            self.client.load_extension(f'cogs.{extension}')
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
        await ctx.channel.send(embed=loadEmbed, delete_after=5)

    @commands.command(aliases=['ul', 'uld'])
    @commands.is_owner()
    async def unload(self, ctx, extension):
        await gcmds.invkDelete(ctx)
        try:
            self.client.unload_extension(f'cogs.{extension}')
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
        await ctx.channel.send(embed=unloadEmbed, delete_after=5)

    @commands.command(aliases=['r', 'rl'])
    @commands.is_owner()
    async def reload(self, ctx, *, extension=None):
        await gcmds.invkDelete(ctx)
        if extension is None:
            print("==========================")
            for filenameReload in os.listdir('./cogs'):
                if filenameReload.endswith('.py'):
                    self.client.reload_extension(f'cogs.{filenameReload[:-3]}')
                    print(f'Cog "{filenameReload[:-3].capitalize()}" has been reloaded')
            reloadEmbed = discord.Embed(title="Reload Success",
                                        description="Successfully reloaded all cogs",
                                        color=discord.Color.blue())
            await ctx.channel.send(embed=reloadEmbed, delete_after=5)
            print("==========================")
        else:
            print("==========================")
            self.client.reload_extension(f'cogs.{extension}')
            print(f'Cog "{extension}" has been reloaded')
            reloadEmbed = discord.Embed(title="Reload Success",
                                        description=f"Successfully reloaded cog `{extension}`",
                                        color=discord.Color.blue())
            await ctx.channel.send(embed=reloadEmbed, delete_after=5)
            print("==========================")

    @commands.command(aliases=['taskkill'])
    @commands.is_owner()
    async def shutdown(self, ctx):
        await gcmds.invkDelete(ctx)
        shutdownEmbed = discord.Embed(title="Bot Shutdown Successful",
                                      description="Bot is logging out",
                                      color=discord.Color.blue())
        await ctx.channel.send(embed=shutdownEmbed)
        await self.client.logout()


def setup(client):
    client.add_cog(Owner(client))
