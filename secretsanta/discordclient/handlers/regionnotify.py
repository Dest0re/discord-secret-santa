import asyncio

import discord
from discord.enums import ButtonStyle

from .basehandler import BaseHandler
from utils.embed import EmbedText
from utils.strings import text_strings as ts


class AcceptButton(discord.ui.Button):
        def __init__(self, member: discord.Member):
            self._member = member
            self._is_active = True

            super().__init__(
                style=ButtonStyle.green,
                emoji="✔️"
            )
        
        async def callback(self, interaction: discord.Interaction):
            if self._is_active:
                if interaction.user != self._member:
                    await interaction.response.send_message(embed=EmbedText(ts.someone_elses_interaction_warning), ephemeral=True)
                else:
                    self._is_active = False
                    self.disabled = True
        
        async def wait_for_accept(self):
            while self._is_active:
                await asyncio.sleep(0.1)


class RegionsNotify(BaseHandler):
    async def _handle(self, ctx: discord.ApplicationContext):
        accept_button = AcceptButton(ctx.author)
        view = discord.ui.View(accept_button)
        await ctx.respond(
            embed=EmbedText(ts.region_warning),
            view=view
        )

        await accept_button.wait_for_accept()

        await ctx.edit(view=view)
