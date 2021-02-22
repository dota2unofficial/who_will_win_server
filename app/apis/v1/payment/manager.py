import math
from typing import Tuple
from hashlib import md5
from pprint import pprint
from datetime import datetime, timedelta

import stripe
from fastapi import HTTPException, status, BackgroundTasks
from pony.orm import db_session

from ....core.settings import settings
from ....libs.constants import (
    CONST_SUPPORTER_FORTUNE_REWARD,
    CONST_SUPPORTER_EXP_REWARD,
    CONST_SUPPORTER_GLORY_REWARD
)
from ....libs.logging import logger
from ....libs.functions import (
    get_bp_required_exp,
    add_battle_pass_exp,
    keys_lower,
    steam_id_to_str
)
from ....core.models.payments import PriceList, GiftCodes, ItemSellingHistory
from ....core.models.players import Player
from ....core.models.inventory import PlayerInventory
from ....core.models.matchs import MatchEvent


payment_url = settings.PAYMENT_RETURN_URL


class PaymentMetaData:
    def __init__(
        self,
        steam_id: str,
        payment_kind: str,
        match_id: int,
        is_gift_code: bool = False
    ):
        self.steam_id = int(steam_id)
        self.payment_kind = payment_kind
        self.match_id = match_id
        self.is_gift_code = 1 if is_gift_code else 0

    def dict(self):
        return {
            'steam_id': str(self.steam_id),
            'match_id': str(self.match_id),
            'payment_kind': self.payment_kind,
            'is_gift_code': self.is_gift_code
        }


@db_session
def get_payment_information(
    payment_kind: str,
    currency: str
) -> Tuple[str, int]:
    def get_price(yuan: int, usd: int):
        return {
            'usd': usd,
            'cny': math.floor(
                yuan / float(settings.CURRENCY_CONVERSION_RATE) * 100
            )
        }.get(currency, None)

    price_entry = PriceList.get(payment_kind=payment_kind)
    if not price_entry:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail=f'No price entry for payment kind <{payment_kind}>'
        )

    amount = get_price(
        price_entry.price_cny,
        price_entry.price_usd
    )
    statement = price_entry.item_name

    if not amount or not statement:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail='Wrong currency'
        )

    return statement, amount


def get_source_options(metadata: PaymentMetaData):
    statement_descriptor, amount = get_payment_information(
        metadata.payment_kind,
        'cny'
    )
    metadata_dict = metadata.dict()
    metadata_dict['item_name'] = statement_descriptor
    return {
        'amount': amount,
        'currency': 'aud',
        'statement_descriptor': (
            f'Gift Code for {statement_descriptor}'
            if metadata.is_gift_code else statement_descriptor
        ),
        'redirect': {
            'return_url': f'{payment_url}payment/result',
        },
        'metadata': metadata_dict
    }


def create_alipay_request(metadata: PaymentMetaData) -> str:
    options = get_source_options(metadata)
    options['type'] = 'alipay'
    source = stripe.Source.create(
        **options
    )
    pprint(source)
    return source['redirect']['url']


def create_wechat_request(metadata: PaymentMetaData) -> str:
    options = get_source_options(metadata)
    options['type'] = 'wechat'
    source = stripe.Source.create(
        **options
    )
    return f"{payment_url}payment/wechat?qr={source['wechat']['qr_code_url']}"


def create_checkout_request(metadata: PaymentMetaData) -> str:
    statement_descriptor, amount = get_payment_information(
        metadata.payment_kind,
        'usd'
    )
    metadata_dict = metadata.dict()
    metadata_dict["item_name"] = statement_descriptor
    checkout_session = stripe.checkout.Session.create(
        success_url=(
            payment_url + 'payment/result?session_id={CHECKOUT_SESSION_ID}'
        ),
        cancel_url=payment_url + 'payment/result',
        payment_method_types=['card'],
        mode='payment',
        line_items=[
            {
                'name': (
                    f"Gift Code for {statement_descriptor}"
                    if metadata.is_gift_code else statement_descriptor
                ),
                'quantity': 1,
                'currency': 'usd',
                'amount': amount
            },
        ],
        metadata=metadata_dict
    )
    return f"{payment_url}payment/checkout?id={checkout_session['id']}"


