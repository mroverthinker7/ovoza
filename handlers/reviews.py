from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from database.db import create_review, get_user_lang, Session
from database.models import Request
from keyboards.reviews import rating_kb, review_comment_kb
from services.i18n import t

router = Router()

class ReviewFlow(StatesGroup):
    comment = State()

@router.callback_query(F.data.startswith("review:rate:"))
async def choose_rating(call: CallbackQuery, state: FSMContext):
    parts = call.data.split(":")
    request_id = int(parts[2])
    rating = int(parts[3])
    lang = await get_user_lang(call.from_user.id)
    async with Session() as s:
        req = await s.get(Request, request_id)
        if not req or req.user_id is None:
            await call.answer(t(lang, "review_unavailable"), show_alert=True)
            return
        # Verify the request belongs to the Telegram user.
        from database.models import User
        user = await s.get(User, req.user_id)
        if not user or user.telegram_id != call.from_user.id or req.status != "completed":
            await call.answer(t(lang, "review_unavailable"), show_alert=True)
            return
    await state.update_data(review_request_id=request_id, review_rating=rating)
    await state.set_state(ReviewFlow.comment)
    await call.message.edit_text(t(lang, "review_comment_prompt", rating=rating), reply_markup=review_comment_kb(lang, request_id))
    await call.answer()

@router.message(ReviewFlow.comment)
async def review_comment(message: Message, state: FSMContext):
    lang = await get_user_lang(message.from_user.id)
    data = await state.get_data()
    request_id = data.get("review_request_id")
    rating = data.get("review_rating")
    if not request_id or not rating:
        await state.clear()
        await message.answer(t(lang, "review_unavailable"))
        return
    comment = (message.text or "").strip() or None
    review = await create_review(int(request_id), int(rating), comment)
    await state.clear()
    if not review:
        await message.answer(t(lang, "review_already"))
        return
    await message.answer(t(lang, "review_saved"))

@router.callback_query(F.data.startswith("review:skip:"))
async def review_skip(call: CallbackQuery, state: FSMContext):
    request_id = int(call.data.split(":")[-1])
    lang = await get_user_lang(call.from_user.id)
    data = await state.get_data()
    rating = data.get("review_rating")
    if not rating or data.get("review_request_id") != request_id:
        await call.answer(t(lang, "review_unavailable"), show_alert=True)
        return
    review = await create_review(request_id, int(rating), None)
    await state.clear()
    if not review:
        await call.answer(t(lang, "review_already"), show_alert=True)
        return
    await call.message.edit_text(t(lang, "review_saved"))
    await call.answer()
