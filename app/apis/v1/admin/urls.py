from fastapi import APIRouter

from .prices import router as price_router
from .quests import router as quest_router
from .management import router as management_router
from .achievements import router as achievement_router
from .payments import router as payment_router
from .keys import router as dedicated_keys_router
from .supporters import router as supporter_router
from .players import router as player_management_router
from .statistics import router as statistic_router
from .timers import router as timer_router
from .errors import router as err_router

router = APIRouter()

router.include_router(price_router)
router.include_router(quest_router)
router.include_router(management_router)
router.include_router(achievement_router)
router.include_router(payment_router)
router.include_router(dedicated_keys_router)
router.include_router(supporter_router)
router.include_router(player_management_router)
router.include_router(statistic_router)
router.include_router(timer_router)
router.include_router(err_router)
