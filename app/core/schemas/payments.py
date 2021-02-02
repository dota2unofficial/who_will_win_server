from pydantic import BaseModel
from typing import Optional


class PaymentCreate(BaseModel):
    steam_id: str
    match_id: int
    method: str
    payment_kind: str
    is_gift_code: Optional[bool] = False
