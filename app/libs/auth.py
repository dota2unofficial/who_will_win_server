import os
from fastapi import Request, HTTPException, status
from pony.orm import db_session

from .logging import logger
from ..core.models.keys import DedicatedKeys


@db_session
async def lua_auth(request: Request):
    if not bool(os.getenv('TEST_ENV', False)):
        return True
    dedi_key: str = request.headers.get("Dedicated-Server-Key", None)
    if not dedi_key or not DedicatedKeys.exists(key=dedi_key):
        logger.info(f"Lua auth key mismatch: {dedi_key}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Incorrect Dedicated-Server-Key'
        )
    return True
