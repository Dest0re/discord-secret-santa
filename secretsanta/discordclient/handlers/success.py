import discord

from .basehandler import BaseHandler
from utils.embed import SuccessText


class SuccessHandler(BaseHandler):
    async def _handle(self, ctx: discord.ApplicationContext):
        await ctx.respond(embed=SuccessText("Всё готово! Игра добавлена! \nСпасибо и с наступающим!"))
