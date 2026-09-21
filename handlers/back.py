from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from database.db import get_user_lang
from keyboards.main import main_kb
from keyboards.search import filter_kb
from services.admin import is_admin
from services.i18n import t

router=Router()
@router.callback_query(F.data=="back:main")
async def back_main(call,state):
    await state.clear(); lang=await get_user_lang(call.from_user.id)
    await call.message.edit_text(t(lang,"main"),reply_markup=main_kb(lang,await is_admin(call.from_user.id))); await call.answer()
@router.callback_query(F.data=="noop")
async def noop(call): await call.answer()
