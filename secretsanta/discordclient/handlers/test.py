import discord
from .basehandler import BaseHandler
from utils.embed import EmbedText


class TestHandler(BaseHandler):
    async def _handle(self, ctx: discord.ApplicationContext):
        await ctx.respond(embed=EmbedText("Это сообщение должно отправиться только после предыдущего шага, но не одновременно с ним."))
