import discord

from .basehandler import BaseHandler
from utils.embed import DebugText


class SelectGameGenresHandler(BaseHandler):
    async def _handle(self, ctx: discord.ApplicationContext):
        await ctx.respond(embed=DebugText("Выбор жанров..."))
