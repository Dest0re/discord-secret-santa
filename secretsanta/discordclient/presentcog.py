import discord
from discord.commands import slash_command

from .basecog import BaseCog
from .handlers import RegionsNotify, TestHandler

from typing import Optional


class PresentCog(BaseCog):
    @slash_command(name='present', guild_ids=[920707642308055100])
    async def _present_command(self, ctx: discord.ApplicationContext, game_url: Optional[str] = None):
        handler = RegionsNotify()
        handler.set_next(TestHandler())
        await handler.do_handle(ctx)
