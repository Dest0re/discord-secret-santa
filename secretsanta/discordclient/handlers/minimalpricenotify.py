import asyncio
import discord
from peewee import fn

from .basehandler import BaseHandler, StopHandleException
from .view.button import PersonalAcceptButton
from model import User, DiscordProfile, Present, GamePackage, connection
from utils.embed import DebugText, WarningText, ErrorText
from utils.strings import text_strings as ts

MINIMAL_PRICE = 500


class MinimalPriceNotify(BaseHandler):
    async def _handle(self, ctx: discord.ApplicationContext):
        user_gifts = (
            GamePackage
            .select()
            .join(Present)
            .join(User)
            .join(DiscordProfile)
            .where(DiscordProfile.discord_id == ctx.author.id, Present.paid == True)
        )

        present_price = user_gifts.select(fn.SUM(GamePackage.price)).scalar()
        present_price = 0 if present_price == None else present_price

        if present_price >= MINIMAL_PRICE:
            await ctx.respond(embed=DebugText('Пользователь подарил достаточно, предупреждение слать не надо'))
            return
        
        button = PersonalAcceptButton(ctx.author)

        message = await ctx.respond(
            embed=WarningText(
                ts.minimal_price_notification.format(
                    minimal_price=MINIMAL_PRICE,
                    estimate=MINIMAL_PRICE - present_price
                )
            ), 
            view=discord.ui.View(button)
        )

        try:
            await button.wait_for_accept()
        except asyncio.TimeoutError:
            await ctx.respond(embed=ErrorText(ts.timeout_error))
            raise StopHandleException("Minimal present price notify")
        finally:
            button.disabled = True
            await message.edit(view=discord.ui.View(button))