method_switch = {
    'alipay': create_alipay_request,
    'wechat': create_wechat_request,
    'checkout': create_checkout_request
}


def create_payment_request(
    method: str,
    metadata: PaymentMetaData
) -> str:
    return method_switch[method](metadata)


def process_gift_code_purchase(
    steam_id: str,
    payment_kind: str,
    item_name: str,
    item_count: int
):
    hash_factory = md5()
    hash_factory.update(
        bytearray(
            steam_id + payment_kind + item_name + str(
                datetime.utcnow().timestamp()
            ),
            'utf-8'
        )
    )
    code = hash_factory.hexdigest()

    GiftCodes(
        steam_id=steam_id,
        code=code,
        payment_kind=payment_kind,
        item_name=item_name,
        item_count=item_count
    )

    return {
        "purchased_code": code
    }


def process_booster_purchase(
    player: Player,
    payment_kind: str,
    steam_id: str
) -> dict:
    current_date = datetime.utcnow()
    purchased_supporter_state = {
        'base_booster': 1,
        'golden_booster': 2,
    }[payment_kind]
    logger.info(
        f'Player <{steam_id}> purchased supporter {payment_kind}, '
        f'current supporter state: {player.supporter_state}, '
        f'purchased: {purchased_supporter_state}'
    )

    # upgrading supporter level doesn't add up duration
    if player.supporter_state == 0:
        logger.info(
            f'Player <{steam_id}> upgraded supporter level '
            f'from: {player.supporter_state} to {purchased_supporter_state}'
        )
        player.supporter_enddate = current_date + timedelta(days=30)
        player.supporter_state = purchased_supporter_state

    elif purchased_supporter_state > player.supporter_state:
        prices = PriceList.select(
            lambda price: price.payment_kind == 'base_booster' or
            price.payment_kind == 'golden_booster'
        )
        booster_prices = {}
        for price in prices:
            price = price.to_dict()
            booster_prices[price['payment_kind']] = price['price_usd']
        logger.info(f'Prices: {booster_prices}')
        supporter_duration = player.supporter_enddate - current_date
        converted_days = math.floor(
            supporter_duration.days / (
                booster_prices['golden_booster'] /
                booster_prices['base_booster']
            )
        )
        logger.info(f'Player <{steam_id}> has ongoing booster for '
                    f'{supporter_duration.days}, '
                    f'converted to {converted_days}')
        player.supporter_enddate = current_date + timedelta(
            days=30 + converted_days
        )
        player.supporter_state = purchased_supporter_state

    elif player.supporter_state == purchased_supporter_state:
        logger.info(f'Player <{steam_id}> increased duration of his supporter '
                    f'{player.supporter_state} / {purchased_supporter_state}')
        player.supporter_enddate += timedelta(days=30)

    player.battlepass_glory += (
        CONST_SUPPORTER_GLORY_REWARD[player.supporter_state]
    )
    player.battlepass_fortune += (
        CONST_SUPPORTER_FORTUNE_REWARD[player.supporter_state]
    )
    add_battle_pass_exp(
        CONST_SUPPORTER_EXP_REWARD[player.supporter_state],
        player
    )

    return {
        "supporter_state": {
            "level": player.supporter_state,
            "enddate": str(player.supporter_enddate)
        },
        "glory": player.battlepass_glory,
        "fortune": player.battlepass_fortune,
        "level": player.battlepass_level,
        "exp": player.battlepass_exp,
        "exp_required": get_bp_required_exp(player.battlepass_level)
    }


