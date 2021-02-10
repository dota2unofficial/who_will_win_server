from pony.orm import db_session

from ..libs.logging import logger
from ..core.models.db import db


def process_exp_limits():
    with db_session:
        db.execute("""
            begin work;
            lock table "Player";
            update "Player"
                set "battlepass_daily_exp"=0, "battlepass_daily_fortune"=0;
                commit work;
        """.strip())
        logger.info("Finished resetting exp limits!")
