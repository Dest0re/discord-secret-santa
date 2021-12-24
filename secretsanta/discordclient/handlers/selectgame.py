import re
import asyncio

import discord

from .basehandler import BaseHandler, StopHandleException
from utils.strings import text_strings as ts
from utils.embed import EmbedText, ErrorText, DebugText, TitledText, WarningText, SuccessText
from steammarket import SteamStore, Game
from steammarket.exceptions import AppDoesNotExist
from .view.dropdown import GamePackageChooseDropdown, PackageSelectOption

game_url_regex = r'[a-z]+://store.steampowered.com/app/(?P<game_id>\d+)/[a-zA-Z]+/?'

steam_store = SteamStore()

class InvalidGameUrl(Exception):
    pass


class SelectGameHandler(BaseHandler):
    async def _get_game_from_url(self, game_url):
        match = re.match(game_url_regex, game_url)

        if not match:
            raise InvalidGameUrl

        game_id = match.group('game_id')

        game = await steam_store.fetch_app(int(game_id))

        return game

    async def _get_one_package(self, ctx: discord.ApplicationContext, game: Game):
        dropdown = GamePackageChooseDropdown(
            user=ctx.author,
            options=map(lambda gp: PackageSelectOption(gp), game.packages)
        )

        message = await ctx.respond(embed=EmbedText(ts.multiple_packages), view=discord.ui.View(dropdown))

        try:
            package = (await dropdown.get_choices(120)).game_package
        except asyncio.TimeoutError:
            await ctx.respond(embed=ErrorText(ts.timeout_error))
            raise StopHandleException

        dropdown.disabled = True
        await message.edit(
            embed=SuccessText(ts.selected_game.format(game_package_name=package.name)), 
            view=discord.ui.View(dropdown)
        )

        return package


    async def _handle(self, ctx: discord.ApplicationContext):
        await ctx.respond(embed=EmbedText(ts.game_url_request))

        try:
            message = None
            for _ in range(3):
                message = await ctx.bot.wait_for(
                    'message', 
                    check=lambda m: m.channel == ctx.channel and m.author == ctx.author,
                    timeout=300
                )

                try:
                    game = await self._get_game_from_url(message.content)

                    game_package = None

                    if len(game.packages) > 1:
                        game_package = await self._get_one_package(ctx, game)
                    else:
                        game_package = game.packages[0]
                    
                    await ctx.respond(embed=DebugText(f"Выбрана игра: {game_package.name}"))

                except InvalidGameUrl:
                    await ctx.respond(embed=WarningText(ts.invalid_game_url))
                    continue
                except AppDoesNotExist:
                    await ctx.respond(embed=WarningText(ts.app_does_not_exist))
                    continue
                else:
                    break
                    
            else:
                await ctx.respond(embed=ErrorText(ts.url_get_error))
                raise StopHandleException("Game url get")
                
            
        except asyncio.TimeoutError:
            await ctx.respond(embed=ErrorText(ts.timeout_error))
            raise StopHandleException("Game url get")
