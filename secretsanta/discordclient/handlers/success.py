import discord

from .basehandler import BaseHandler
from utils.embed import SuccessText
from utils.strings import text_strings as ts


class SuccessHandler(BaseHandler):
    async def _handle(self, ctx: discord.ApplicationContext):
        await ctx.respond(embed=SuccessText(ts.game_add_success))
