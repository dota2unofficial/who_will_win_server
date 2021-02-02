from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates


templates = Jinja2Templates(
    directory="app/templates"
)
router = APIRouter()


@router.get('/admin/v1/statistics/{map_name}')
async def get_statistics_page(request: Request, map_name: str):
    return {'message': 'Hello world'}


@router.get('/admin/script-errors')
async def get_script_error_page(request: Request):
    return {'message': 'Hello world'}


@router.get('/admin/script-errors-clear')
async def clear_script_errors(request: Request):
    return {'message': 'Hello world'}


@router.post('/reset_exp_limit')
async def reset_daily_exp():
    return {'message': 'Hello world'}
