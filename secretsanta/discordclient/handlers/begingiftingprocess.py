import discord

from .basehandler import BaseHandler, StopHandleException
from model import User, DiscordProfile
from utils.embed import ErrorText
from utils.strings import text_strings as ts


class BeginGiftingProcess(BaseHandler):    
    async def _handle(self, ctx: discord.ApplicationContext):
        user = (
            User
            .select()
            .join(DiscordProfile)
            .where(DiscordProfile.discord_id == ctx.author.id)
            .get_or_none()
        )

        if not user:
            return

        user.in_process = True
        user.save()
