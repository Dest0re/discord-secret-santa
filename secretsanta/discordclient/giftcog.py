import discord
from discord.commands import slash_command

from .basecog import BaseCog
from .handlers import RegionsNotify, SaveBasicUserInformation, \
    SelectGameHandler, PaymentHandler, SelectGameGenresHandler, \
    SelectGameRequirementsHandler, SelectPreferredGenresHandler, \
    SelectPCPerformanceHandler, SuccessHandler


class GiftCog(BaseCog):
    @slash_command(name='gift', guild_ids=[920707642308055100])
    async def _present_command(self, ctx: discord.ApplicationContext):
        handler = RegionsNotify()
        (
            handler 
            .set_next(SaveBasicUserInformation())
            .set_next(SelectGameHandler()) 
            .set_next(PaymentHandler()) 
            .set_next(SelectGameGenresHandler()) 
            .set_next(SelectGameRequirementsHandler()) 
            .set_next(SelectPreferredGenresHandler()) 
            .set_next(SelectPCPerformanceHandler()) 
            .set_next(SuccessHandler())
        )
        await handler.do_handle(ctx)
