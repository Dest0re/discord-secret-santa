from os import removedirs
import re
import asyncio

import aiohttp

from .environmentvariables import EnvironmentVariables

env = EnvironmentVariables('STEAM_TOKEN')


STEAM_PROFILE_LINK_REGEX = r'https://steamcommunity.com/id/(?P<vanity_id>.+)/?.+'
ID_GET_URL = 'http://api.steampowered.com/ISteamUser/ResolveVanityURL/v0001/'


class InvalidSteamProfileUrl(Exception):
    pass


class SteamUtils:
    def __init__(self, token):
        self._token = token
        self._session = aiohttp.ClientSession(trust_env=True)
    
    def __del__(self):
        asyncio.get_event_loop().create_task(self._session.close())

    async def id_from_url(self, url: str):
        match = re.match(STEAM_PROFILE_LINK_REGEX, url)
        if not match:
            raise InvalidSteamProfileUrl

        params = {
            'key': self._token,
            'vanityurl': match.group('vanity_id')
        }

        async with self._session.get(ID_GET_URL, params=params) as response:
            if not response.ok:
                raise InvalidSteamProfileUrl

            json_response = (await response.json())['response']
        
        if json_response['success'] != 1:
            raise InvalidSteamProfileUrl
        
        steamid64 = int(json_response['steamid'])
        steamid32 = steamid64 & 0b11111111111111111111111111111111

        return steamid32, steamid64


steam_utils = SteamUtils(env.STEAM_TOKEN)
