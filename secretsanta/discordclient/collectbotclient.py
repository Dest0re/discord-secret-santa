import discord
from discord.commands import errors
from discord.ext import commands
from discord.ext.commands.errors import PrivateMessageOnly

from .debugcog import DebugCog
from .giftcog import GiftCog
from model import User
from utils.embed import ErrorText

from utils.strings import text_strings as ts


class CollectBotClient(commands.Bot):
    async def on_ready(self):
        User.update(in_process=False).execute()

        await self.change_presence(activity=discord.Game(ts.collection_stage_status_text))
        print(f'Logged in Discord as {self.user}')

    async def on_command_error(self, ctx: discord.ApplicationContext, error):
        if isinstance(error, commands.errors.PrivateMessageOnly):
            await ctx.respond(embed=ErrorText(ts.only_dm_error), ephemeral=True)


bot = CollectBotClient()
bot.add_cog(DebugCog(bot))
bot.add_cog(GiftCog(bot))
