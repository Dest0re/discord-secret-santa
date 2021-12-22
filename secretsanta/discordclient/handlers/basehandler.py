import discord


class BaseHandler:
    def __init__(self):
        self._next: BaseHandler = None

    async def _handle(self, ctx: discord.ApplicationContext):
        pass

    async def do_handle(self, ctx: discord.ApplicationContext):
        await self._handle(ctx)

        if self._next:
            await self._next.do_handle(ctx)

    def set_next(self, next_handler):
        self._next = next_handler

        return next_handler
