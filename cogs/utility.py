import os
import json
from datetime import datetime, timedelta
from io import BytesIO

import discord
from discord.ext import commands, tasks
from utils import globalcommands, paginator

gcmds = globalcommands.GlobalCMDS()
invite_url = "https://discord.com/oauth2/authorize?client_id=763094082046132276&scope=bot&permissions=66061568"


class Utility(commands.Cog):

    def __init__(self, bot: commands.AutoShardedBot):
        global gcmds
        self.bot = bot
        gcmds = globalcommands.GlobalCMDS(bot=self.bot)

    @commands.command(desc="Displays MarwynnBot Music's invite link",
                      usage="invite")
    async def invite(self, ctx):
        embed = discord.Embed(title="MarwynnBot Music's Invite Link",
                              description=f"{ctx.author.mention}, thank you for using MarwynnBot Music! "
                              f"Here is MarwynnBot Music's invite link that you can share:\n\n {invite_url}",
                              color=discord.Color.blue(),
                              url=invite_url)
        await ctx.channel.send(embed=embed)

    @commands.command(aliases=['p', 'checkprefix', 'prefixes'],
                      desc="Displays the server's custom prefix",
                      usage="prefix")
    async def prefix(self, ctx):
        serverPrefix = await gcmds.prefix(ctx)
        prefixEmbed = discord.Embed(title='Prefixes',
                                    color=discord.Color.blue())
        prefixEmbed.add_field(name="Current Server Prefix",
                              value=f"The current server prefix is: `{serverPrefix}`",
                              inline=False)
        prefixEmbed.add_field(name="Global Prefixes",
                              value=f"{self.bot.user.mention} or `mbm ` - *ignorecase*",
                              inline=False)
        await ctx.channel.send(embed=prefixEmbed)

    @commands.command(aliases=['sp', 'setprefix'],
                      desc="Sets the server's custom prefix",
                      usage="setprefix [prefix]",
                      uperms=["Manage Server"],
                      note="If `[prefix]` is \"reset\", then the custom prefix will be set to \"m!\"")
    @commands.has_permissions(manage_guild=True)
    async def setPrefix(self, ctx, prefix):
        async with self.db.acquire() as con:
            if prefix != 'reset':
                await con.execute(f"UPDATE guild_mb SET custom_prefix=$tag${prefix}$tag$ WHERE guild_id={ctx.guild.id}")
                prefixEmbed = discord.Embed(title='Server Prefix Set',
                                            description=f"Server prefix is now set to `{prefix}` \n\n"
                                                        f"You will still be able to use {self.bot.user.mention} "
                                                        f"and `mbm ` as prefixes",
                                            color=discord.Color.blue())
            else:
                await con.execute(f"UPDATE guild_mb SET custom_prefix='m!' WHERE guild_id={ctx.guild.id}")
                prefixEmbed = discord.Embed(title='Server Prefix Set',
                                            description=f"Server prefix has been reset to `m!`",
                                            color=discord.Color.blue())
            await ctx.channel.send(embed=prefixEmbed)

    @commands.command(desc="Displays MarwynnBot Music's uptime since the last restart",
                      usage="uptime")
    async def uptime(self, ctx):
        time_now = int(datetime.now().timestamp())
        td = timedelta(seconds=time_now - self.bot.uptime)
        embed = discord.Embed(title="Uptime",
                              description=f"MarwynnBot Music has been up and running for\n```\n{str(td)}\n```",
                              color=discord.Color.blue())
        return await ctx.channel.send(embed=embed)


def setup(bot):
    bot.add_cog(Utility(bot))
