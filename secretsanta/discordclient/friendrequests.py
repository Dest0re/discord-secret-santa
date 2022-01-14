import discord
from discord.ext import commands
from peewee import fn

from model import User, DiscordProfile, SteamProfile, Present, GamePackage
from utils.embed import EmbedText, WarningText
from steammarket import SteamStore
from utils.environmentvariables import EnvironmentVariables
from utils.strings import text_strings as ts

env = EnvironmentVariables('STEAM_TOKEN', 'STEAM_LOGIN', 'STEAM_PASSWORD')

steam = SteamStore(env.STEAM_LOGIN, env.STEAM_PASSWORD, env.STEAM_TOKEN)


class SendFriendRequestsBotClient(commands.Bot):
    def __init__(self, *args, **kwargs):
        intents = discord.Intents.default()
        intents.members = True

        super().__init__(
            intents=intents, 
            *args, 
            **kwargs
        )
        
        self._is_ready = False

    async def send_requests(self):
        query = (
            User
            .select()
            .join(Present)
            .join(GamePackage)
            .where(Present.paid == True)
            .group_by(User.id)
            .having(fn.SUM(GamePackage.price) >= 500, User.discord_profile != None)
        )

        for user in set(query):
            
            discord_user = await self.fetch_user(user.discord_profile.discord_id)

            if discord_user:
                if not user.steam_profile:
                    await discord_user.send(embed=WarningText(ts.missed_steam_prыofile_warning))
                    continue

                await steam.add_to_friends(user.steam_profile.steam_id64)

                await discord_user.send(embed=EmbedText(ts.accept_friend_request))

            print(f'{user.discord_profile.discord_id} : {user.steam_profile.steam_id64}')

    async def on_ready(self):
        print(f'Logged in Discord as {self.user}')

        await steam.login()

        if not self._is_ready:
            self._is_ready = True

            await self.send_requests()
