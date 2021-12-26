import aiohttp
import asyncio
import contextvars
import sys
import functools
import base64
import time

import rsa

from .exceptions import *
from model import gamegenre, GamePackage, gamepackagegenre, ModelPrototype


class Package(ModelPrototype):
    def __init__(self):
        self.id = 0
        self.name = ''
        self.price = 0
    
    def __model__(self):
        return GamePackage.get_or_create(steam_id=self.id, name=self.name, price=self.price)


class Game:
    def __init__(self):
        self.id = 0
        self.name = ''
        self.packages = []


if sys.version_info >= (3, 9):
    from asyncio import to_thread
else:
    async def to_thread(callable, *args, **kwargs):
        loop = asyncio.get_running_loop()
        ctx = contextvars.copy_context()
        partial = functools.partial(ctx.run, callable, *args, **kwargs)
        return await loop.run_in_executor(None, partial)


def login_required(func):
    def func_wrapper(self, *args, **kwargs):
        if not self.logged_in:
            raise LoginRequired('Use login method first on SteamClient')
        else:
            return func(self, *args, **kwargs)

    return func_wrapper


class SteamStore:
    def __init__(self):
        self.StoreURL = "https://store.steampowered.com"
        self.session = aiohttp.ClientSession(trust_env=True)
        self.logged_in = False

    async def login(self, username, password) -> None:
        await self.session.get(url=f"{self.StoreURL}/?l=russian")
        params = {
            "review_score_preference": 0,
            "l": "russian",
            "pagev6": "true"
        }
        values = f"?username={username}"
        response = await self.session.get(url=f"{self.StoreURL}/login/getrsakey/{values}", params=params)
        json = await response.json()
        publickey_mod = int(json['publickey_mod'], 16)
        publickey_exp = int(json['publickey_exp'], 16)
        rsa_timestamp = json['timestamp']
        encrypted_password = \
            base64.b64encode(rsa.encrypt(password.encode('utf-8'), rsa.PublicKey(publickey_mod, publickey_exp)))
        data = {
            'password': encrypted_password.decode("utf-8"),
            'username': username,
            'twofactorcode': '',
            'emailauth': '',
            'loginfriendlyname': '',
            'captchagid': '-1',
            'captcha_text': '',
            'emailsteamid': '',
            'rsatimestamp': rsa_timestamp,
            'remember_login': 'true',
            'donotcache': str(int(time.time() * 1000)),
            'tokentype': '-1'
        }
        response = await self.session.post(f"{self.StoreURL}/login/dologin/", data=data)
        json = await response.json()
        while not json['success']:
            twofactor = await to_thread(input, "Нужен код SteamGuard >>> ") if json['requires_twofactor'] else ""
            emailauth = await to_thread(input, f"Нужен код из почты {json['emaildomain']} >>> ") if json['emailauth_needed'] else ""
            data['twofactorcode'] = twofactor
            data['emailauth'] = emailauth
            response = await self.session.post(f"{self.StoreURL}/login/dologin/", data=data)
            json = await response.json()
        parameters = json['transfer_parameters']
        for url in json['transfer_urls']:
            print(parameters)
            await self.session.post(url=url, data=parameters)
        self.logged_in = True

    async def fetch_app(self, app_id: int) -> Game:
        url = f"{self.StoreURL}/api/appdetails/?appids={app_id}&cc=RU&l=russian&v=1"
        response = await self.session.get(url)
        json = (await response.json())[str(app_id)]
        if not json['success']:
            raise AppDoesNotExist("App does not exist")
        game = Game()
        game.id = json['data']['steam_appid']
        game.name = json['data']['name']
        for package in json['data']['package_groups'][0]['subs']:
            pack = Package()
            pack.id = package['packageid']
            pack.price = package['price_in_cents_with_discount'] // 100
            pack.name = "".join(i + ' - ' for i in package["option_text"].split(" - ")[:-1])[:-3]
            game.packages.append(pack)
        return game

    async def fetch_package(self, package_id: int) -> Package:
        url = f"{self.StoreURL}/api/packagedetails/?packageids={package_id}&cc=RU&l=russian&v=1"
        response = await self.session.get(url)
        json = (await response.json())[str(package_id)]
        if not json['success']:
            raise PackageDoesNotExist("App does not exist")
        package = Package()
        package.name = json['data']['name']
        package.id = package_id
        package.price = int(json['data']['price']['final']) // 100
        return package

    @login_required
    async def add_to_cart(self, package_id: int) -> None:
        url = f"{self.StoreURL}/api/addtocart/?packageids={package_id}"
        response = await self.session.get(url)
        json = await response.json()
        if not json['success']:
            raise ApiError(f"Failed. Response: {json}")

    async def close(self):
        await self.session.close()


async def main():
    steam = SteamStore()
    response = await steam.fetch_app(924970)
    print(response.name)
    response = await steam.fetch_package(54029)
    print(response.name)
    await steam.close()


if __name__ == "__main__":
    asyncio.run(main())
