import discord
from discord.commands import SlashCommandGroup
from discord.ext import commands

from .basecog import BaseCog
from .handlers import SaveBasicUserInformation, TestHandler, SelectGameHandler


class DebugCog(BaseCog):
    debug_group = SlashCommandGroup('debug', 'Debug features. Admin only!', guild_ids=[920707642308055100])

    @debug_group.command(name='ping')
    async def _ping_command(self, ctx: discord.ApplicationContext):
        await ctx.respond('Pong!')

    @debug_group.command(name='register_simple_user', guild_ids=[920707642308055100])
    async def _register_simple_user(self, ctx: discord.ApplicationContext):
        handler = SaveBasicUserInformation()
        handler.set_next(TestHandler())
        await handler.do_handle(ctx)

    @debug_group.command(name='register_new_game', guild_ids=[920707642308055100])
    async def _register_new_game(self, ctx: discord.ApplicationContext):
        handler = SelectGameHandler()
        handler.set_next(TestHandler())
        await handler.do_handle(ctx)
