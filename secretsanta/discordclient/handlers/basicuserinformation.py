import discord

from .basehandler import BaseHandler
from model import User, DiscordProfile
from utils.embed import DebugText


class SaveBasicUserInformation(BaseHandler):
    async def _handle(self, ctx: discord.ApplicationContext):
        discord_profile = DiscordProfile.get_or_create(discord_id=ctx.author.id)[0]
        user = User.get_or_create(discord_profile=discord_profile)[0]

        await ctx.respond(embed=DebugText(f"Ваш id в базе: {user.id}"))
