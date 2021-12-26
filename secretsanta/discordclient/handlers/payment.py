import discord

from .basehandler import BaseHandler, StopHandleException
from utils.embed import DebugText, ErrorText, SuccessText
from model import Present, User, DiscordProfile
from utils.strings import text_strings as ts


class PaymentHandler(BaseHandler):
    async def _handle(self, ctx: discord.ApplicationContext):
        await ctx.respond(embed=DebugText("Оплата... (всегда успешная)"))
        
        present = (
            Present
            .select()
            .join(User)
            .join(DiscordProfile)
            .where(DiscordProfile.discord_id == ctx.author.id)
            .order_by(Present.id.desc())
            .get()
        )

        if not present:
            await ctx.send(embed=ErrorText("Подарок не найден"))
            raise StopHandleException("Payment")
        
        present.paid = True
        present.save()

        await ctx.respond(embed=SuccessText(ts.payment_success))
