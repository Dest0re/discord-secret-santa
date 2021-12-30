import aiohttp
import asyncio
import contextvars
import sys
import functools
import base64
import time

import rsa
from bs4 import BeautifulSoup
import js2py

from .exceptions import *
from model import gamegenre, GamePackage, gamepackagegenre, ModelPrototype
from strings import errors


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


class Friend:
    def __init__(self, friend_id: int, bot_id: int, api_key: str):
        self.id = friend_id
        self.bot_id = bot_id
        self.api_key = api_key
        self.session = aiohttp.ClientSession()
        self.accepted = False

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def wait_for_accept(self, timeout: float or int):
        async def wait():
            while not self.accepted:
                await self._check()
                await asyncio.sleep(5)

        await asyncio.wait_for(wait(), timeout=timeout)

    async def _check(self):
        url = "http://api.steampowered.com/ISteamUser/GetFriendList/v1"
        params = {
            "key": self.api_key,
            "steamid": str(self.bot_id)
        }
        response = await self.session.get(url, params=params)
        json = await response.json()
        if str(self.id) in [str(i['steamid']) for i in json['friendslist']['friends']]:
            self.accepted = True

    async def close(self):
        await self.session.close()


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
        self.CommunityURL = "https://steamcommunity.com"
        self.session = aiohttp.ClientSession(trust_env=True)
        self.logged_in = False
        self.api_key = None
        self.id = None

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def login(self, username, password, api_key) -> None:
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
        message = "There have been too many login failures from your network in a short time period.  " \
                  "Please wait and try again later."
        if json['message'] == message:
            raise TooManyRequests(message)
        while not json['success']:
            twofactor = await to_thread(input, "Нужен код SteamGuard >>> ") if json['requires_twofactor'] else ""
            emailauth = await to_thread(input, f"Нужен код из почты {json['emaildomain']} >>> ") \
                if json['emailauth_needed'] else ""
            data['twofactorcode'] = twofactor
            data['emailauth'] = emailauth
            response = await self.session.post(f"{self.StoreURL}/login/dologin/", data=data)
            json = await response.json()
        parameters = json['transfer_parameters']
        for url in json['transfer_urls']:
            await self.session.post(url=url, data=parameters)
        response = await self.session.get(self.CommunityURL)
        text = await response.text()
        soup = BeautifulSoup(text, "lxml")
        steam_id = js2py.eval_js([i for i in soup.find("div", class_="responsive_page_content").find_all("script")
                                   if "PHP" in i.text][0].text.replace("\r", "").replace("\n", "").replace("\t",
                                   "").replace("\\", "").split(";g_strLanguage")[0])
        self.logged_in = True
        self.id = steam_id
        self.api_key = api_key

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
            pack.price = package['price_in_cents_with_discount'] / 100
            pack.name = "".join(i + ' - ' for i in package["option_text"].split(" - ")[:-1])[:-3]
            game.packages.append(pack)
        return game

    async def fetch_package(self, package_id: int) -> Package:
        url = f"{self.StoreURL}/api/packagedetails/?packageids={package_id}&cc=RU&l=russian&v=1"
        response = await self.session.get(url)
        json = (await response.json())[str(package_id)]
        if not json['success']:
            raise PackageDoesNotExist("Package does not exist")
        package = Package()
        package.name = json['data']['name']
        package.id = package_id
        package.price = int(json['data']['price']['final']) / 100
        return package

    @login_required
    async def add_to_cart(self, package_id: int) -> None:
        url = f"{self.StoreURL}/api/addtocart/?packageids={package_id}"
        response = await self.session.get(url)
        json = await response.json()
        if not json['success']:
            raise ApiError(f"Failed. Response: {json}")

    @login_required
    async def buy_gift(self, friend_id: int) -> None:
        gidShoppingCart = self.session.cookie_jar.filter_cookies(self.StoreURL)['shoppingCartGID'].value
        sessionid = self.session.cookie_jar.filter_cookies(self.StoreURL)['sessionid'].value
        data = {
            "gidShoppingCart": gidShoppingCart,
            "gidReplayOfTransID": "-1",
            "PaymentMethod": "", # visa/mastercard
            "abortPendingTransactions": "0",
            "bHasCardInfo": "1",
            "CardNumber": "", # сюда номер карты
            "CardExpirationYear": "", # сюда год истечения карты
            "CardExpirationMonth": "", # сюда месяц истечения карты
            "FirstName": "Ivan",
            "LastName": "Ivanov",
            "Address": "Lenina 1",
            "AddressTwo": "",
            "Country": "RU",
            "City": "Moscow",
            "State": "",
            "PostalCode": "101000",
            "Phone": "79012345678",
            "ShippingFirstName": "Ivan",
            "ShippingLastName": "Ivanov",
            "ShippingAddress": "Lenina 1",
            "ShippingAddressTwo": "",
            "ShippingCountry": "RU",
            "ShippingCity": "Moscow",
            "ShippingState": "",
            "ShippingPostalCode": "101000",
            "ShippingPhone": "79012345678",
            "bIsGift": "1",
            "GifteeAccountID": str(friend_id),
            "GifteeEmail": "",
            "GifteeName": "User", # Поменять
            "GiftMessage": "Бип буп бип", # Поменять
            "Sentiment": "С наилучшими пожеланиями", # Поменять
            "Signature": "Secret Santa", # Поменять
            "ScheduledSendOnDate": "0",
            "BankAccount": "",
            "BankCode": "",
            "BankIBAN": "",
            "BankBIC": "",
            "TPBankID": "",
            "BankAccountID": "",
            "bSaveBillingAddress": "0",
            "gidPaymentID": "",
            "bUseRemainingSteamAccount": "0",
            "bPreAuthOnly": "0",
            "sessionid": sessionid
        }
        url = f"{self.StoreURL}/checkout/inittransaction/"
        response = await self.session.post(url, data=data)
        json = await response.json()
        if str(json['success']) != "1":
            raise PaymentError("PaymentError")
        transid = json['transid']
        url = f"{self.StoreURL}/checkout/getfinalprice/?count=1&transid={transid}&purchasetype=gift&microtxnid=-1&cart={gidShoppingCart}&gidReplayOfTransID=-1"
        await self.session.get(url)
        url = f"{self.StoreURL}/checkout/finalizetransaction/"
        data = {
            "transid": str(transid),
            "CardCVV2": "000",
            "browserInfo": '{"language": "en-US", "javaEnabled": "false", "colorDepth": 24, "screenHeight": 1080, "screenWidth": 1920}'
        }
        await self.session.post(url, data=data)
        for i in range(1, 4):
            url = f"{self.StoreURL}/checkout/transactionstatus/?count={i}&transid={transid}"
            response = await self.session.get(url)
            json = await response.json()
            if str(json['success']) == "1":
                break
            await asyncio.sleep(2)
        url = f"{self.StoreURL}/checkout/logsuccessfulpurchase"
        await self.session.post(url)

    @login_required
    async def add_to_friends(self, friend_id: int, friend_name: str) -> Friend:
        response = await self.session.get(f"{self.CommunityURL}/id/{friend_name}")
        text = await response.text()
        soup = BeautifulSoup(text, "lxml")
        sessionid = js2py.eval_js([i for i in soup.find("div", class_="responsive_page_content").find_all("script")
                     if "PHP" in i.text][0].text.replace("\r", "").replace("\n", "").replace("\t", "").replace(
                    "\\", "").split(";g_steamID")[0])
        url = f"{self.CommunityURL}/actions/AddFriendAjax"
        data = f"sessionID={sessionid}&steamid={friend_id}&accept_invite=0"
        headers = {
            "Host": "steamcommunity.com",
            "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:95.0) Gecko/20100101 Firefox/95.0",
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "X-Requested-With": "XMLHttpRequest",
            "Content-Length": str(len(str(data))),
            "Origin": f"{self.CommunityURL}",
            "Connection": "keep-alive",
            "Referer": f"{self.CommunityURL}/id/{friend_name}",
            "Cookie": "".join(f"{cookie.key}={cookie.value}; " for key, cookie in self.session.cookie_jar.filter_cookies(self.StoreURL).items())[:-2],
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "Sec-GPC": "1"
        }
        response = await self.session.post(url, headers=headers, data=data)
        json = await response.json()
        if "failed_invites" in json:
            error = str(json['failed_invites_result'][0])
            if error != "41" and error in errors:
                raise FriendInviteError(errors[error])
            elif error != "41":
                raise FriendInviteError("Unknown error happened.")
            else:
                print("WARNING: Friend invite returned 41")
        return Friend(bot_id=self.id, friend_id=friend_id, api_key=self.api_key)

    async def close(self) -> None:
        await self.session.close()


async def main():
    pass


if __name__ == "__main__":
    asyncio.run(main())
