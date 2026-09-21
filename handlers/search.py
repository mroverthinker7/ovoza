from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from database.db import get_user_lang
from keyboards.search import filter_kb, service_kb, region_kb, district_kb, price_kb, rating_kb, results_kb
from services.i18n import t
from services.search import find_groups

router=Router()

async def show_filters(call: CallbackQuery, state: FSMContext):
    lang = await get_user_lang(call.from_user.id)
    data = await state.get_data()
    filters = data.get("search_filters", {})
    await call.message.edit_text(
        t(lang, "filters"),
        reply_markup=filter_kb(lang, filters),
    )
    await call.answer()

@router.callback_query(F.data=="search:open")
async def open_search(call: CallbackQuery, state: FSMContext):
    # Open the filter screen without destroying filters already selected.
    data = await state.get_data()
    if "search_filters" not in data:
        await state.update_data(search_filters={})
    await show_filters(call, state)

@router.callback_query(F.data=="search:reset")
async def reset(call: CallbackQuery, state: FSMContext):
    await state.update_data(search_filters={})
    await show_filters(call, state)


@router.callback_query(F.data == "filter:back")
async def filter_back(call: CallbackQuery, state: FSMContext):
    await show_filters(call, state)

@router.callback_query(F.data=="filter:service")
async def service(call: CallbackQuery):
    lang = await get_user_lang(call.from_user.id)
    await call.message.edit_text(t(lang, "select_service"), reply_markup=service_kb(lang))
    await call.answer()
@router.callback_query(F.data=="filter:region")
async def region(call: CallbackQuery):
    lang = await get_user_lang(call.from_user.id)
    await call.message.edit_text(t(lang, "select_region"), reply_markup=region_kb(lang))
    await call.answer()

@router.callback_query(F.data=="setregion:toshkent")
async def choose_city(call: CallbackQuery):
    lang = await get_user_lang(call.from_user.id)
    await call.message.edit_text(t(lang, "select_district"), reply_markup=district_kb(lang))
    await call.answer()

@router.callback_query(F.data.startswith("setdistrict:"))
async def setdistrict(call: CallbackQuery, state: FSMContext):
    from services.catalog import DISTRICT_MAP
    key = call.data.split(":", 1)[1]
    district = DISTRICT_MAP.get(key)
    if not district:
        await call.answer("❌", show_alert=True)
        return
    await set_filter(call, state, "region", district[0])
@router.callback_query(F.data=="filter:price")
async def price(call: CallbackQuery):
    lang = await get_user_lang(call.from_user.id)
    await call.message.edit_text(t(lang, "select_price"), reply_markup=price_kb(lang))
    await call.answer()
@router.callback_query(F.data=="filter:rating")
async def rating(call: CallbackQuery):
    lang = await get_user_lang(call.from_user.id)
    await call.message.edit_text(t(lang, "select_rating"), reply_markup=rating_kb(lang))
    await call.answer()

async def set_filter(call: CallbackQuery, state: FSMContext, key, value):
    data = await state.get_data()
    filters = dict(data.get("search_filters", {}))
    filters[key] = value
    await state.update_data(search_filters=filters)
    await show_filters(call, state)

@router.callback_query(F.data.startswith("setservice:"))
async def setservice(call: CallbackQuery, state: FSMContext):
    await set_filter(call, state, "service", call.data.split(":", 1)[1])

@router.callback_query(F.data.startswith("setprice:"))
async def setprice(call: CallbackQuery, state: FSMContext):
    v = call.data.split(":", 1)[1]
    ranges = {
        "any": (0, 10**12),
        "1": (0, 1_000_000),
        "2": (1_000_000, 3_000_000),
        "3": (3_000_000, 5_000_000),
        "4": (5_000_000, 10**12),
    }
    lo, hi = ranges[v]
    data = await state.get_data()
    filters = dict(data.get("search_filters", {}))
    filters["min_price"] = lo
    filters["max_price"] = hi
    await state.update_data(search_filters=filters)
    await show_filters(call, state)
@router.callback_query(F.data.startswith("setrating:"))
async def setrating(call: CallbackQuery, state: FSMContext):
    await set_filter(call, state, "rating", float(call.data.split(":", 1)[1]))

async def display_result(call,state,idx=0,new_message=False):
    data=await state.get_data(); filters=data.get("search_filters",{}); groups=await find_groups(filters)
    lang=await get_user_lang(call.from_user.id)
    if not groups:
        await call.message.edit_text(t(lang,"no_results"),reply_markup=filter_kb(lang)); return
    idx=max(0,min(idx,len(groups)-1)); await state.update_data(result_index=idx, current_group_id=groups[idx].id)
    g=groups[idx]
    services=", ".join(s.name_uz if lang=="uz" else s.name_ru for s in g.services)
    name=g.name_uz if lang=="uz" else g.name_ru; region=g.region_uz if lang=="uz" else g.region_ru; desc=g.description_uz if lang=="uz" else g.description_ru
    text=(f"🎭 <b>{name}</b>\n\n{desc}\n\n📍 {region}\n🎯 {services}\n💰 {g.price_from:,} — {g.price_to:,} so‘m\n⭐ {g.rating:.1f} ({g.reviews_count})\n👥 {g.members_count}\n💼 {g.experience_years} yil\n📞 {g.phone}\n✈️ {g.telegram}")
    kb=results_kb(lang,idx,len(groups))
    if new_message or call.message.photo:
        try: await call.message.delete()
        except: pass
    if g.photo:
        await call.message.answer_photo(g.photo,caption=text,reply_markup=kb,parse_mode="HTML")
    else:
        await call.message.edit_text(text,reply_markup=kb,parse_mode="HTML")

@router.callback_query(F.data=="search:results")
async def search_results(call: CallbackQuery, state: FSMContext):
    # Answer immediately so Telegram does not leave the callback spinner running
    # while the database query/message update is being processed.
    await call.answer()
    try:
        await display_result(call, state, 0)
    except Exception:
        import logging
        logging.exception("search:results failed")
        lang = await get_user_lang(call.from_user.id)
        await call.message.answer(
            t(lang, "no_results"),
            reply_markup=filter_kb(lang),
        )

@router.callback_query(F.data=="search:all")
async def all_groups(call: CallbackQuery, state: FSMContext):
    # Clear every filter and show the complete catalog.
    await call.answer()
    await state.update_data(search_filters={})
    try:
        await display_result(call, state, 0)
    except Exception:
        import logging
        logging.exception("search:all failed")
        lang = await get_user_lang(call.from_user.id)
        await call.message.answer(
            t(lang, "no_results"),
            reply_markup=filter_kb(lang),
        )

@router.callback_query(F.data.startswith("result:"))
async def result(call,state): await display_result(call,state,int(call.data.split(":",1)[1]))

@router.callback_query(F.data == "request:contact")
async def contact_team(call: CallbackQuery, state: FSMContext):
    from database.db import create_request
    lang = await get_user_lang(call.from_user.id)
    data = await state.get_data()
    group_id = data.get("current_group_id")
    if not group_id:
        await call.answer(t(lang, "group_not_found"), show_alert=True)
        return
    req, created = await create_request(call.from_user.id, int(group_id))
    if not created:
        await call.answer(t(lang, "request_exists"), show_alert=True)
        return
    async with __import__('database.db', fromlist=['Session']).Session() as s:
        from database.models import Group
        g = await s.get(Group, int(group_id))
    if g:
        name = g.name_uz if lang == "uz" else g.name_ru
        await call.message.answer(t(lang, "request_created", name=name, phone=g.phone, telegram=g.telegram))
    await call.answer(t(lang, "request_sent"), show_alert=True)
