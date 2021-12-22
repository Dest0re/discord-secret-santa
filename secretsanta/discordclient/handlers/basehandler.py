import discord

class BaseHandler:
    def __init__(self):
        self.next: BaseHandler = None

    async def _handle(self, ctx: discord.ApplicationContext):
        pass

    async def do_handle(self, ctx: discord.ApplicationContext):
        await self._handle(ctx)

        if self.next:
            await next.do_handle(ctx)

    def set_next(self, awaitable):
        self.next = awaitable

        return self
