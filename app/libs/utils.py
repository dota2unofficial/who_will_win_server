from typing import Final

from aiohttp import ClientSession

__Session: Final = ClientSession()


async def close_htts_session():
    await __Session.close()
