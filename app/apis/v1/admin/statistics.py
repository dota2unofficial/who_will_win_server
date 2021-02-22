from datetime import datetime, timedelta, date

from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
from pony.orm import db_session, select, avg, desc, count

from ....libs.constants import CONST_RATING_CHANGES, CONST_STAT_TYPES
from ....libs.logging import logger
from ....libs.queries import (
    abilities_average_round,
    most_picked_abilities,
    items_average_round,
    most_purchased_items,
    innates_average_round,
    most_picked_innates,
    hardest_round_death_element,
    quests_progress,
    achievements_progress,
    dated_leaderboard,
    masteries_average_round,
    ability_per_day_pickrate,
    item_per_day_pickrate
)
from .templates import templates
from ....core.models.db import db
from ....core.models.players import Player
from ....core.models.matchs import Match
from ....core.models.payments import ItemSellingHistory

router = APIRouter()


class Statistics:
    @staticmethod
    async def get_abilities_page(
        request: Request,
        map_name: str,
        selected_type: str
    ):
        from_date = datetime.utcnow() - timedelta(days=7)
        map_names = list(CONST_RATING_CHANGES.keys())
        logger.info(f'Get abilities page: {map_name}')
        with db_session:
            data = {
                'ability_average_round': db.select(abilities_average_round),
                'ability_usage': db.select(most_picked_abilities),
                'match_count': Match.select(
                    lambda m: m.map_name == map_name and
                    m.ended_at >= from_date
                ).count(),
            }
        return templates.TemplateResponse(
            'statistics/abilities.html',
            {
                'title': 'Abilities Stats',
                'request': request,
                'map_names': map_names,
                'selected_map': map_name,
                'from_date': str(from_date),
                'stat_types': CONST_STAT_TYPES,
                'selected_type': selected_type,
                **data
            }
        )

    @staticmethod
    async def get_item_page(
        request: Request,
        map_name: str,
        selected_type: str
    ):
        from_date = datetime.utcnow() - timedelta(days=7)
        map_names = list(CONST_RATING_CHANGES.keys())
        with db_session:
            data = {
                'item_average_round': db.select(items_average_round),
                'item_usage': db.select(most_purchased_items),
                'match_count': Match.select(
                    lambda m: m.map_name == map_name and
                    m.ended_at >= from_date
                ).count(),
            }
        return templates.TemplateResponse(
            'statistics/items.html',
            {
                'title': 'Items Stats',
                'request': request,
                'map_names': map_names,
                'selected_map': map_name,
                'from_date': str(from_date),
                'stat_types': CONST_STAT_TYPES,
                'selected_type': selected_type,
                **data
            }
        )

    @staticmethod
    async def get_battle_pass_page(
        request: Request,
        map_name: str,
        selected_type: str
    ):
        from_date = datetime.utcnow() - timedelta(days=7)
        map_names = list(CONST_RATING_CHANGES.keys())
        with db_session:
            data = {
                'quests': db.select(quests_progress),
                'achievements': db.select(achievements_progress),
                'avg_level': list(
                    select(
                        avg(
                            p.battlepass_level
                        ) for p in Player if p.steam_id != 0
                    )
                )[0],
                'avg_glory': list(
                    select(
                        avg(
                            p.battlepass_glory
                        ) for p in Player if p.steam_id != 0
                    )
                )[0],
                'top_level': list(
                    select(
                        (
                            p.steam_id,
                            p.battlepass_level
                        ) for p in Player if p.steam_id != 0
                    ).order_by(desc(2)).limit(20)
                ),
                'top_glory': list(
                    select(
                        (
                            p.steam_id,
                            p.battlepass_glory
                        ) for p in Player if p.steam_id != 0
                    ).order_by(desc(2)).limit(20)
                )
            }
        return templates.TemplateResponse(
            'statistics/battlepass.html',
            {
                'title': 'Battle Pass Stats',
                'request': request,
                'map_names': map_names,
                'selected_map': map_name,
                'from_date': str(from_date),
                'stat_types': CONST_STAT_TYPES,
                'selected_type': selected_type,
                **data
            }
        )

    @staticmethod
    async def get_innates_page(
        request: Request,
        map_name: str,
        selected_type: str
    ):
        from_date = datetime.utcnow() - timedelta(days=7)
        map_names = list(CONST_RATING_CHANGES.keys())
        with db_session:
            data = {
                'innate_average_round': db.select(innates_average_round),
                'innate_usage': db.select(most_picked_innates)
            }
        return templates.TemplateResponse(
            'statistics/innates.html',
            {
                'title': 'Innates Stats',
                'request': request,
                'map_names': map_names,
                'selected_map': map_name,
                'from_date': str(from_date),
                'stat_types': CONST_STAT_TYPES,
                'selected_type': selected_type,
                **data
            }
        )

    @staticmethod
    async def get_rounds_page(
        request: Request,
        map_name: str,
        selected_type: str
    ):
        from_date = datetime.utcnow() - timedelta(days=7)
        map_names = list(CONST_RATING_CHANGES.keys())
        with db_session:
            # rd_field here is used as context variable for db query,
            #  used by Pony ORM
            data = {}
            rd_field = 'name'
            data['hardest_round'] = db.select(hardest_round_death_element)
            rd_field = 'totem'
            data['hardest_totem'] = db.select(hardest_round_death_element)
        return templates.TemplateResponse(
            'statistics/rounds.html',
            {
                'title': 'Rounds Stats',
                'request': request,
                'map_names': map_names,
                'selected_map': map_name,
                'from_date': str(from_date),
                'stat_types': CONST_STAT_TYPES,
                'selected_type': selected_type,
                **data
            }
        )

    @staticmethod
    async def get_leaderboard_page(
        request: Request,
        map_name: str,
        selected_type: str
    ):
        page = request.query_params.get('page', 0)
        if page == '':
            page = 0
        leaderboard_day = request.query_params.get('leaderboard_day', None)
        leaderboard_month = request.query_params.get('leaderboard_month', None)
        leaderboard_year = request.query_params.get('leaderboard_year', None)

        if leaderboard_day:
            from_date = date(
                int(leaderboard_year),
                int(leaderboard_month),
                int(leaderboard_day)
            )
        else:
            from_date = datetime.utcnow().date()
        map_names = list(CONST_RATING_CHANGES.keys())
        with db_session:
            logger.info(
                f'Fetched leaderboard page {page} from date {str(from_date)}'
            )
            data = {
                'leaderboard': db.select(dated_leaderboard)
            }
        return templates.TemplateResponse(
            'statistics/leaderboards.html',
            {
                'title': f'Leaderboards of {map_name}',
                'request': request,
                'map_names': map_names,
                'selected_map': map_name,
                'from_date': from_date,
                'page': page,
                'stat_types': CONST_STAT_TYPES,
                'selected_type': selected_type,
                **data
            }
        )

    @staticmethod
    async def get_sells_page(
        request: Request,
        map_name: str,
        selected_type: str
    ):
        map_names = list(CONST_RATING_CHANGES.keys())
        from_date = datetime.utcnow()

        with db_session:
            data = {
                'glory_item_sells_top': list(
                    select(
                        (
                            item.item_name,
                            sum(item.item_count),
                            sum(item.glory_cost)
                        ) for (
                            item
                        ) in ItemSellingHistory if item.glory_cost is not None
                    ).order_by(-2, -3)
                ),
                'real_item_sells_top': list(
                    select(
                        (
                            item.item_name,
                            sum(item.item_count),
                            sum(item.real_cost)
                        ) for (
                            item
                        ) in ItemSellingHistory if item.real_cost is not None
                    ).order_by(-2, -3)
                ),
                'purchase_count': ItemSellingHistory.select().count()
            }

        return templates.TemplateResponse(
            'statistics/sells_history.html',
            {
                'title': f'Selling Statistics {map_name}',
                'request': request,
                'map_names': map_names,
                'selected_map': map_name,
                'from_date': from_date,
                'stat_types': CONST_STAT_TYPES,
                'selected_type': selected_type,
                **data
            }
        )

    @staticmethod
    async def get_match_count_page(
        request: Request,
        map_name: str,
        selected_type: str
    ):
        map_names = list(CONST_RATING_CHANGES.keys())
        from_date = datetime.utcnow()

        with db_session:
            res = db.select("""
                SELECT
                    m."ended_at"::date,
                    count(m."ended_at"::date)
                FROM "Match" m
                WHERE m."map_name" = $map_name
                GROUP BY m."ended_at"::date
                ORDER BY m."ended_at"::date;
            """.strip())
            data = {
                'match_counts_repr': [val[1] for val in res],
                'dates_repr': [val[0].strftime('%d.%m.%Y') for val in res],
            }

        return templates.TemplateResponse(
            'statistics/match_count.html',
            {
                'title': 'Match Count Stats',
                'request': request,
                'map_names': map_names,
                'selected_map': map_name,
                'from_date': from_date,
                'stat_types': CONST_STAT_TYPES,
                'selected_type': selected_type,
                **data
            }
        )

    @staticmethod
    async def get_masteries_page(
        request: Request,
        map_name: str,
        selected_type: str
    ):
        map_names = list(CONST_RATING_CHANGES.keys())
        from_date = datetime.utcnow() - timedelta(days=7)

        with db_session:
            data = {
                'masteries_average_round': db.select(masteries_average_round)
            }

        return templates.TemplateResponse(
            'statistics/masteries.html',
            {
                'title': 'Masteries Stats',
                'request': request,
                'map_names': map_names,
                'selected_map': map_name,
                'from_date': from_date,
                'stat_types': CONST_STAT_TYPES,
                'selected_type': selected_type,
                **data
            }
        )


