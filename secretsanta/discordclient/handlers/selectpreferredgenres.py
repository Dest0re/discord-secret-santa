import discord

from .basehandler import BaseHandler
from utils.embed import DebugText


class SelectPreferredGenresHandler(BaseHandler):
    async def _handle(self, ctx: discord.ApplicationContext):
        await ctx.respond(embed=DebugText("Выбор предпочитаемых жанров..."))
