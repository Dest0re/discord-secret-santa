import asyncio

import discord
from discord.ext import commands

from .debugcog import DebugCog


class BotClient(commands.Bot):
    async def on_ready(self):
        print(f'Logged in Discord as {self.user}')


bot = BotClient(debug_guild=920707642308055100)
bot.add_cog(DebugCog(bot))