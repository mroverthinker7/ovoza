from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from database.db import upsert_user
from keyboards.language import language_kb
from keyboards.main import main_kb
from services.i18n import t
from services.admin import is_admin

router=Router()

@router.message(CommandStart())
async def start(message: Message):
    await message.answer("🌐 Tilni tanlang / Выберите язык:", reply_markup=language_kb())

@router.callback_query(F.data.startswith("lang:"))
async def set_language(call: CallbackQuery):
    lang=call.data.split(":",1)[1]
    await upsert_user(call.from_user.id,lang)
    admin=await is_admin(call.from_user.id)
    await call.message.edit_text(t(lang,"main"),reply_markup=main_kb(lang,admin))
    await call.answer()
