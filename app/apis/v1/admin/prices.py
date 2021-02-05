from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from pony.orm import db_session, ObjectNotFound

from .templates import templates
from ....libs.actions import get_price_list
from ....libs.auth import payment_http_auth
from ....core.models.payments import PriceList

router = APIRouter()


@router.get('/price_list')
async def get_price_list_page(
    request: Request,
    user=Depends(payment_http_auth)
):
    price_list = get_price_list(create_session=True)
    return templates.TemplateResponse(
        'prices/pricelist.html',
        {
            'title': 'Prices List',
            'request': request,
            'price_list': price_list
        }
    )


@router.post('/price_list')
async def update_price_list(request: Request, user=Depends(payment_http_auth)):
    data = await request.json()
    with db_session:
        for price_id, new_values in data.items():
            PriceList[int(price_id)].set(**new_values)
    return HTMLResponse(status_code=200)


@router.get('/add_price')
async def add_price(
    payment_name: str,
    price_usd: int,
    price_cny: int,
    item_name: str,
    user=Depends(payment_http_auth)
):
    with db_session:
        existing = PriceList.get(payment_kind=payment_name)
        if existing:
            raise HTTPException(
                400,
                f'ERROR: Payment with kind <{payment_name}> already exists!'
            )
        PriceList(
            payment_kind=payment_name,
            price_usd=price_usd,
            price_cny=price_cny,
            item_name=item_name
        )
    return RedirectResponse(url='/admin/price_list')


@router.get('/remove_price')
async def remove_price(price_id: int, user=Depends(payment_http_auth)):
    with db_session:
        try:
            PriceList[price_id].delete()
        except ObjectNotFound:
            return RedirectResponse(url='/admin/price_list')
    return RedirectResponse(url='/admin/price_list')
