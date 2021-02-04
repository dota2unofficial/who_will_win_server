from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from pony.orm import db_session, select, count

from .templates import templates
from ....core.models.db import db
from ....core.models.matchs import ScriptError

router = APIRouter()


@router.get('/script-errors', response_class=HTMLResponse)
async def get_script_error_page(request: Request):
    with db_session:
        errors = select(
            (
                err.stack, count(err.match_id), sum(err.count)
            ) for err in ScriptError
        ).order_by(-3)
        return templates.TemplateResponse(
            'errors/script_errors.html',
            {
                'title': 'Script Errors',
                'request': request,
                'errors': list(errors)
            }
        )


@router.get('/script-errors-clear')
async def clear_script_errors(request: Request):
    with db_session:
        # delete(err for err in ScriptError)
        db.execute('truncate "ScriptError" restart identity')
    return RedirectResponse(url='/admin/script-errors')
