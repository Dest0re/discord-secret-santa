import discord

from model import User, DiscordProfile


class StopHandleException(Exception):
    def __init__(self, stage: str):
        super().__init__(stage)


class BaseHandler:
    def __init__(self):
        self._next: BaseHandler = None

    async def _handle(self, ctx: discord.ApplicationContext):
        pass

    async def _exc(self, ctx: discord.ApplicationContext):
        user = (
            User
            .select()
            .join(DiscordProfile)
            .where(DiscordProfile.discord_id == ctx.author.id)
            .get()
        )

        if user:
            user.in_process = False
            user.save()

    async def do_handle(self, ctx: discord.ApplicationContext):
        try:
            await self._handle(ctx)
        except StopHandleException:
            await self._exc(ctx)
        else:
            if self._next:
                await self._next.do_handle(ctx)

    def set_next(self, next_handler):
        self._next = next_handler

        return next_handler
