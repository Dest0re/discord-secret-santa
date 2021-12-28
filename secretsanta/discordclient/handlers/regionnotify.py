import asyncio

import discord
from discord.enums import ButtonStyle

from .basehandler import BaseHandler
from .view.button import PersonalAcceptButton
from utils.embed import EmbedText
from utils.strings import text_strings as ts


class RegionsNotify(BaseHandler):
    async def _handle(self, ctx: discord.ApplicationContext):
        accept_button = PersonalAcceptButton(ctx.author)
        view = discord.ui.View(accept_button)
        await ctx.respond(
            embed=EmbedText(ts.region_warning),
            view=view
        )

        await accept_button.wait_for_accept()

        await ctx.edit(view=view)
