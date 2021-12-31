import asyncio
import discord
from discord.embeds import Embed

from .basehandler import BaseHandler, StopHandleException
from .view.button import PersonalYesOrNoButtonsView
from utils.steam import steam_utils, InvalidSteamProfileUrl
from model import User, DiscordProfile, SteamProfile
from utils.embed import SuccessText, ErrorText, DebugText, WarningText, EmbedText
from utils.strings import text_strings as ts


STEAM_PROFILE_URL = 'http://steamcommunity.com/profiles/{steam_id64}'


class GettingProfileSteamUrlError(Exception):
    pass


class AskForSteamUrlHandler(BaseHandler):
    async def _handle(self, ctx: discord.ApplicationContext):
        user = (
            User
            .select()
            .join(DiscordProfile)
            .where(DiscordProfile.discord_id == ctx.author.id)
            .get()
        )

        if not user:
            await ctx.send(embed=ErrorText('В предыдущих шагах что-то пошло не так...'))
            raise StopHandleException('Ask for steam url')

        if user.steam_profile:
            return
        
        await ctx.respond(embed=EmbedText(ts.ask_for_steam_profile_url))

        message = None

        try:
            for _ in range(3):
                message = await ctx.bot.wait_for(
                    'message',
                    check=lambda m: m.author == ctx.author and m.channel == ctx.channel,
                    timeout=120
                )

                if not message.content:
                    await ctx.respond(embed=WarningText(ts.invalid_steam_profile_url))
                    continue

                try:
                    steam_id32, steam_id64 = await steam_utils.id_from_url(message.content)

                    select_view = PersonalYesOrNoButtonsView(ctx.author)
                    confirm_message = await ctx.respond(embed=EmbedText(
                        ts.ask_for_steam_profile_confirm.format(
                            steam_profile_url=STEAM_PROFILE_URL.format(
                                steam_id64=steam_id64
                            )
                        )), 
                        view=select_view
                    )

                    result = await select_view.wait_for_result(timeout=120)

                    if not result:
                        await confirm_message.edit(view=select_view)
                        raise InvalidSteamProfileUrl

                    await confirm_message.edit(view=select_view)

                    user.steam_profile = SteamProfile.get_or_create(steam_id32=steam_id32, steam_id64=steam_id64)[0]
                    user.save()

                    break

                except InvalidSteamProfileUrl:
                    await ctx.respond(embed=WarningText(ts.invalid_steam_profile_url))
                    continue
                    
            else:
                await ctx.respond(embed=ErrorText(ts.error_while_getting_steam_profile_url))
                raise StopHandleException('Ask for steam_url')

        except asyncio.TimeoutError:
            await ctx.respond(embed=ErrorText(ts.timeout_error))
            raise StopHandleException('Ask for steam url')
