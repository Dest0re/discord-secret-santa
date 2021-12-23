from discord.ext import commands

from .debugcog import DebugCog
from .presentcog import PresentCog


class CollectBotClient(commands.Bot):
    async def on_ready(self):
        print(f'Logged in Discord as {self.user}')


bot = CollectBotClient(debug_guild=920707642308055100)
bot.add_cog(DebugCog(bot))
bot.add_cog(PresentCog(bot))
