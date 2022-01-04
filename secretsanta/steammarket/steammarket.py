import aiohttp
import asyncio
import contextvars
import sys
import functools
import base64
import time
import os

import rsa
from bs4 import BeautifulSoup
import js2py

from .exceptions import *
from model import gamegenre, GamePackage, gamepackagegenre, ModelPrototype
from utils.strings import text_strings as ts
from utils import EnvironmentVariables


errors = {
    "11": "user_in_black_list_error",
    "15": "friend_list_full_error",
    "24": "account_does_not_fit_error",
    "25": "my_friend_list_full_error",
    "40": "in_black_list_error",
    "41": "try_again_later_error",
    "84": "too_many_requests_error"
}


class Package(ModelPrototype):
    def __init__(self):
        self.id = 0
        self.name = ''
        self.price = 0

    def __model__(self):
        return GamePackage.get_or_create(steam_id=self.id, name=self.name, price=self.price)


class Game:
    def __init__(self, id=None, name=None, packages=None, is_dlc=None):
        self.id = id if id is not None else 0
        self.name = name if name is not None else ""
        self.packages = packages if packages is not None else []
        self.is_dlc = is_dlc if is_dlc is not None else False


class FriendRequest:
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

    def __del__(self):
        asyncio.create_task(self.close())

    async def wait_for_accept(self, timeout: float or int):
        async def wait():
            while not self.accepted:
                await self._check()
                await asyncio.sleep(10)

        try:
            await asyncio.wait_for(wait(), timeout=timeout)
        finally:
            await self.close()

    async def _check(self):
        url = "http://api.steampowered.com/ISteamUser/GetFriendList/v1"
        params = {
            "key": self.api_key,
            "steamid": str(self.bot_id)
        }
        response = await self.session.get(url, params=params)
        json_response = await response.json()
        if str(self.id) in [str(i['steamid']) for i in json_response['friendslist']['friends']]:
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


