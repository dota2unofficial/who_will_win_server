from pony.orm import db_session, OperationalError

from ..core.models.db import db
from ..libs.logging import logger


def ping_db():
    with db_session:
        logger.info("Pinging database...")
        try:
            res = db.execute('select id from "DedicatedKeys" limit 1')
        except OperationalError:
            res = "ERROR"
            logger.info(f"Database ping status: {res}")


def clean_old_match_data():
    with db_session:
        res = db.execute("""
            delete
                from "MatchPlayer" mp using "Match" m
                where
                    m."match_id" = mp."match_id" and
                    m."ended_at" <= current_date - 21;
            delete
                from "MatchTeam" mt using "Match" m
                where m."match_id" = mt."match_id" and
                m."ended_at" <= current_date - 21;
            delete
                from "Match" m
                where m."ended_at" <= current_date - 21;
        """.strip())
    logger.info(f"Deletion info: {res}")
