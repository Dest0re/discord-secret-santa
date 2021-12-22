import discord
from .basehandler import BaseHandler, StopHandleException
from utils.embed import EmbedText, ErrorText


class TestHandler(BaseHandler):
    async def _handle(self, ctx: discord.ApplicationContext):
        await ctx.respond(embed=EmbedText("Это сообщение должно отправиться только после предыдущего шага, но не одновременно с ним."))

    async def _exc(self, ctx: discord.ApplicationContext):
        await ctx.respond(embed=ErrorText('Это запланированная ошибка'))