@router.get('/statistics')
async def get_statistics_redirect(
    map_name: str = 'ffa',
    stats_type: str = 'abilities'
):
    return RedirectResponse(
        f'/admin/statistics/{map_name}/{stats_type}',
        status_code=308
    )


@router.get('/statistics/{map_name}/{stats_type}')
async def get_statistics_by_stats_page(
    request: Request,
    map_name: str,
    stats_type: str
):
    callback = {
        'abilities': Statistics.get_abilities_page,
        'items': Statistics.get_item_page,
        'battlepass': Statistics.get_battle_pass_page,
        'innates': Statistics.get_innates_page,
        'rounds': Statistics.get_rounds_page,
        'leaderboard': Statistics.get_leaderboard_page,
        'sells': Statistics.get_sells_page,
        'match_count': Statistics.get_match_count_page,
        'masteries': Statistics.get_masteries_page
    }[stats_type](request, map_name, stats_type)
    return await callback


@router.get('/statistics/{map_name}')
async def get_statistics_by_map_page(request: Request, map_name: str):
    with db_session:
        from_date = datetime.utcnow() - timedelta(days=7)
        map_names = list(CONST_RATING_CHANGES.keys())
        data = {}
        data['ability_average_round'] = db.select(abilities_average_round)
        data['ability_usage'] = db.select(most_picked_abilities)
        data['item_average_round'] = db.select(items_average_round)
        data['item_usage'] = db.select(most_purchased_items)
        data['innate_average_round'] = db.select(innates_average_round)
        data['innate_usage'] = db.select(most_picked_innates)
        # rd_field is used as a context variable in next raw queries
        #  and is substituted by PonyORM
        rd_field = 'name'
        data['hardest_round'] = db.select(hardest_round_death_element)
        rd_field = 'totem'
        data['hardest_totem'] = db.select(hardest_round_death_element)

        data['quests'] = db.select(quests_progress)
        data['achievements'] = db.select(achievements_progress)

        data['avg_level'] = list(
            select(avg(p.battlepass_level) for p in Player if p.steam_id != 0)
        )[0]
        data['avg_glory'] = list(
            select(avg(p.battlepass_glory) for p in Player if p.steam_id != 0)
        )[0]
        data['top_level'] = list(
            select(
                (
                    p.steam_id, p.battlepass_level
                ) for p in Player if p.steam_id != 0
            ).order_by(desc(2)).limit(20))
        data['top_glory'] = list(
            select(
                (
                    p.steam_id, p.battlepass_glory
                ) for p in Player if p.steam_id != 0
            ).order_by(desc(2)).limit(20))

    return templates.TemplateResponse(
        'statistics/statistics.html',
        {
            'title': 'Statistics',
            'request': request,
            'map_names': map_names,
            'selected_map': map_name,
            'from_date': str(from_date),
            **data
        }
    )


