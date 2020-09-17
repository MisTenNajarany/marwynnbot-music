import json
import discord
from discord.ext import commands
from utils import globalcommands


gcmds = globalcommands.GlobalCMDS()


class Utility(commands.Cog):

    def __init__(self, bot: commands.AutoShardedBot):
        global gcmds
        self.bot = bot
        gcmds = globalcommands.GlobalCMDS(self.bot)

    @commands.command()
    async def invite(self, ctx):
        embed = discord.Embed(title="MarwynnBot Music's Invite Link",
                              description=f"{ctx.author.mention}, thank you for using MarwynnBot Music! Here is my"
                              " invite link that you can share:\n\n https://discord.com/oauth2/authorize?client_id=7519"
                              "66223813705809&scope=bot&permissions=66334016",
                              color=discord.Color.blue(),
                              url="https://discord.com/oauth2/authorize?client_id=751966223813705809&"
                              "scope=bot&permissions=66334016")
        await ctx.channel.send(embed=embed)

    @commands.command(aliases=['p', 'checkprefix', 'prefixes'])
    async def prefix(self, ctx):
        prefixEmbed = discord.Embed(title='Prefixes',
                                    color=discord.Color.blue())
        prefixEmbed.add_field(name="Current Server Prefix",
                              value=f"The current server prefix is: `{gcmds.prefix(ctx)}`",
                              inline=False)
        prefixEmbed.add_field(name="Global Prefixes",
                              value=f"{self.bot.user.mention} or `mbm ` - *ignorecase*",
                              inline=False)
        await ctx.channel.send(embed=prefixEmbed)

    @commands.command(aliases=['sp', 'setprefix'])
    @commands.has_permissions(manage_guild=True)
    async def setPrefix(self, ctx, prefix):
        async with self.db.acquire() as con:
            if prefix != 'reset':
                await con.execute(f"UPDATE guild_mb SET custom_prefix = {prefix} WHERE guild_id = {ctx.guild.id}")
                prefixEmbed = discord.Embed(title='Server Prefix Set',
                                            description=f"Server prefix is now set to `{prefix}` \n\n"
                                                        f"You will still be able to use {self.bot.user.mention} "
                                                        f"and `mbm ` as prefixes",
                                            color=discord.Color.blue())
            else:
                await con.execute(f"UPDATE guild_mb SET custom_prefix = 'm?' WHERE guild_id = {ctx.guild.id}")
                prefixEmbed = discord.Embed(title='Server Prefix Set',
                                            description=f"Server prefix has been reset to `m?`",
                                            color=discord.Color.blue())
            await ctx.channel.send(embed=prefixEmbed)


def setup(client):
    client.add_cog(Utility(client))
