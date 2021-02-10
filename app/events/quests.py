from pony.orm import db_session

from ..libs.logging import logger
from ..core.models.db import db


def process_daily_quests():
    # this is probably very expensive, too bad!
    with db_session:
        logger.info("Started resetting daily quests")
        db.execute("select replace_player_quests();")
        logger.info("Finished resetting daily quests")


# def clean_old_match_data():
#     with db_session:
#         res = db.execute("""
#             delete
#                 from "MatchPlayer" mp using "Match" m
#                 where
#                     m."match_id" = mp."match_id" and
#                     m."ended_at" <= current_date - 21;
#             delete
#                 from "MatchTeam" mt using "Match" m
#                 where
#                     m."match_id" = mt."match_id" and
#                     m."ended_at" <= current_date - 21;
#             delete
#                 from "Match" m
#                 where m."ended_at" <= current_date - 21;
#         """.strip())
#     print('asdfaasddsafdfasdfa')
#     logger.info(f"Deletion info: {res}")
