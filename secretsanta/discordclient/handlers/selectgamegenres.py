import asyncio
import discord

from .basehandler import BaseHandler, StopHandleException
from utils.embed import DebugText, ErrorText, SuccessText, EmbedText
from model import GameGenre, GamePackage, GamePackageGenre, Present, User, DiscordProfile
from .view.dropdown import GameGenreSelectOption, PersonalGameGenreChooseDropdown
from utils.strings import text_strings as ts


class SelectGameGenresHandler(BaseHandler):
    def _check_if_already_selected(self, package: GamePackage):
        genres = (
            GameGenre
            .select()
            .join(GamePackageGenre)
            .join(GamePackage)
            .where(GamePackage.id == package.id)
            .select()
            .execute()
        )
        
        return bool(genres)

    async def _handle(self, ctx: discord.ApplicationContext):
        game_package = (
            GamePackage
            .select()
            .join(Present)
            .join(User)
            .join(DiscordProfile)
            .where(DiscordProfile.discord_id == ctx.author.id)
            .order_by(Present.id.desc())
            .get()
        )

        if not game_package:
            await ctx.respond(embed=ErrorText('На предыдущих этапах что-то пошло не так.'))
            raise StopHandleException("Select game genres")

        if self._check_if_already_selected(game_package):
            return
        
        dropdown = PersonalGameGenreChooseDropdown(ctx.author)

        message = await ctx.respond(
            embed=EmbedText(ts.game_genres_select),
            view=discord.ui.View(dropdown)
        )

        try:
            game_genres = await dropdown.get_choices(120)
            game_genres = [game_genre.game_genre for game_genre in game_genres]
        except asyncio.TimeoutError:
            dropdown.disabled = True
            await message.edit(
                embed=ErrorText(ts.timeout_error),
                view=discord.ui.View(dropdown)
            )
            raise StopHandleException("Game genres select")
        else:
            dropdown.disabled = True
            embed = SuccessText(ts.game_genres_select_success.format(game_genres='\n'.join(map(lambda g: f'**{g.name}**', game_genres))))
            
            try:
                await message.edit(
                    embed=embed,
                    view=discord.ui.View(dropdown)
                )
            except AttributeError:
                await ctx.respond(embed=DebugText("Это в дебаге не работает, но жанры в базу записаны"))

        for genre in game_genres:
            GamePackageGenre.create(game_package=game_package, game_genre=genre)

