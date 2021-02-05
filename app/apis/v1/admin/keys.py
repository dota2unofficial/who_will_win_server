from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from pony.orm import db_session

from ....core.models.keys import DedicatedKeys
from .templates import templates
from ....libs.auth import dedikeys_http_auth

router = APIRouter()


@router.get('/dedicated_keys')
def get_dedicated_keys_page(
    request: Request,
    user=Depends(dedikeys_http_auth)
):
    with db_session:
        dedicated_keys = list(DedicatedKeys.select())
    return templates.TemplateResponse(
        'keys/dedikeys.html',
        {
            'title': 'Dedicated Keys',
            'request': request,
            'keys': dedicated_keys
        }
    )


@router.post('/dedicated_keys')
async def update_dedicated_keys_page(
    request: Request,
    user=Depends(dedikeys_http_auth)
):
    data = await request.json()
    with db_session:
        for dedicated_key_id, new_values in data.items():
            DedicatedKeys[int(dedicated_key_id)].set(**new_values)
    return HTMLResponse(status_code=200)


@router.get('/add_dedicated_key')
async def add_dedicated_key(
    dedicated_key: str,
    user=Depends(dedikeys_http_auth)
):
    with db_session:
        DedicatedKeys(Key=dedicated_key)
    return RedirectResponse(url='/admin/dedicated_keys')


@router.get('/remove_dedicated_key')
async def remove_dedicated_key(
    dedicated_key_id: int,
    user=Depends(dedikeys_http_auth)
):
    with db_session:
        DedicatedKeys[dedicated_key_id].delete()
    return RedirectResponse(url='/admin/dedicated_keys')
