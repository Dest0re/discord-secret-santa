import re
import asyncio

import discord

from .basehandler import BaseHandler, StopHandleException
from utils.strings import text_strings as ts
from utils.embed import EmbedText, ErrorText, DebugText

game_url_regex = r'[a-z]+://store.steampowered.com/app/\d+/[a-zA-Z]+/?'


class SelectGameHandler(BaseHandler):
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

                if re.match(game_url_regex, message.content):
                    await ctx.respond(embed=DebugText("Тут должен быть выбор пакета через выпадающий список"))
                    break
                else:
                    await ctx.respond(embed=ErrorText(ts.invalid_game_url))
            else:
                await ctx.respond(embed=ErrorText(ts.url_get_error))
                raise StopHandleException("Game url get")
                
            
        except asyncio.TimeoutError:
            await ctx.respond(embed=ErrorText(ts.timeout_error))
            raise StopHandleException("Game url get")
