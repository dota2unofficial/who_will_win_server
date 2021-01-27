from fastapi import APIRouter


router = APIRouter()


@router.post("/create")
async def create_payment():
    return {'message': 'Hello world'}


@router.post("/stripe")
async def stripe_webhook():
    return {'message': 'Hello world'}


@router.get("/result")
async def payment_result():
    return {'message': 'Hello world'}
