import os

from fastapi import FastAPI

from .core.setting import Settings
from .libs.logging import logger
from .libs.utils import close_htts_session

from .apis.v1.routes.matchs import router as match_routers
from .apis.v1.routes.payments import router as payment_routers

if not bool(os.getenv('DEBUG_ENV', False)):
    app = FastAPI(
        title='Who_Will_Win API',
        description='This is a web server for Who_Will_Win custom game',
        version='1.0.0'
    )
else:
    app = FastAPI(
        docs_url=None,
        redoc_url=None,
        title='Who_Will_Win API',
        description='This is a web server for Who_Will_Win custom game',
        version='1.0.0'
    )


@app.get('/')
def index():
    return {'message': 'Hello world'}


app.include_router(
    match_routers,
    prefix="/api/v1/match",
    tags=["Match"]
)

app.include_router(
    payment_routers,
    prefix="/api/v1/payment",
    tags=["Payment"]
)


@app.on_event('startup')
async def init_setting():
    logger.info('[startup] process started')
    Settings.stripe_connection
    Settings.assemble_db_connection
    logger.info('[startup] process finished')


@app.on_event('shutdown')
async def on_shutdown():
    await close_htts_session()
    await Settings.shutdown()
    logger.info('[shutdown] process finished')
