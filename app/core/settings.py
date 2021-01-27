from typing import Any, Dict, Optional

import stripe
from pony import orm
from pony.orm.core import BindingError
from pony.orm.dbapiprovider import ProgrammingError
from pydantic import BaseSettings

from ..libs.logging import logger


db = orm.Database()


class Settings(BaseSettings):
    DB_PROVIDER: str
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: str
    STRIPE_SECRET: str
    STEAM_WEBAPI_KEY: str

    def db_connect(
        self, v: Optional[str], values: Dict[str, Any]
    ) -> Any:
        if isinstance(v, str):
            return v
        db_provider = values.get('DB_PROVIDER')
        db_user = values.get('DB_USER')
        db_password = values.get('DB_PASSWORD')
        db_host = values.get('DB_HOST')
        db_port = values.get('DB_PORT')
        db_name = values.get('DB_NAME')

        print(f'Connecting to {db_provider} databse with user: {db_user}, ' +
              f'password: {db_password}, host: {db_host}, ' +
              f'port: {db_port}, database: {db_name}')
        logger.info(
            f'Connecting to {db_provider} databse with user: {db_user}, ' +
            f'password: {db_password}, host: {db_host}, ' +
            f'port: {db_port}, database: {db_name}')

        try:
            if db_provider == 'postgres':
                db.bind(
                    'postgres',
                    user=db_user,
                    password=db_password,
                    host=db_host,
                    port=db_port,
                    database=db_name
                )
            elif db_provider == 'mysql':
                db.bind(
                    'mysql',
                    user=db_user,
                    passwd=db_password,
                    host=db_host,
                    db=db_name
                )
            elif db_provider == 'sqlite':
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
        except ProgrammingError as e:
            print(f'Failed in connectiong to database: {e}')
            logger.error(f'Failed in connectiong to database: {e}')

    async def shutdown(self):
        db.disconnect()

    def stripe_connect(
        self, v: Optional[str], values: Dict[str, Any]
    ) -> Any:
        if isinstance(v, str):
            return v
        secret_key = values.get('STRIPE_SECRET')
        stripe.api_key = secret_key

    class Config:
        case_sensitive = True
        env_file = '.env'


settings = Settings()
