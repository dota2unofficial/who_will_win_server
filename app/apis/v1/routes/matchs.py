from fastapi import APIRouter


router = APIRouter()


@router.post("/before")
async def before_match():
    return {'message': 'Hello world'}


@router.post("/after_match_player")
async def after_match_player():
    return {'message': 'Hello world'}


@router.post("/events")
async def match_events():
    return {'message': 'Hello world'}


@router.post("/update_settings")
async def update_player_setting():
    return {'message': 'Hello world'}


@router.post("/script_errors")
async def script_errors():
    return {'message': 'Hello world'}
