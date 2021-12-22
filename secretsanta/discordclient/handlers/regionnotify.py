import asyncio

import discord
from discord.enums import ButtonStyle

from .basehandler import BaseHandler
from utils.embed import EmbedText

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
                    await interaction.response.send_message(embed=EmbedText('Это не твоё.'), ephemeral=True)
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
            embed=EmbedText("Сейчас мы поддерживаем не все регионы. Если вы живёте не в одном из этих: (список), то будьте осторожны: вы всё ещё сможете подарить игру по вашей региональной цене, но вряд ли мы сумеем отправить подарок вам в ответ!"),
            view=view
        )

        await accept_button.wait_for_accept()

        await ctx.edit(view=view)
