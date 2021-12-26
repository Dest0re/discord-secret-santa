import asyncio

import discord

from .basehandler import BaseHandler, StopHandleException
from utils.embed import DebugText, ErrorText, EmbedText, SuccessText
from model import PCPerformance, User, DiscordProfile
from .view.dropdown import PCPerformanceChooseDropdown, PCPerformanceSelectOption
from utils.strings import text_strings as ts


class SelectPCPerformanceHandler(BaseHandler):
    async def _handle(self, ctx: discord.ApplicationContext):
        user = (
            User
            .select()
            .join(DiscordProfile)
            .where(DiscordProfile.discord_id == ctx.author.id)
            .get()
        )

        if not user:
            await ctx.respond(embed=ErrorText("Пользователь не найден"))
            raise StopHandleException("Select PC performance")

        if user.pc_performance:
            await ctx.respond(embed=DebugText("Пользователь уже выбирал жанры"))
            return

        requirement_list = [PCPerformanceSelectOption(gr, ctx.bot.get_emoji(gr.emoji_id)) for gr in PCPerformance.select()][::-1]

        dropdown = PCPerformanceChooseDropdown(ctx.author, requirement_list)

        message = await ctx.respond(
            embed=EmbedText(ts.pc_performance_select), 
            view=discord.ui.View(dropdown)
        )

        try:
            pc_performance = (await dropdown.get_choices(timeout=120)).pc_performance
        except asyncio.TimeoutError:
            await ctx.respond(embed=ErrorText(ts.timeout_error))
            raise StopHandleException('PC performance select')

        dropdown.disabled = True
        try:
            await message.edit(
                embed=SuccessText(ts.pc_performance_select_success.format(
                    pc_performance_name=pc_performance.name
                )),
                view=discord.ui.View(dropdown)
            )
        except AttributeError:
            await message.edit_original_message(
                embed=SuccessText(ts.pc_performance_select_success.format(
                    pc_performance_name=pc_performance.name
                )),
                view=discord.ui.View(dropdown)
            )

        user.pc_performance = pc_performance
        user.save()