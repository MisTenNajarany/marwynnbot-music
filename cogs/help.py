import random
from datetime import datetime
import discord
from discord.ext import commands
from utils import globalcommands

gcmds = globalcommands.GlobalCMDS()


class Help(commands.Cog):

    def __init__(self, bot: commands.AutoShardedBot):
        global gcmds
        self.bot = bot
        gcmds = globalcommands.GlobalCMDS(self.bot)

    async def syntaxEmbed(self, ctx, commandName, syntaxMessage, exampleUsage=None, exampleOutput=None,
                          userPerms=None, botPerms=None, specialCases=None, thumbnailURL="https://www.jing.fm/clipimg"
                                                                                         "/full/71-716621_transparent"
                                                                                         "-clip-art-open-book-frame"
                                                                                         "-line-art.png",
                          delete_after=None):
        embed = discord.Embed(title=f"{commandName} Help",
                              color=discord.Color.blue())
        embed.add_field(name="Command Syntax",
                        value=f'{syntaxMessage}')
        if exampleUsage:
            embed.add_field(name="Example Usage",
                            value=exampleUsage,
                            inline=False)
        if exampleOutput:
            embed.add_field(name="Output",
                            value=exampleOutput,
                            inline=False)
        cmdName = self.bot.get_command(ctx.command.name)
        aliases = cmdName.aliases
        if aliases:
            embed.add_field(name="Aliases",
                            value=f"`{'` `'.join(aliases)}`",
                            inline=False)
        if userPerms:
            embed.add_field(name="User Permissions Required",
                            value=userPerms,
                            inline=False)
        if botPerms:
            embed.add_field(name="Bot Permissions Required",
                            value=botPerms,
                            inline=False)
        if specialCases:
            embed.add_field(name="Special Cases",
                            value=specialCases,
                            inline=False)
        if thumbnailURL:
            embed.set_thumbnail(url=thumbnailURL)

        timestamp = f"Executed by {ctx.author.display_name} " + "at: {:%m/%d/%Y %H:%M:%S}".format(datetime.now())
        embed.set_footer(text=timestamp,
                         icon_url=ctx.author.avatar_url)

        await ctx.channel.send(embed=embed, delete_after=delete_after)

    @commands.group(invoke_without_command=True, aliases=['h'])
    async def help(self, ctx):
        timestamp = f"Executed by {ctx.author.display_name} " + "at: {:%m/%d/%Y %H:%M:%S}".format(datetime.now())
        helpEmbed = discord.Embed(title="MarwynnBot Music Help Menu",
                                    color=discord.Color.blue(),
                                    url="https://discord.gg/fYBTdUp",
                                    description="These are all the commands I currently support! Type"
                                                f"\n```{gcmds.prefix(ctx)}help [command]```\n to get help on "
                                                f"that specific command")
        helpEmbed.set_thumbnail(
            url="https://www.jing.fm/clipimg/full/71-716621_transparent-clip-art-open-book-frame-line-art.png")
        helpEmbed.set_author(name="MarwynnBot Music",
                                icon_url=ctx.me.avatar_url)
        helpEmbed.set_footer(text=timestamp,
                                icon_url=ctx.author.avatar_url)

        cogNames = [i for i in self.bot.cogs]
        cogs = [self.bot.get_cog(j) for j in cogNames]
        strings = {}
        for name in cogNames:
            cog_commands = self.bot.get_cog(name).get_commands()
            strings.update({name.lower(): [command.name.lower() for command in cog_commands]})

        helpCmds = f"`{'` `'.join(strings['help'])}`"
        musicCmds = f"`{'` `'.join(strings['music'])}`"
        ownerCmds = f"`{'` `'.join(strings['owner'])}`"
        utilityCmds = f"`{'` `'.join(strings['utility'])}`"

        helpEmbed.add_field(name="Help",
                            value=helpCmds,
                            inline=False)
        helpEmbed.add_field(name="Music",
                            value=musicCmds,
                            inline=False)
        helpEmbed.add_field(name="Utility",
                            value=utilityCmds,
                            inline=False)
        helpEmbed.add_field(name="Owner Only",
                            value=ownerCmds,
                            inline=False)
        await ctx.send(embed=helpEmbed)

    # =================================================
    # Help
    # =================================================

    @help.command(aliases=['h', 'help'])
    async def _help(self, ctx):
        commandName = 'Command Specific'
        syntaxMessage = f"`{gcmds.prefix(ctx)}help [commandName]`"
        exampleUsage = f"`{gcmds.prefix(ctx)}help ping`"
        await self.syntaxEmbed(ctx,
                               commandName=commandName,
                               syntaxMessage=syntaxMessage,
                               exampleUsage=exampleUsage)

    # =================================================
    # Music
    # =================================================

    @help.command()
    async def join(self, ctx):
        commandName = "Join"
        syntaxMessage = f"`{gcmds.prefix(ctx)}join`"
        userPerms = "`Connect to Voice Channel`"
        botPerms = userPerms
        specialCases = "You must currently be connected to a voice channel in order to use this command"
        await self.syntaxEmbed(ctx,
                               commandName=commandName,
                               syntaxMessage=syntaxMessage,
                               userPerms=userPerms,
                               botPerms=botPerms,
                               specialCases=specialCases)

    @help.command()
    async def play(self, ctx):
        commandName = "Play"
        syntaxMessage = f"`{gcmds.prefix(ctx)}play [query or url]`"
        specialCases = "`[query or url]` currently only supports YouTube queries and links. You can play livestreams " \
                       "as well"
        await self.syntaxEmbed(ctx,
                               commandName=commandName,
                               syntaxMessage=syntaxMessage,
                               specialCases=specialCases)

    @help.command()
    async def queue(self, ctx):
        commandName = "Queue"
        syntaxMessage = f"`{gcmds.prefix(ctx)}queue [query or url]`"
        specialCases = "`[query or url]` currently only supports YouTube queries and links. You can play livestreams " \
                       "as well"
        await self.syntaxEmbed(ctx,
                               commandName=commandName,
                               syntaxMessage=syntaxMessage,
                               specialCases=specialCases)

    @help.command(aliases=['clearqueue', 'qc'])
    async def queueclear(self, ctx):
        commandName = "Queue"
        syntaxMessage = f"`{gcmds.prefix(ctx)}queueclear"
        await self.syntaxEmbed(ctx,
                               commandName=commandName,
                               syntaxMessage=syntaxMessage)

    @help.command()
    async def stop(self, ctx):
        commandName = "Stop"
        syntaxMessage = f"`{gcmds.prefix(ctx)}stop`"
        userPerms = "`Bot Owner`"
        await self.syntaxEmbed(ctx,
                               commandName=commandName,
                               syntaxMessage=syntaxMessage,
                               userPerms=userPerms)

    @help.command()
    async def leave(self, ctx):
        commandName = "Leave"
        syntaxMessage = f"`{gcmds.prefix(ctx)}leave`"
        specialCases = "You must currently be connected to a voice channel in order to use this command"
        await self.syntaxEmbed(ctx,
                               commandName=commandName,
                               syntaxMessage=syntaxMessage,
                               specialCases=specialCases)

    @help.command()
    async def volume(self, ctx):
        commandName = "Volume"
        syntaxMessage = f"{gcmds.prefix(ctx)}volume [integer]"
        specialCases = "``[integer]` must be a valid integer between 1 - 100"
        await self.syntaxEmbed(ctx,
                               commandName=commandName,
                               syntaxMessage=syntaxMessage,
                               specialCases=specialCases)

    @help.command(aliases=['playlists'])
    async def playlist(self, ctx):
        commandName = "Playlist"
        syntaxMessage = f"`{gcmds.prefix(ctx)}playlist [optional operation]`"
        specialCases = "If `[optional operation]` is unspecified, it displays your saved playlists\n\n" \
                       "Valid arguments for `[optional operation]`:\n" \
                       "`add [playlistID] [url]` - adds track to playlist *(under development)*\n" \
                       "`load [playlistName]` - loads a playlist to queue\n" \
                       "`save` - saves current queue as a new playlist *alias=edit*\n" \
                       "`remove` - deletes a playlist *(under development)* *aliase=delete*"
        await self.syntaxEmbed(ctx,
                               commandName=commandName,
                               syntaxMessage=syntaxMessage,
                               specialCases=specialCases)

    # =================================================
    # Utility
    # =================================================

    @help.command()
    async def invite(self, ctx):
        commandName = "Invite"
        syntaxMessage = f"`{gcmds.prefix(ctx)}invite`"
        await self.syntaxEmbed(ctx,
                               commandName=commandName,
                               syntaxMessage=syntaxMessage)

    @help.command(aliases=['p', 'checkprefix', 'prefix', 'prefixes'])
    async def _prefix(self, ctx):
        commandName = "Prefix"
        syntaxMessage = f"`{gcmds.prefix(ctx)}prefix`"
        exampleUsage = f"`{gcmds.prefix(ctx)}prefix`"
        exampleOutput = f"`This server's prefix is: {gcmds.prefix(ctx)}`\n\n`The global prefixes are:" \
                        f"`{self.bot.user.mention} or `mbm `"
        await self.syntaxEmbed(ctx,
                               commandName=commandName,
                               syntaxMessage=syntaxMessage,
                               exampleUsage=exampleUsage,
                               exampleOutput=exampleOutput)

    @help.command(aliases=['sp', 'setprefix'])
    async def setPrefix(self, ctx):
        commandName = "Set Prefix"
        syntaxMessage = f"`{gcmds.prefix(ctx)}setprefix [serverprefix]`"
        exampleUsage = f"`{gcmds.prefix(ctx)}setprefix !m`"
        exampleOutput = "`Server prefix set to: !m`"
        specialCases = f"To reset the server prefix to bot default, enter `reset` as the `[serverprefix]` argument"
        await self.syntaxEmbed(ctx,
                               commandName=commandName,
                               syntaxMessage=syntaxMessage,
                               exampleUsage=exampleUsage,
                               exampleOutput=exampleOutput,
                               specialCases=specialCases)

    # =================================================
    # Owner
    # =================================================

    @help.command(aliases=['l', 'ld'])
    async def load(self, ctx):
        commandName = "Load"
        syntaxMessage = f"`{gcmds.prefix(ctx)}load [extension]`"
        userPerms = "`Bot Owner`"
        await self.syntaxEmbed(ctx,
                               commandName=commandName,
                               syntaxMessage=syntaxMessage,
                               userPerms=userPerms)

    @help.command(aliases=['ul', 'uld'])
    async def unload(self, ctx):
        commandName = "Unload"
        syntaxMessage = f"`{gcmds.prefix(ctx)}unload [extension]`"
        userPerms = "`Bot Owner`"
        await self.syntaxEmbed(ctx,
                               commandName=commandName,
                               syntaxMessage=syntaxMessage,
                               userPerms=userPerms)

    @help.command(aliases=['r', 'rl'])
    async def reload(self, ctx):
        commandName = "Reload"
        syntaxMessage = f"`{gcmds.prefix(ctx)}reload [optional extension]`"
        userPerms = "`Bot Owner`"
        specialCases = "If `[optional extension]` is not specified, it will reload all currently loaded extensions"
        await self.syntaxEmbed(ctx,
                               commandName=commandName,
                               syntaxMessage=syntaxMessage,
                               userPerms=userPerms,
                               specialCases=specialCases)

    @help.command(aliases=['taskkill'])
    async def shutdown(self, ctx):
        commandName = "Shutdown"
        syntaxMessage = f"`{gcmds.prefix(ctx)}shutdown`"
        userPerms = "`Bot Owner`"
        await self.syntaxEmbed(ctx,
                               commandName=commandName,
                               syntaxMessage=syntaxMessage,
                               userPerms=userPerms)


def setup(client):
    client.add_cog(Help(client))
