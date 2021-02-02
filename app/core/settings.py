from typing import Final
import stripe
from pydantic import BaseSettings
from pony.orm.core import BindingError
from pony.orm.dbapiprovider import ProgrammingError
from aiohttp import ClientSession

from ..libs.logging import logger
from .models.db import db
from .models import *

__Session: Final = ClientSession()


class Settings(BaseSettings):
    DB_PROVIDER: str
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: str
    STEAM_WEBAPI_KEY: str
    STRIPE_SECRET: str = (
        'sk_test_51HL7fDGFJ5EJYxIJ7jXNoasDDExu2rs6hXiItU46IMu' +
        'CIyBf2KQ0coSZoQWAm2k3PJogolrE3OOIXkkVdZaV9pSs00CWxI3bvZ'
    )
    PAYMENT_RETURN_URL: str = 'http://localhost:5000/'
    STRIPE_WEBHOOK_SECRET: str = 'whsec_FQkgYFcA5Z7HIwdEGhLRDgnl9gzRlSy9'

    async def db_connect(self):
        print(
            f'Connecting to {self.DB_PROVIDER} databse ' +
            f'with user: {self.DB_USER}, ' +
            f'password: {self.DB_PASSWORD}, host: {self.DB_HOST}, ' +
            f'port: {self.DB_PORT}, database: {self.DB_NAME}')
        logger.info(
            f'Connecting to {self.DB_PROVIDER} databse ' +
            f'with user: {self.DB_USER}, ' +
            f'password: {self.DB_PASSWORD}, host: {self.DB_HOST}, ' +
            f'port: {self.DB_PORT}, database: {self.DB_NAME}')

        try:
            if self.DB_PROVIDER == 'postgres':
                db.bind(
                    provider='postgres',
                    user=self.DB_USER,
                    password=self.DB_PASSWORD,
                    host=self.DB_HOST,
                    port=self.DB_PORT,
                    database=self.DB_NAME
                )
            elif self.DB_PROVIDER == 'mysql':
                db.bind(
                    'mysql',
                    user=self.DB_USER,
                    passwd=self.DB_PASSWORD,
                    host=self.DB_HOST,
                    db=self.DB_NAME
                )
            elif self.DB_PROVIDER == 'sqlite':
                db.bind(
                    'sqlite',
                    'database_file.sqlite',
                    create_db=True
                )
        except BindingError as e:
            print(e)
            logger.error(e)

        try:
            db.generate_mapping(create_tables=True)
            print('generate_mapping')
        except ProgrammingError as e:
            print(f'Failed in connectiong to database: {e}')
            logger.error(f'Failed in connectiong to database: {e}')

    async def shutdown(self):
        db.disconnect()

    async def stripe_connect(self):
        secret_key = self.STRIPE_SECRET
        stripe.api_key = secret_key
        logger.info('Stripe Key has been set.')

    async def close_htts_session(self):
        await __Session.close()

    class Config:
        case_sensitive = True
        env_file = '.env'


settings = Settings()
