from apscheduler.schedulers.blocking import BlockingScheduler

from .libs.logging import logger
from .core.settings import settings
from .events.quests import process_daily_quests
from .events.patchnotes import process_patch_notes
from .events.exp_limits import process_exp_limits
from .events.misc_events import ping_db, clean_old_match_data


def tasks():
    logger.info('[scheduler] Init started')
    print('[scheduler] Init started')
    scheduler = BlockingScheduler()

    logger.info('[scheduler-database] Database init started')
    print('[scheduler-database] Database init started')
    settings.db_connect()
    logger.info('[scheduler-database] Database init completed')
    print('[scheduler-database] Database init completed')

    scheduler.add_job(
        process_daily_quests,
        'cron',
        hour=0,
        minute=0
    )  # hour=0, minute=0  # each day at 0:00
    scheduler.add_job(
        process_patch_notes,
        'cron',
        minute="*/10"
    )  # each 10 minutes
    scheduler.add_job(
        process_exp_limits,
        'cron',
        hour=0,
        minute=0
    )
    scheduler.add_job(
        ping_db,
        'cron',
        second='*/30'
    )
    scheduler.add_job(
        clean_old_match_data,
        'cron',
        hour=0,
        minute=0
    )

    logger.info('[scheduler] Init finished')
    print('[scheduler] Init finished')
    scheduler.start()
    logger.warning('[scheduler] Finished')
    print('[scheduler] Finished')
