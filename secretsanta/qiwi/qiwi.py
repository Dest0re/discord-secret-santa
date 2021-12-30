from random import choice
import datetime
import asyncio
import string

import aiohttp

from .exceptions import *

REJECT_BILL_URL = 'https://api.qiwi.com/partner/bill/v1/bills/{bill_id}/reject'
CHECK_BILL_URL = 'https://api.qiwi.com/partner/bill/v1/bills/{bill_id}'


class Bill:
    def __init__(self, secret: str, billid: str, value: float, name: str, json: dict):
        self._secret = secret
        self.id = billid
        self.value = value
        self.name = name
        self.payurl = json['payUrl']
        self.rejected = True if json["status"]["value"] == "REJECTED" else False
        self.payed = True if json["status"]["value"] == "PAID" else False
        self.waiting = True if json["status"]["value"] == "WAITING" else False
        self.session = aiohttp.ClientSession()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def wait_for_payment(self, timeout: float):
        async def wait(self):
            while not self.payed and not self.rejected:
                await self._check()
                await asyncio.sleep(5)

        await asyncio.wait_for(wait(self), timeout)

    async def cancel(self):
        url = REJECT_BILL_URL.format(bill_id=self.id)
        headers = {
            "Authorization": f"Bearer {self._secret}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        response = await self.session.post(url, headers=headers)
        json = await response.json()
        if "errorCode" in json:
            raise ApiError(f"Api returned error: {json['errorCode']}")
        self.rejected = True
        self.waiting = False

    async def _check(self):
        url = CHECK_BILL_URL.format(bill_id=self.id)
        headers = {
            "Authorization": f"Bearer {self._secret}",
            "Accept": "application/json"
        }
        response = await self.session.get(url, headers=headers)
        json = await response.json()
        if "errorCode" in json:
            raise ApiError(f"Api returned error: {json['errorCode']}")
        self.rejected = True if json["status"]["value"] == "REJECTED" else False
        self.payed = True if json["status"]["value"] == "PAID" else False
        self.waiting = True if json["status"]["value"] == "WAITING" else False

    async def close(self):
        await self.session.close()


class Qiwi:
    def __init__(self, secret: str):
        self._secret = secret

        self.session = aiohttp.ClientSession()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def create_bill(self, value: float, game_name: str) -> Bill:
        bill_id = "".join(choice(string.ascii_lowercase + string.digits + "-_") for i in range(36))
        expirationdatetime = (datetime.datetime.now() + datetime.timedelta(minutes=15))
        expirationdatetime = expirationdatetime.replace(microsecond=0).isoformat() + "+03:00"
        url = CHECK_BILL_URL.format(bill_id=bill_id)
        data = {
            'amount': {
                'currency': 'RUB',
                'value': str(value)
            },
            'comment': game_name,
            'expirationDateTime': expirationdatetime
        }
        headers = {
            "Authorization": f"Bearer {self._secret}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        print(headers, data)
        response = await self.session.put(url, headers=headers, json=data)
        json = await response.json()
        if "errorCode" in json:
            raise ApiError(f"Api returned error: {json['errorCode']}")
        return Bill(bill_id, value, game_name, json)

    async def cancel_bill(self, bill: Bill):
        await bill.cancel()

    async def check_bill(self, bill: Bill):
        await bill._check()

    async def close(self):
        await self.session.close()


async def main():
    qiwi = Qiwi()
    bill = await qiwi.create_bill(1.0, "test")
    print(bill.payurl)
    await bill.wait_for_payment(300.0)
    print("payment successful")
    await bill.session.close()
    await qiwi.session.close()


if __name__ == "__main__":
    asyncio.run(main())
