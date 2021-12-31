import discord
from discord.ext import commands

from .debugcog import DebugCog
from .giftcog import GiftCog
from model import User


class CollectBotClient(commands.Bot):
    async def on_ready(self):
        User.update(in_process=False).execute()

        await self.change_presence(activity=discord.Game('/gift в ЛС!'))
        print(f'Logged in Discord as {self.user}')


bot = CollectBotClient()
bot.add_cog(DebugCog(bot))
bot.add_cog(GiftCog(bot))
