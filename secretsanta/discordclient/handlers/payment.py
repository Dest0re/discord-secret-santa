import asyncio
import discord

from .basehandler import BaseHandler, StopHandleException
from utils.embed import DebugText, ErrorText, SuccessText, EmbedText
from model import Present, User, DiscordProfile
from utils.strings import text_strings as ts
from utils.environmentvariables import EnvironmentVariables
import qiwi

env = EnvironmentVariables('QIWI_SECRET')

payment = qiwi.Qiwi(env.QIWI_SECRET)


class PaymentHandler(BaseHandler):
    async def _handle(self, ctx: discord.ApplicationContext):
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
        
        
        bill = await payment.create_bill(
            value=present.game_package.price,
            comment=ts.payment_form_comment.format(game_name=present.game_package.name)
        )

        await ctx.respond(
            embed=EmbedText(
                ts.request_payment.format(
                    game_price=present.game_package.price,
                    pay_url=bill.payurl
                )
            ), 
            ephemeral=True
        )

        try:
            await bill.wait_for_payment(300)
            pass
        except asyncio.TimeoutError:
            await bill.cancel()
            await ctx.respond(embed=ErrorText(ts.timeout_error))
            raise StopHandleException("Payment")

        present.paid = True
        present.save()

        await ctx.respond(embed=SuccessText(ts.payment_success))
