from fastapi import APIRouter, Request, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from pony.orm import db_session, desc

from ....core.models.db import db
from ....core.models.timer import TimerPerformance
from .templates import templates

router = APIRouter()


@router.get('/timers', response_class=HTMLResponse)
async def get_script_error_page(request: Request):
    with db_session:
        timers = list(
            TimerPerformance.select().order_by(
                desc(TimerPerformance.average_time)
            )
        )
    return templates.TemplateResponse(
        'timers/timers.html',
        {
            'title': 'Timers Performance',
            'request': request,
            'timers': timers
        }
    )


@router.get('/timers-clear')
async def clear_script_errors():
    with db_session:
        db.execute('truncate "TimerPerformance" restart identity')
    return RedirectResponse(url='/admin/timers')


@router.post('/reset_exp_limit')
async def reset_daily_exp():
    with db_session:
        db.execute("""
            begin work;
            lock table "Player";
            update "Player"
            set "battlepass_daily_exp"=0, "battlepass_daily_fortune"=0;
            commit work;
        """.strip())
    return Response(status_code=200)