class SteamStore:
    def __init__(self):
        self.StoreURL = "https://store.steampowered.com"
        self.CommunityURL = "https://steamcommunity.com"
        self.cookiejar = aiohttp.CookieJar()
        if os.path.exists("saved_cookies"):
            self.cookiejar.load("saved_cookies")
            self.logged_in = True
        self.session = aiohttp.ClientSession(trust_env=True, cookie_jar=self.cookiejar)
        self.logged_in = False
        self.api_key = None
        self.id = None

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    def __del__(self):
        asyncio.create_task(self.close())

    async def login(self) -> None:
        username = EnvironmentVariables("STEAM_USERNAME")
        password = EnvironmentVariables("STEAM_PASSWORD")
        api_key = EnvironmentVariables("STEAM_APIKEY")
        await self.session.get(url=f"{self.StoreURL}/?l=russian")
        params = {
            "review_score_preference": 0,
            "l": "russian",
            "pagev6": "true"
        }
        values = f"?username={username}"
        response = await self.session.get(url=f"{self.StoreURL}/login/getrsakey/{values}", params=params)
        json_response = await response.json()
        publickey_mod = int(json_response['publickey_mod'], 16)
        publickey_exp = int(json_response['publickey_exp'], 16)
        rsa_timestamp = json_response['timestamp']
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
        json_response = await response.json()
        captchagid = "-1"
        captcha_text = ""
        if not json_response['success'] and json_response['message'] != "":
            raise LoginError(json_response['message'])
        elif json_response.get("captcha_needed"):
            captchagid = json_response["captcha_gid"]
            print(f"Нужно решить капчу: https://steamcommunity.com/login/rendercaptcha/?gid={captchagid}")
            captcha_text = to_thread(input, "Нужен текст капчи >>> ")
        while not json_response['success']:
            twofactor = await to_thread(input, "Нужен код SteamGuard >>> ") \
                if json_response['requires_twofactor'] else ""
            emailauth = await to_thread(input, f"Нужен код из почты {json_response['emaildomain']} >>> ") \
                if json_response['emailauth_needed'] else ""
            data['twofactorcode'] = twofactor
            data['emailauth'] = emailauth
            data['captchagid'] = captchagid
            data['captcha_text'] = captcha_text
            response = await self.session.post(f"{self.StoreURL}/login/dologin/", data=data)
            json_response = await response.json()
        parameters = json_response['transfer_parameters']
        for url in json_response['transfer_urls']:
            await self.session.post(url=url, data=parameters)
        response = await self.session.get(self.CommunityURL)
        text = await response.text()
        soup = BeautifulSoup(text, "html.parser")
        steam_id = js2py.eval_js([i for i in soup.find("div", class_="responsive_page_content").find_all("script")
                                   if "PHP" in i.text][0].text.replace("\r", "").replace("\n", "").replace("\t",
                                   "").replace("\\", "").split(";g_strLanguage")[0])
        self.logged_in = True
        self.id = steam_id
        self.api_key = api_key

    async def fetch_app(self, app_id: int) -> Game:
        url = f"{self.StoreURL}/api/appdetails/?appids={app_id}&cc=RU&l=russian&v=1"
        response = await self.session.get(url)
        json_response = (await response.json())[str(app_id)]
        if not json_response['success']:
            raise AppDoesNotExist("App does not exist")
        game = Game()
        game.id = json_response['data']['steam_appid']
        game.name = json_response['data']['name']
        game.is_dlc = json_response['data']['type'] == "dlc"
        for package in json_response['data']['package_groups'][0]['subs']:
            pack = Package()
            pack.id = package['packageid']
            pack.price = package['price_in_cents_with_discount'] / 100
            pack.name = "".join(i + ' - ' for i in package["option_text"].split(" - ")[:-1])[:-3]
            game.packages.append(pack)
        return game

    async def fetch_package(self, package_id: int) -> Package:
        url = f"{self.StoreURL}/api/packagedetails/?packageids={package_id}&cc=RU&l=russian&v=1"
        response = await self.session.get(url)
        json_response = (await response.json())[str(package_id)]
        if not json_response['success']:
            raise PackageDoesNotExist("Package does not exist")
        package = Package()
        package.name = json_response['data']['name']
        package.id = package_id
        package.price = int(json_response['data']['price']['final']) / 100
        return package

    async def _add_to_cart(self, package_id: int) -> None:
        if not self.logged_in:
            raise LoginRequired("You need to login first")
        url = f"{self.StoreURL}/api/addtocart/?packageids={package_id}"
        response = await self.session.get(url)
        json_response = await response.json()
        if not json_response['success']:
            raise ApiError(f"Failed. Response: {json_response}")

    async def buy_gifts(self, packages_id, steam_id32: int, username: str, message: str, signature: str) -> None:
        if not self.logged_in:
            raise LoginRequired("You need to login first")
        url = "https://store.steampowered.com/cart/"
        response = await self.session.get(url)
        soup = BeautifulSoup(await response.text(), "html.parser")
        url = soup.find("a", id="btn_purchase_gift").get("href")
        response = await self.session.get(url)
        if response.status == 302:
            await self.login()
        for package_id in packages_id:
            await self._add_to_cart(package_id)
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
            "GifteeAccountID": str(steam_id32),
            "GifteeEmail": "",
            "GifteeName": username,
            "GiftMessage": message,
            "Sentiment": "С наилучшими пожеланиями", # Поменять
            "Signature": signature,
            "ScheduledSendOnDate": "0",
            "BankAccount": "",
            "BankCode": "",
            "BankIBAN": "",
            "BankBIC": "",
            "TPBankID": "",
            "BankAccountID": "",
            "bSaveBillingAddress": "0",
            "gidPaymentID": "",  # В случай если привязан Paypal или карточка
            "bUseRemainingSteamAccount": "0",
            "bPreAuthOnly": "0",
            "sessionid": sessionid
        }
        url = f"{self.StoreURL}/checkout/inittransaction/"
        response = await self.session.post(url, data=data)
        json_response = await response.json()
        if str(json_response['success']) != "1":
            raise PaymentError("PaymentError")
        transid = json_response['transid']
        url = f"{self.StoreURL}/checkout/getfinalprice/?count=1&transid={transid}&purchasetype=gift" \
              f"&microtxnid=-1&cart={gidShoppingCart}&gidReplayOfTransID=-1"
        await self.session.get(url)
        url = f"{self.StoreURL}/checkout/finalizetransaction/"
        data = {
            "transid": str(transid),
            "CardCVV2": "000",
            "browserInfo": '{"language": "en-US", "javaEnabled": "false", '
                           '"colorDepth": 24, "screenHeight": 1080, "screenWidth": 1920}'
        }
        await self.session.post(url, data=data)
        for i in range(1, 4):
            url = f"{self.StoreURL}/checkout/transactionstatus/?count={i}&transid={transid}"
            response = await self.session.get(url)
            json_response = await response.json()
            if str(json_response['success']) == "1":
                break
            await asyncio.sleep(2)
        url = f"{self.StoreURL}/checkout/logsuccessfulpurchase"
        await self.session.post(url)

    async def add_to_friends(self, steam_id64: int) -> FriendRequest:
        if not self.logged_in:
            raise LoginRequired("You need to login first")
        response = await self.session.get(f"{self.CommunityURL}")
        text = await response.text()
        soup = BeautifulSoup(text, "html.parser")
        sessionid = js2py.eval_js([i for i in soup.find("div", class_="responsive_page_content").find_all("script")
                     if "PHP" in i.text][0].text.replace("\r", "").replace("\n", "").replace("\t", "").replace(
                    "\\", "").split(";g_steamID")[0])
        url = f"{self.CommunityURL}/actions/AddFriendAjax"
        data = f"sessionID={sessionid}&steamid={steam_id64}&accept_invite=0"
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
            "Cookie": "".join(f"{cookie.key}={cookie.value}; "
                              for key, cookie in self.session.cookie_jar.filter_cookies(self.StoreURL).items())[:-2],
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "Sec-GPC": "1"
        }
        response = await self.session.post(url, headers=headers, data=data)
        json_response = await response.json()
        if json_response is False:
            raise FriendInviteError(f"Steam returned False. data={data}")
        if "failed_invites" in json_response:
            error = str(json_response['failed_invites_result'][0])
            if error != "41" and error in errors:
                raise FriendInviteError(getattr(ts, errors[error]))
            elif error != "41":
                raise FriendInviteError("Unknown error happened.")
            else:
                print("WARNING: Friend Request invite returned 41")
        return FriendRequest(bot_id=self.id, friend_id=steam_id64, api_key=self.api_key)

    async def user_games(self, steam_id64):
        url = f"https://steamcommunity.com/profiles/{steam_id64}/games?tab=all&xml=1"
        response = await self.session.get(url)
        soup = BeautifulSoup(await response.text(), "html.parser")
        games = []
        for game in soup.find_all("game"):
            app_id = game.appid.text
            fetched_game = self.fetch_app(app_id)
            games.append(fetched_game)
        return games

    async def close(self) -> None:
        self.session.cookie_jar.save("saved_cookies")
        await self.session.close()
