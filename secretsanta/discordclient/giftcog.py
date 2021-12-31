import discord
from discord.ext import commands
from discord.commands import slash_command

from .basecog import BaseCog
from .handlers import RegionsNotify, SaveBasicUserInformation, \
    SelectGameHandler, PaymentHandler, SelectGameGenresHandler, \
    SelectGameRequirementsHandler, SelectPreferredGenresHandler, \
    SelectPCPerformanceHandler, SuccessHandler, AskForSteamUrlHandler, \
    MinimalPriceNotify, CheckIfInProcess, BeginGiftingProcess, EndGiftingProcess, AddGiftMessage


class GiftCog(BaseCog):
    @slash_command(name='gift')
    @commands.dm_only()
    async def _present_command(self, ctx: discord.ApplicationContext):
        handler = SaveBasicUserInformation()
        (
            handler
            .set_next(CheckIfInProcess())
            .set_next(BeginGiftingProcess())
            .set_next(RegionsNotify())
            .set_next(AskForSteamUrlHandler())
            .set_next(MinimalPriceNotify())
            .set_next(SelectGameHandler()) 
            .set_next(PaymentHandler()) 
            .set_next(AddGiftMessage())
            .set_next(SelectGameGenresHandler()) 
            .set_next(SelectGameRequirementsHandler()) 
            .set_next(SelectPreferredGenresHandler()) 
            .set_next(SelectPCPerformanceHandler()) 
            .set_next(SuccessHandler())
            .set_next(EndGiftingProcess())
        )
        await handler.do_handle(ctx)
