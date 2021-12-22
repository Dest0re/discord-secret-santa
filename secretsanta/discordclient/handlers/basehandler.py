import discord


class StopHandleException(Exception):
    def __init__(self, stage: str):
        super().__init__(stage)


class BaseHandler:
    def __init__(self):
        self._next: BaseHandler = None

    async def _handle(self, ctx: discord.ApplicationContext):
        pass

    async def _exc(self, ctx: discord.ApplicationContext):
        pass

    async def do_handle(self, ctx: discord.ApplicationContext):
        await self._handle(ctx)

        if self._next:
            await self._next.do_handle(ctx)

    def set_next(self, next_handler):
        try:
            self._next = next_handler
        except StopHandleException:
            self._exc

        return next_handler
