import os
import secrets

from fastapi import Request, HTTPException, status, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pony.orm import db_session

from .logging import logger
from ..core.settings import settings
from ..core.models.keys import DedicatedKeys

security = HTTPBasic()


def check_passwords(
    credentials: HTTPBasicCredentials,
    expected_credentials: dict
):
    correct_username = secrets.compare_digest(
        credentials.username,
        expected_credentials['login']
    )
    correct_password = secrets.compare_digest(
        credentials.password,
        expected_credentials['password']
    )
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Incorrect email or password',
            headers={'WWW-Authenticate': 'Basic'},
        )
    return credentials.username


@db_session
async def lua_auth(request: Request):
    if not bool(os.getenv('TEST_ENV')):
        return True
    dedi_key: str = request.headers.get('Dedicated-Server-Key', None)
    if not dedi_key or not DedicatedKeys.exists(key=dedi_key):
        logger.info(f'Lua auth key mismatch: {dedi_key}')
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Incorrect Dedicated-Server-Key'
        )
    return True


async def http_auth(credentials: HTTPBasicCredentials = Depends(security)):
    return check_passwords(credentials, {
        'login': settings.ADMIN_USER,
        'password': settings.ADMIN_PASS,
    })


async def dedikeys_http_auth(
    credentials: HTTPBasicCredentials = Depends(security)
):
    return check_passwords(credentials, {
        'login': settings.DEDICATED_USER,
        'password': settings.DEDICATED_PASS,
    })


async def payment_http_auth(
    credentials: HTTPBasicCredentials = Depends(security)
):
    return check_passwords(credentials, {
        'login': settings.PAYMENT_USER,
        'password': settings.PAYMENT_PASS
    })