def process_glory_purchase(
    player: Player,
    payment_kind: str,
    steam_id: str,
    item_name: str
) -> dict:
    glory_amount = payment_kind.split('_')
    glory_amount = int(glory_amount[-1]) if (
        len(glory_amount) >= 1 and glory_amount[-1].isdigit()
    ) else 550
    logger.info(f'User <{steam_id}> purchased glory {item_name}, '
                f'exact value: {glory_amount}')
    player.battlepass_glory += glory_amount
    # TODO: rework this bullshit into something appropriate,
    #  json in price list or whatever
    player.battlepass_fortune += {
        100: 2,
        550: 12,
        1150: 25,
        3000: 70,
        6500: 150,
        15000: 330,
    }[glory_amount]

    return {
        'glory': player.battlepass_glory,
        'fortune': player.battlepass_fortune,
    }


def process_item_purchase(
    steam_id: str,
    item_name: str,
    payment_kind: str,
    item_count: int
) -> dict:
    logger.info(f'User <{steam_id}> purchased item {item_name}')
    in_game_item_name = payment_kind.replace('purchase_', '')
    purchased_item = PlayerInventory.get(
        item_name=in_game_item_name, SteamId=steam_id
    )
    if purchased_item:
        purchased_item.count += item_count
    else:
        purchased_item = PlayerInventory(
            steam_id=steam_id,
            item_name=in_game_item_name,
            count=item_count
        )
    return {
        'purchased_item': keys_lower(steam_id_to_str(purchased_item.to_dict()))
    }


def process_purchase(
    player: Player,
    item_count: int,
    steam_id: str,
    payment_kind: str,
    item_name: str,
    is_gift_code: bool = False
) -> dict:
    if is_gift_code:
        return process_gift_code_purchase(
            steam_id,
            payment_kind,
            item_name,
            item_count
        )

    if "booster" in payment_kind:
        return process_booster_purchase(
            player,
            payment_kind,
            steam_id
        )
    elif "glory_bundle" in payment_kind:
        return process_glory_purchase(
            player,
            payment_kind,
            steam_id,
            item_name
        )
    else:
        return process_item_purchase(
            steam_id,
            item_name,
            payment_kind,
            item_count
        )


@db_session
def _finish_payment(event: stripe.Event):
    metadata = event['data']['object']['metadata']
    steam_id = metadata['steam_id']
    match_id = metadata['match_id']
    payment_kind = metadata['payment_kind']
    item_name = metadata['item_name']
    item_count = metadata.get('count', 1)
    is_gift_code = bool(int(metadata.get('is_gift_code', 0)))
    pprint(metadata)

    player = Player.get(steam_id=steam_id)

    event_body = process_purchase(
        player,
        item_count,
        steam_id,
        payment_kind,
        item_name,
        is_gift_code
    )
    event_body["kind"] = "paymentUpdate"
    event_body["steam_id"] = str(steam_id)

    MatchEvent(
        match_id=match_id,
        body=keys_lower(event_body),
    )

    try:
        ItemSellingHistory(
            steam_id=steam_id,
            item_name=item_name,
            item_count=metadata.get("count", 1),
            sold_at=datetime.utcnow().date(),
            real_cost=(
                event['data']['object'].get("amount_total", None) or
                event['data']['object'].get("amount", 0)
            )
        )
    except Exception:
        logger.warning('Item Sell history recording failed!')
    logger.info(f'User <{steam_id}> finished payment')


def finish_payment(event: stripe.Event, tasks: BackgroundTasks):
    tasks.add_task(_finish_payment, event)


def charge_payment(event: stripe.Event, tasks: BackgroundTasks):
    logger.info('Charge payment initialized:')
    pprint(event)
    source = event['data']['object']
    charge = stripe.Charge.create(
        amount=source['amount'],
        currency=source['currency'],
        source=source['id'],
    )
    logger.info('Charge created')
    if charge['status'] != 'succeeded':
        logger.info(f"Charge status is not succeeded: {charge['status']}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Charge {charge['id']} of source {event} " +
                f"has invalid initial status {charge['status']}"
            )
        )
    finish_payment(event, tasks)
