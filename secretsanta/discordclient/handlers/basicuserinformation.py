import discord

from .basehandler import BaseHandler
from model import User, DiscordProfile
from utils.embed import DebugText


class SaveBasicUserInformation(BaseHandler):
    async def _handle(self, ctx: discord.ApplicationContext):
        discord_profile = DiscordProfile.get_or_create(discord_id=ctx.author.id)[0]
        User.get_or_create(discord_profile=discord_profile)[0]
