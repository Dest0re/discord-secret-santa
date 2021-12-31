import asyncio

import discord

from .basehandler import BaseHandler, StopHandleException
from utils.embed import DebugText, SuccessText, EmbedText, ErrorText
from utils.strings import text_strings as ts
from model import GamePackage, GameRequirements, User, DiscordProfile, Present
from .view.dropdown import GameRequirementsChooseDropdown, GameRequirementsSelectOption


class SelectGameRequirementsHandler(BaseHandler):
    async def _handle(self, ctx: discord.ApplicationContext):
        package = (
            GamePackage
            .select()
            .join(Present)
            .join(User)
            .join(DiscordProfile)
            .where(
                DiscordProfile.discord_id == ctx.author.id,
                Present.paid == True
            )
            .order_by(Present.id.desc())
            .limit(1)
            .get()
        )

        if not package:
            await ctx.respond(embed=DebugText('Не нашли подарка'))
            raise StopHandleException('Game requirements select')

        if package.requirements:
            return

        requirement_list = [GameRequirementsSelectOption(gr, ctx.bot.get_emoji(gr.emoji_id)) for gr in GameRequirements.select()][::-1]

        dropdown = GameRequirementsChooseDropdown(ctx.author, requirement_list)

        message = await ctx.respond(
            embed=EmbedText(ts.select_game_requirements), 
            view=discord.ui.View(dropdown)
        )

        try:
            game_requirements = (await dropdown.get_choices(timeout=120)).game_requirements
        except asyncio.TimeoutError:
            await ctx.respond(embed=ErrorText(ts.timeout_error))
            raise StopHandleException('Game requirements select')

        dropdown.disabled = True
        try:
            await message.edit(
                embed=SuccessText(ts.select_game_requirements_success.format(
                    game_requirements_name=game_requirements.name
                )),
                view=discord.ui.View(dropdown)
            )
        except AttributeError:
            await message.edit_original_message(
                embed=SuccessText(ts.select_game_requirements_success.format(
                    game_requirements_name=game_requirements.name
                )),
                view=discord.ui.View(dropdown)
            )

        package.requirements = game_requirements
        package.save()
