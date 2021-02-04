from fastapi.templating import Jinja2Templates

from .filters import (
    steamid_linkify,
    item_sell_linkify,
    player_profile,
    item_stats_linkify,
    ability_stats_linkify
)

templates = Jinja2Templates(
    directory="app/templates"
)
templates.env.filters['steamid_linkify'] = steamid_linkify
templates.env.filters['item_sell_linkify'] = item_sell_linkify
templates.env.filters['player_profile_linkify'] = player_profile
templates.env.filters['item_stats_linkify'] = item_stats_linkify
templates.env.filters['ability_stats_linkify'] = ability_stats_linkify
