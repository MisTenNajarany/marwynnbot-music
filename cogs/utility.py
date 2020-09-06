import json
import discord
from discord.ext import commands
from globalcommands import GlobalCMDS


gcmds = GlobalCMDS()


class Utility(commands.Cog):

    def __init__(self, client):
        self.client = client
        self.messages = {}
        self.update_server_stats.start()

    def cog_unload(self):
        self.update_server_stats.cancel()

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'Cog "{self.qualified_name}" has been loaded')

    @commands.command()
    async def invite(self, ctx):
        await gcmds.invkDelete(ctx)
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
        await gcmds.invkDelete(ctx)
        with open('db/prefixes.json', 'r') as f:
            prefixes = json.load(f)

        serverPrefix = prefixes[str(ctx.guild.id)]
        prefixEmbed = discord.Embed(title='Prefixes',
                                    color=discord.Color.blue())
        prefixEmbed.add_field(name="Current Server Prefix",
                              value=f"The current server prefix is: `{serverPrefix}`",
                              inline=False)
        prefixEmbed.add_field(name="Global Prefixes",
                              value=f"{self.client.user.mention} or `mb ` - *ignorecase*",
                              inline=False)
        await ctx.channel.send(embed=prefixEmbed)
        gcmds.incrCounter(ctx, 'prefix')

    @commands.command(aliases=['sp', 'setprefix'])
    @commands.has_permissions(manage_guild=True)
    async def setPrefix(self, ctx, prefix):
        await gcmds.invkDelete(ctx)
        with open('db/prefixes.json', 'r') as f:
            prefixes = json.load(f)
            if prefix != 'reset':
                prefixes[str(ctx.guild.id)] = prefix
            else:
                prefixes[str(ctx.guild.id)] = 'm!'
        with open('db/prefixes.json', 'w') as f:
            json.dump(prefixes, f, indent=4)
        if prefix != 'reset':
            prefixEmbed = discord.Embed(title='Server Prefix Set',
                                        description=f"Server prefix is now set to `{prefix}` \n\n"
                                                    f"You will still be able to use {self.client.user.mention} "
                                                    f"and `mb ` as prefixes",
                                        color=discord.Color.blue())
        else:
            prefixEmbed = discord.Embed(title='Server Prefix Set',
                                        description=f"Server prefix has been reset to `m!`",
                                        color=discord.Color.blue())
        await ctx.channel.send(embed=prefixEmbed)
        gcmds.incrCounter(ctx, 'setPrefix')


def setup(client):
    client.add_cog(Utility(client))
