import asyncio
import json
import os
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config import BOT_TOKEN, ADMIN_IDS
from database.db import init_db, add_admin
from handlers.start import router as start_router
from handlers.search import router as search_router
from handlers.admin import router as admin_router
from handlers.back import router as back_router
from handlers.reviews import router as reviews_router


class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path in ("/", "/health"):
            payload = json.dumps({"status": "ok", "service": "ovoza"}).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
            return
        self.send_response(404)
        self.end_headers()

    def log_message(self, format, *args):
        return


def start_health_server():
    port = int(os.getenv("PORT", "10000"))
    server = ThreadingHTTPServer(("0.0.0.0", port), HealthHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    print(f"[health] listening on 0.0.0.0:{port}")
    return server


async def main():
    start_health_server()
    await init_db()
    for admin_id in ADMIN_IDS:
        await add_admin(admin_id)

    bot = Bot(BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()
    dp.include_router(start_router)
    dp.include_router(search_router)
    dp.include_router(admin_router)
    dp.include_router(back_router)
    dp.include_router(reviews_router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
