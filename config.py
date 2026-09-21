"""Ovoza bot configuration.

Local development keeps the original config.py workflow. On Render,
BOT_TOKEN, ADMIN_IDS, and DATABASE_URL are supplied as environment variables.
"""

import os

# Local defaults (never put a real bot token into GitHub).
BOT_TOKEN = os.getenv("BOT_TOKEN", "PASTE_YOUR_BOT_TOKEN_HERE")

_default_admin_ids = {123456789}
_admin_ids_env = os.getenv("ADMIN_IDS", "").strip()
if _admin_ids_env:
    ADMIN_IDS = {int(x.strip()) for x in _admin_ids_env.split(",") if x.strip()}
else:
    ADMIN_IDS = _default_admin_ids

DB_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///ovoza.db")

if not BOT_TOKEN or BOT_TOKEN == "PASTE_YOUR_BOT_TOKEN_HERE":
    raise RuntimeError(
        "BOT_TOKEN sozlanmagan. Local ishlatishda config.py ni sozlang, "
        "Renderda esa BOT_TOKEN environment variable kiriting."
    )

if not ADMIN_IDS:
    raise RuntimeError(
        "ADMIN_IDS sozlanmagan. Kamida bitta Telegram ID kiriting."
    )
