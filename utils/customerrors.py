import discord
from discord.ext import commands



class CannotPaginate(commands.CommandError):
    """Error raised when the paginator cannot paginate

    Args:
        message (str): message that will be sent in traceback
    """

    def __init__(self, message):
        self.message = message


class NoBoundChannel(commands.CommandError):
    def __init__(self):
        self.embed = discord.Embed(title="No Music Channel Bound",
                                   description="You must bind MarwynnBot's music commands to a channel",
                                   color=discord.Color.dark_red())


class NotBoundChannel(commands.CommandError):
    def __init__(self, channel_id):
        self.embed = discord.Embed(title="Not Bound Channel",
                                   description=f"Execute music commands in <#{channel_id}>",
                                   color=discord.Color.dark_red())


class PremiumError(commands.CommandError):
    pass


class NoPremiumGuilds(PremiumError):
    """Error raised when there are no guilds that are MarwynnBot Premium guilds
    """

    def __init__(self):
        self.embed = discord.Embed(title="No MarwynnBot Premium Members",
                                   description="There are no servers registered as MarwynnBot Premium servers \:(",
                                   color=discord.Color.dark_red())


class NoPremiumUsers(PremiumError):
    """Error raised when the current guild contains no MarwynnBot Premium users
    """

    def __init__(self):
        self.embed = discord.Embed(title="No MarwynnBot Premium Members",
                                   description="This server does not have any MarwynnBot Premium members \:(",
                                   color=discord.Color.dark_red())


class NoGlobalPremiumUsers(NoPremiumUsers):
    """Error raised when no user is MarwynnBot Premium
    """

    def __init__(self):
        super().__init__()
        self.embed.description = "There are currently MarwynnBot Premium users"


class NotPremiumGuild(PremiumError):
    """Error raised when the current guild is not a MarwynnBot Premium guild

    Args:
        guild (discord.Guild): the current guild
    """

    def __init__(self, guild: discord.Guild):
        self.embed = discord.Embed(title="Not MarwynnBot Premium",
                                   description=f"This guild, {guild.name}, must have a MarwynnBot Premium Server Subscription"
                                   " to use this command",
                                   color=discord.Color.dark_red())


class NotPremiumUser(PremiumError):
    """Error raised when the current user is not a MarwynnBot Premium user

    Args:
        user (discord.User): the current user
    """

    def __init__(self, user: discord.User):
        self.embed = discord.Embed(title="Not MarwynnBot Premium",
                                   description=f"{user.mention}, you must have a MarwynnBot Premium User Subscription to use this command",
                                   color=discord.Color.dark_red())


class NotPremiumUserOrGuild(PremiumError):
    """Error raised when the current user and guild are both not MarwynnBot Premium

    Args:
        user (discord.User): the current user
        guild (discord.Guild): the current guild
    """

    def __init__(self, user: discord.User, guild: discord.Guild):
        self.embed = discord.Embed(title="Not MarwynnBot Premium",
                                   description=f"{user.mention}, you or this server, {guild.name}, must have a "
                                   "MarwynnBot Premium Server Subscription to use this command",
                                   color=discord.Color.dark_red())


class UserPremiumException(PremiumError):
    """Error raised when there is an exception while performing a premium operation on a user

    Args:
        user (discord.User): the user the error occured with
    """

    def __init__(self, user: discord.User):
        self.embed = discord.Embed(title="Set Premium Error",
                                   description=f"An error occured when trying to operate on {user.display_name}",
                                   color=discord.Color.dark_red())


class UserAlreadyPremium(UserPremiumException):
    """Error raised when the user already has MarwynnBot Premium

    Args:
        user (discord.User): the user the error occured with
    """

    def __init__(self, user: discord.User):
        super().__init__(user)
        self.embed.description = f"{user.display_name} already has a MarwynnBot Premium subscription"


class GuildPremiumException(PremiumError):
    """Error raised when there is an exception while performing a premium operation on a guild

    Args:
        guild (discord.Guild): the guild the error occured with
    """

    def __init__(self, guild: discord.Guild):
        self.embed = discord.Embed(title="Set Premium Error",
                                   description=f"An error occured when trying to operate on {guild.name}",
                                   color=discord.Color.dark_red())


class GuildAlreadyPremium(GuildPremiumException):
    """Error raised when the guild already has MarwynnBot Premium

    Args:
        guild (discord.Guild): the guild the error occured with
    """

    def __init__(self, guild: discord.Guild):
        super().__init__(guild)
        self.embed.description = f"{guild.name} already has a MarwynnBot Premium subscription"


class MBConnectedError(commands.CommandError):
    def __init__(self, channel: discord.VoiceChannel):
        self.embed = discord.Embed(title="MarwynnBot Already Connected",
                                   description=f"MarwynnBot is already connected to {channel.name}. Please have me join another voice channel",
                                   color=discord.Color.dark_red())