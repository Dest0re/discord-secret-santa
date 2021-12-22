import discord
from discord.commands import SlashCommandGroup
from discord.ext import commands

from .basecog import BaseCog


class DebugCog(BaseCog):
    debug_group = SlashCommandGroup('debug', 'Debug features. Admin only!', guild_ids=[920707642308055100])

    @debug_group.command(name='ping')
    async def _ping_command(self, ctx: discord.commands.ApplicationContext):
        await ctx.respond('Pong!')
