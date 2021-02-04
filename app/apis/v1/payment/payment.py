import sys
from typing import Optional

import stripe
from fastapi import APIRouter, Request, BackgroundTasks, Response, status
from fastapi.responses import HTMLResponse

from ....libs.logging import logger
from ....core.schemas.payments import PaymentCreate
from ....core.settings import settings
from ..admin.templates import templates
from .manager import (
    PaymentMetaData,
    create_payment_request,
    charge_payment,
    finish_payment
)

router = APIRouter()


@router.post('/create')
def create_payment(data: PaymentCreate):
    metadata = PaymentMetaData(
        data.steam_id,
        data.payment_kind,
        data.match_id,
        data.is_gift_code
    )
    try:
        url = create_payment_request(data.method, metadata)
    except Exception:
        logger.error(f'Exception in payment creation: {sys.exc_info()}')
        url = ''
    return {'url': url}


@router.post('/stripe')
async def stripe_webhook(request: Request, tasks: BackgroundTasks):
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET
    payload = await request.body()
    sig_header = request.headers.get('stripe-signature', None)
    if not sig_header:
        return Response(status_code=status.HTTP_401_UNAUTHORIZED)
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload,
            sig_header,
            endpoint_secret
        )
    except ValueError as e:
        # Invalid payload
        logger.info(f"Value error: invalid payload, {e}")
        return Response(status_code=400)
    except stripe.error.SignatureVerificationError as e:
        logger.info(f"Stripe error: invalid signature, {e}")
        # Invalid signature
        return Response(status_code=400)
    logger.info(f"event type: {event['type']}")
    # Handle the checkout.session.completed event
    if event['type'] == 'source.chargeable':
        logger.info("[Stripe webhook] Payment is chargeable")
        charge_payment(event, tasks)
    if event['type'] == 'checkout.session.completed':
        logger.info("[Stripe webhook] Payment complete")
        finish_payment(event, tasks)
    if event['type'] == 'charge.succeeded':
        logger.info(f"[Stripe webhook] charge succeeded {event}")
    return Response(status_code=200)


@router.get('/result', response_class=HTMLResponse)
async def payment_successful(
    request: Request,
    session_id: Optional[str] = None
):
    print('PAYMENT Status:', session_id)

    return templates.TemplateResponse(
        'payments/result.html',
        {
            'title': 'Checkout Result',
            'request': request,
            'session_id': session_id
        }
    )
