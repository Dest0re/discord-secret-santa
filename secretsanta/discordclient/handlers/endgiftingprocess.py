import discord

from .basehandler import BaseHandler, StopHandleException
from model import User, DiscordProfile
from utils.embed import ErrorText
from utils.strings import text_strings as ts


class EndGiftingProcess(BaseHandler):
    async def _exc(self, ctx: discord.ApplicationContext):
        pass
    
    async def _handle(self, ctx: discord.ApplicationContext):
        user = (
            User
            .select()
            .join(DiscordProfile)
            .where(DiscordProfile.discord_id == ctx.author.id)
            .get()
        )

        if not user:
            return

        user.in_process = False
        user.save()
