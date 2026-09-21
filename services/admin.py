from config import ADMIN_IDS
from database.db import is_db_admin

async def is_admin(tg_id: int) -> bool:
    return tg_id in ADMIN_IDS or await is_db_admin(tg_id)
