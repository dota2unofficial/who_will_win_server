import os

from fastapi import FastAPI

from .core.setting import Settings
from .utils.logging import logger

if bool(os.getenv('DEBUG_ENV', False)):
    app = FastAPI(title='Who_Will_Win API')
else:
    app = FastAPI(docs_url=None, redoc_url=None, title='Who_Will_Win API')


@app.get('/')
def index():
    return {'message': 'Hello world'}


@app.on_event('startup')
async def init_setting():
    logger.info('[startup] process started')
    Settings.stripe_connection
    Settings.assemble_db_connection
    logger.info('[startup] process finished')
