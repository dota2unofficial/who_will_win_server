from jinja2 import Markup

from ....core.settings import settings

domain_url = settings.PAYMENT_RETURN_URL


def steamid_linkify(text, argument=None):
    return Markup(
        f'<a href="https://steamcommunity.com/profiles/{text}" ' +
        'target="_blank" rel="noreferrer noopener">' +
        f'{argument if argument else text}</a>'
    )


def player_profile(text):
    return Markup(
        f'<a href="{domain_url}admin/players/{text}" ' +
        f'target="_blank" rel="noreferrer noopener">{text}</a>'
    )


def item_sell_linkify(text):
    return Markup(
        f'<a href="{domain_url}admin/sells/{text}" ' +
        f'target="_blank" rel="noreferrer noopener">{text}</a>'
    )


def item_stats_linkify(text):
    return Markup(
        f'<a href="{domain_url}admin/item/{text}" ' +
        f'target="_blank" rel="noreferrer noopener">{text}</a>'
    )


def ability_stats_linkify(text):
    return Markup(
        f'<a href="{domain_url}admin/ability/{text}" ' +
        f'target="_blank" rel="noreferrer noopener">{text}</a>'
    )
