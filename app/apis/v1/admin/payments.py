import base64
import io
from typing import Optional

import qrcode
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse

from ....libs.logging import logger
from ....core.settings import settings
from .templates import templates

router = APIRouter()


@router.get('/payments/checkout', response_class=HTMLResponse)
async def get_payment_page(request: Request, id: Optional[str]):
    logger.info('SESSION ID: ', id)
    publishable_key = settings.STRIPE_PUBLISHABLE
    return templates.TemplateResponse(
        'payments/checkout.html',
        {
            'title': 'Checkout',
            'request': request,
            'publishable_key': publishable_key,
            'session_id': id
        }
    )


@router.get('/payments/result', response_class=HTMLResponse)
async def get_payment_result_page(
    request: Request,
    session_id: Optional[str] = None
):
    print('PAYMENT Status:', session_id)

    return templates.TemplateResponse(
        'payments/result.html',
        {
            'request': request,
            'session_id': session_id
        }
    )


@router.get('/payments/wechat', response_class=HTMLResponse)
async def get_wechat_payment_page(request: Request, qr: Optional[str]):
    if not qr:
        raise HTTPException(status_code=404)
    qr_code = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_Q,
        border=0
    )
    qr_code.add_data(qr)
    qr_code.make()
    img = qr_code.make_image(
        fill_color='black',
        back_color='white'
    )
    buffered = io.BytesIO()
    img.save(buffered, format='PNG')
    img_str = base64.b64encode(
        buffered.getvalue()
    ).decode('utf-8')
    return templates.TemplateResponse(
        'payments/wechat.html',
        {
            'request': request,
            'qr_code': img_str
        }
    )
