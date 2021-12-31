import discord
import asyncio

from .basehandler import BaseHandler, StopHandleException
from model import User, DiscordProfile, GamePackage, Present
from utils.embed import ErrorText, EmbedText
from utils.strings import text_strings as ts


class AddGiftMessage(BaseHandler):
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
            await ctx.respond(embed=ErrorText('На предыдущих шагах что-то пошло не так...'))
            raise StopHandleException("Add gift message")
        
        message = await ctx.respond(embed=EmbedText(ts.ask_for_gift_message))

        try:
            user_message = await ctx.bot.wait_for('message', check=lambda m: m.channel == ctx.channel and m.author == ctx.author, timeout=120)
        except asyncio.TimeoutError:
            await ctx.respond(embed=ErrorText(ts.timeout_error))
            raise StopHandleException("Add gift message")
        
        present.comment = user_message.content[:300]
        present.save()
