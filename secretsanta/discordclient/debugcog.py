import discord
from discord.commands import SlashCommandGroup
from discord.ext import commands

from .basecog import BaseCog
from .handlers import SaveBasicUserInformation, TestHandler, SelectGameHandler, SelectGameRequirementsHandler, SelectGameGenresHandler, SelectPCPerformanceHandler, AskForSteamUrlHandler, MinimalPriceNotify, PaymentHandler


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

    @debug_group.command(name='select_game_requirements', guild_ids=[920707642308055100])
    async def _select_game_requirements(self, ctx: discord.ApplicationContext):
        handler = SelectGameRequirementsHandler()
        handler.set_next(TestHandler())
        await handler.do_handle(ctx)

    @debug_group.command(name='select_pc_performance', guild_ids=[920707642308055100])
    async def _select_pc_performance(self, ctx: discord.ApplicationContext):
        handler = SelectPCPerformanceHandler()
        handler.set_next(TestHandler())
        await handler.do_handle(ctx)

    @debug_group.command(name='select_game_genres', guild_ids=[920707642308055100])
    async def _select_game_genres(self, ctx: discord.ApplicationContext):
        handler = SelectGameGenresHandler()
        handler.set_next(TestHandler())
        await handler.do_handle(ctx)

    @debug_group.command(name='add_steam_profile', guild_ids=[920707642308055100])
    async def _add_steam_profile(self, ctx: discord.ApplicationContext):
        handler = AskForSteamUrlHandler()
        handler.set_next(TestHandler())
        await handler.do_handle(ctx)

    @debug_group.command(name='notify_about_minimal_price', guild_ids=[920707642308055100])
    async def _notify_about_minimal_price(self, ctx: discord.ApplicationContext):
        handler = MinimalPriceNotify()
        await handler.do_handle(ctx)
    
    @debug_group.command(name='buy_game', guild_ids=[920707642308055100])
    async def _buy_game(self, ctx: discord.ApplicationContext):
        handler = PaymentHandler()
        handler.set_next(TestHandler())
        await handler.do_handle(ctx)
