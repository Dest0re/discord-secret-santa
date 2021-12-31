from random import choice
from datetime import datetime, timedelta
import asyncio
import string

import aiohttp

#from .exceptions import *

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

    def __del__(self):
        asyncio.create_task(self.close())

    async def wait_for_payment(self, timeout: float):
        async def wait(self):
            while not self.payed and not self.rejected:
                await self._check()
                await asyncio.sleep(5)

        try:
            await asyncio.wait_for(wait(self), timeout)
        finally:
            await self.close()


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
        await self.close()

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

    def __del__(self):
        asyncio.create_task(self.close)

    async def create_bill(self, value: float, comment: str) -> Bill:
        bill_id = "".join(choice(string.ascii_lowercase + string.digits + "-_") for i in range(36))
        expirationdatetime = (datetime.now().replace(microsecond=0) + timedelta(minutes=15)).isoformat() + "+03:00"
        url = CHECK_BILL_URL.format(bill_id=bill_id)
        data = {
            'amount': {
                'currency': 'RUB',
                'value': str(value)
            },
            'comment': comment,
            'expirationDateTime': expirationdatetime
        }
        headers = {
            "Authorization": f"Bearer {self._secret}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        response = await self.session.put(url, headers=headers, json=data)
        json = await response.json()
        if "errorCode" in json:
            raise ApiError(f"Api returned error: {json['errorCode']}")
        return Bill(self._secret, bill_id, value, comment, json)

    async def cancel_bill(self, bill: Bill):
        await bill.cancel()
        await bill.close()

    async def check_bill(self, bill: Bill):
        await bill._check()

    async def close(self):
        await self.session.close()