@router.get('/ability/{ability_name}')
async def get_ability_stats(request: Request, ability_name: str):
    with db_session:
        res = db.select(ability_per_day_pickrate)
        data = {
            'avg_rounds': [float(val[2]) for val in res],
            'pick_rates_repr': [val[1] for val in res],
            'dates_repr': [val[0].strftime('%d.%m.%Y') for val in res],
        }
    return templates.TemplateResponse(
        'statistics/entity_pickrate.html',
        {
            '': f'{ability_name}',
            'request': request,
            **data
        }
    )


@router.get('/item/{item_name}')
async def get_item_stats(request: Request, item_name: str):
    with db_session:
        res = db.select(item_per_day_pickrate)
        data = {
            'avg_rounds': [float(val[2]) for val in res],
            'pick_rates_repr': [val[1] for val in res],
            'dates_repr': [val[0].strftime('%d.%m.%Y') for val in res],
        }
    return templates.TemplateResponse(
        'statistics/entity_pickrate.html',
        {
            'title': f'{item_name}',
            'request': request,
            **data
        }
    )


@router.get('/sells/{item_name}')
async def get_item_sells(request: Request, item_name: str):
    with db_session:
        data = {
            'purchased_times':
                ItemSellingHistory.select(
                    lambda item: item.item_name == item_name
                ).count(),
            'purchased_total_count':
                list(
                    select(
                        sum(item.item_count) for item in (
                            ItemSellingHistory
                        ) if item.item_name == item_name
                    )
                )[0],
            'item_purchases':
                list(
                    select(item for item in (
                        ItemSellingHistory
                    ) if item.item_name == item_name).order_by(
                        desc(ItemSellingHistory.sold_at)).limit(100)
                    ),
            'item_purchases_per_date':
                list(
                    select(
                        (item.sold_at, count(item.id)) for item in (
                            ItemSellingHistory
                        ) if item.item_name == item_name
                    )
                ),
        }
    return templates.TemplateResponse(
        'statistics/item_sells.html',
        {
            'title': f'{item_name} Sells in Custom Hero Clash',
            'request': request,
            'item_name': item_name,
            **data
        }
    )
