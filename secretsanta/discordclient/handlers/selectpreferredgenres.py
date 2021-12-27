import asyncio
import discord

from .basehandler import BaseHandler, StopHandleException
from utils.embed import DebugText, ErrorText, SuccessText, EmbedText
from model import GameGenre, GamePackage, Present, User, DiscordProfile, UserPreferredGenre
from .view.dropdown import GameGenreSelectOption, PersonalGameGenreChooseDropdown
from utils.strings import text_strings as ts


class SelectPreferredGenresHandler(BaseHandler):
    def _check_if_already_selected(self, user: User):
        genres = (
            GameGenre
            .select()
            .join(UserPreferredGenre)
            .join(User)
            .where(User.id == user.id)
            .select()
            .execute()
        )
        
        return bool(genres)

    async def _handle(self, ctx: discord.ApplicationContext):
        user = (
            User
            .select()
            .join(DiscordProfile)
            .where(DiscordProfile.discord_id == ctx.author.id)
            .get()
        )

        if not user:
            await ctx.respond(embed=ErrorText('На предыдущих этапах что-то пошло не так.'))
            raise StopHandleException("Select preferred genres")

        if self._check_if_already_selected(user):
            return
        
        dropdown = PersonalGameGenreChooseDropdown(ctx.author)

        message = await ctx.respond(
            embed=EmbedText(ts.preferred_genres_select),
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
            raise StopHandleException("Preferred game genres select")
        else:
            dropdown.disabled = True
            embed = SuccessText(ts.game_genres_select_success.format(game_genres='\n'.join(map(lambda g: g.name, game_genres))))
            
            try:
                await message.edit(
                    embed=embed,
                    view=discord.ui.View(dropdown)
                )
            except AttributeError:
                await ctx.respond(embed=DebugText("Это в дебаге не работает, но жанры в базу записаны"))

        for genre in game_genres:
            UserPreferredGenre.create(user=user, genre=genre)

