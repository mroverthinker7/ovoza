import asyncio, os, sys
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy import select, func
from database.db import Session, count_groups, add_admin, get_user_lang
from database.models import Admin, Group, Service, Request, User
from keyboards.main import admin_kb, main_kb
from keyboards.common import back_kb
from services.i18n import t
from services.admin import is_admin
from services.catalog import SERVICES, CITY, DISTRICTS

router=Router()

class AddGroup(StatesGroup):
    name_uz=State(); name_ru=State(); desc_uz=State(); desc_ru=State(); region=State(); services=State(); price_from=State(); price_to=State(); members=State(); experience=State(); phone=State(); telegram=State(); photo=State(); preview=State()
class AddAdmin(StatesGroup):
    telegram_id=State()

async def guard(call):
    if not await is_admin(call.from_user.id):
        await call.answer("⛔",show_alert=True); return False
    return True

@router.callback_query(F.data=="admin:open")
async def open_admin(call: CallbackQuery, state:FSMContext):
    if not await guard(call): return
    await state.clear()
    lang=await get_user_lang(call.from_user.id)
    await call.message.edit_text(t(lang,"admin_panel"),reply_markup=admin_kb(lang)); await call.answer()

@router.callback_query(F.data=="admin:stats")
async def stats(call: CallbackQuery):
    if not await guard(call): return
    lang=await get_user_lang(call.from_user.id)
    async with Session() as state: admins=int(await state.scalar(select(func.count(Admin.id))) or 0)
    await call.message.edit_text(t(lang,"stats_text",groups=await count_groups(),admins=admins),reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=t(lang,"back"),callback_data="admin:open")]])); await call.answer()

@router.callback_query(F.data=="admin:add_admin")
async def add_admin_start(call:CallbackQuery,state:FSMContext):
    if not await guard(call): return
    lang=await get_user_lang(call.from_user.id); await state.set_state(AddAdmin.telegram_id)
    await call.message.edit_text(t(lang,"send_admin_id"),reply_markup=back_kb("admin:open",t(lang,"back"))); await call.answer()

@router.message(AddAdmin.telegram_id)
async def add_admin_value(message:Message,state:FSMContext):
    lang=await get_user_lang(message.from_user.id)
    value=message.text.strip() if message.text else ""
    if not value.isdigit():
        await message.answer(t(lang,"invalid_id"),reply_markup=back_kb("admin:open",t(lang,"back"))); return
    await add_admin(int(value)); await state.clear()
    await message.answer(t(lang,"admin_added",id=value),reply_markup=admin_kb(lang))

@router.callback_query(F.data=="admin:add_group")
async def add_group_start(call:CallbackQuery,state:FSMContext):
    if not await guard(call): return
    lang=await get_user_lang(call.from_user.id); await state.clear(); await state.set_state(AddGroup.name_uz)
    await call.message.edit_text(t(lang,"enter_name_uz"),reply_markup=back_kb("admin:open",t(lang,"back"))); await call.answer()

async def prompt(message,state,st,key,back_to,lang):
    await state.set_state(st); await message.answer(t(lang,key),reply_markup=back_kb(back_to,t(lang,"back")))

@router.message(AddGroup.name_uz)
async def ag1(m: Message, state: FSMContext): await state.update_data(name_uz=m.text); await prompt(m,state,AddGroup.name_ru,"enter_name_ru","admin:add_group_back:name_uz",await get_user_lang(m.from_user.id))
@router.message(AddGroup.name_ru)
async def ag2(m: Message, state: FSMContext): await state.update_data(name_ru=m.text); await prompt(m,state,AddGroup.desc_uz,"enter_desc_uz","admin:add_group_back:name_ru",await get_user_lang(m.from_user.id))
@router.message(AddGroup.desc_uz)
async def ag3(m: Message, state: FSMContext): await state.update_data(desc_uz=m.text); await prompt(m,state,AddGroup.desc_ru,"enter_desc_ru","admin:add_group_back:desc_uz",await get_user_lang(m.from_user.id))
@router.message(AddGroup.desc_ru)
async def ag4(m: Message, state: FSMContext):
    lang = await get_user_lang(m.from_user.id)
    await state.update_data(desc_ru=m.text)
    await state.set_state(AddGroup.region)
    await m.answer(t(lang, "choose_region"), reply_markup=region_admin_kb(lang))

@router.message(AddGroup.region)
async def ag_region_text(m: Message, state: FSMContext):
    lang = await get_user_lang(m.from_user.id)
    # Region is selected from the inline keyboard so that the stored key and
    # localized DB values can never get out of sync.
    await m.answer(t(lang, "choose_region"), reply_markup=region_admin_kb(lang))

def region_admin_kb(lang):
    city_text = CITY[1] if lang == "uz" else CITY[2]
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"📍 {city_text}", callback_data="agregion:toshkent")],
        [InlineKeyboardButton(text=t(lang, "back"), callback_data="admin:add_group_back:desc_ru")],
    ])

def district_admin_kb(lang):
    rows=[]
    for i in range(0, len(DISTRICTS), 2):
        rows.append([InlineKeyboardButton(text=(DISTRICTS[j][1] if lang=="uz" else DISTRICTS[j][2]), callback_data=f"agdistrict:{DISTRICTS[j][0]}") for j in range(i, min(i+2, len(DISTRICTS)))])
    rows.append([InlineKeyboardButton(text=t(lang, "back"), callback_data="admin:add_group_back:region")])
    return InlineKeyboardMarkup(inline_keyboard=rows)

def services_admin_kb(lang,selected):
    rows=[]
    for k,u,r in SERVICES:
        mark="✅ " if k in selected else ""
        rows.append([InlineKeyboardButton(text=mark+(u if lang=="uz" else r),callback_data=f"agservice:{k}")])
    rows.append([InlineKeyboardButton(text=t(lang,"services_done"),callback_data="agservice:done")])
    rows.append([InlineKeyboardButton(text=t(lang,"back"),callback_data="admin:add_group_back:region")]); return InlineKeyboardMarkup(inline_keyboard=rows)

@router.callback_query(F.data=="agregion:toshkent")
async def choose_city_admin(call: CallbackQuery, state: FSMContext):
    lang = await get_user_lang(call.from_user.id)
    await state.set_state(AddGroup.region)
    await call.message.edit_text(t(lang, "select_district"), reply_markup=district_admin_kb(lang))
    await call.answer()

@router.callback_query(F.data.startswith("agdistrict:"))
async def choose_district_admin(call: CallbackQuery, state: FSMContext):
    lang = await get_user_lang(call.from_user.id)
    key = call.data.split(":", 1)[1]
    district = next((x for x in DISTRICTS if x[0] == key), None)
    if not district:
        await call.answer("❌", show_alert=True)
        return
    await state.update_data(region_uz=district[1], region_ru=district[2], services=[])
    await state.set_state(AddGroup.services)
    await call.message.edit_text(t(lang, "choose_services"), reply_markup=services_admin_kb(lang, []))
    await call.answer()

@router.callback_query(F.data.startswith("agservice:"))
async def choose_service(call: CallbackQuery, state: FSMContext):
    lang=await get_user_lang(call.from_user.id); key=call.data.split(":")[1]; data=await state.get_data(); selected=data.get("services",[])
    if key=="done":
        if not selected: await call.answer("Kamida bitta xizmat tanlang / Выберите хотя бы одну услугу",show_alert=True); return
        await state.set_state(AddGroup.price_from); await call.message.edit_text(t(lang,"enter_price_from"),reply_markup=back_kb("admin:add_group_back:services",t(lang,"back"))); await call.answer(); return
    if key in selected: selected.remove(key)
    else: selected.append(key)
    await state.update_data(services=selected); await call.message.edit_reply_markup(reply_markup=services_admin_kb(lang,selected)); await call.answer()

async def number_step(m,state,current,next_state,next_key,back,lang):
    if not (m.text and m.text.strip().isdigit()): await m.answer(t(lang,"invalid_number"),reply_markup=back_kb(back,t(lang,"back"))); return False
    await state.update_data(**{current:int(m.text.strip())}); await prompt(m,state,next_state,next_key,back,lang); return True

@router.message(AddGroup.price_from)
async def agpf(m: Message, state: FSMContext):
    lang=await get_user_lang(m.from_user.id)
    if not await number_step(m,state,"price_from",AddGroup.price_to,"enter_price_to","admin:add_group_back:services",lang): return
@router.message(AddGroup.price_to)
async def agpt(m: Message, state: FSMContext):
    lang=await get_user_lang(m.from_user.id)
    if not await number_step(m,state,"price_to",AddGroup.members,"enter_members","admin:add_group_back:price_from",lang): return
@router.message(AddGroup.members)
async def agm(m: Message, state: FSMContext):
    lang=await get_user_lang(m.from_user.id)
    if not await number_step(m,state,"members",AddGroup.experience,"enter_experience","admin:add_group_back:price_to",lang): return
@router.message(AddGroup.experience)
async def age(m: Message, state: FSMContext):
    lang=await get_user_lang(m.from_user.id)
    if not await number_step(m,state,"experience",AddGroup.phone,"enter_phone","admin:add_group_back:members",lang): return
@router.message(AddGroup.phone)
async def agphone(m: Message, state: FSMContext): await state.update_data(phone=m.text); await prompt(m,state,AddGroup.telegram,"enter_telegram","admin:add_group_back:experience",await get_user_lang(m.from_user.id))
@router.message(AddGroup.telegram)
async def agtg(m: Message, state: FSMContext): await state.update_data(telegram=m.text); await prompt(m,state,AddGroup.photo,"send_photo","admin:add_group_back:phone",await get_user_lang(m.from_user.id))
@router.message(AddGroup.photo)
async def agphoto(m: Message, state: FSMContext):
    lang=await get_user_lang(m.from_user.id)
    photo=m.photo[-1].file_id if m.photo else None
    if not photo and (m.text or "").strip().lower()!="skip": await m.answer(t(lang,"send_photo"),reply_markup=back_kb("admin:add_group_back:telegram",t(lang,"back"))); return
    await state.update_data(photo=photo); data=await state.get_data(); await state.set_state(AddGroup.preview)
    sv=[]
    for k in data["services"]:
        x=next(x for x in SERVICES if x[0]==k); sv.append(x[1] if lang=="uz" else x[2])
    txt=t(lang,"preview",name=data["name_uz"] if lang=="uz" else data["name_ru"],region=data["region_uz"] if lang=="uz" else data["region_ru"],price_from=data["price_from"],price_to=data["price_to"],members=data["members"],experience=data["experience"],phone=data["phone"],telegram=data["telegram"],services=", ".join(sv))
    kb=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=t(lang,"publish"),callback_data="ag:publish")],[InlineKeyboardButton(text=t(lang,"edit"),callback_data="admin:add_group_back:telegram")],[InlineKeyboardButton(text=t(lang,"back"),callback_data="admin:add_group_back:telegram")]])
    if photo: await m.answer_photo(photo,caption=txt,reply_markup=kb)
    else: await m.answer(txt,reply_markup=kb)

@router.callback_query(F.data == "ag:publish")
async def publish(call: CallbackQuery, state: FSMContext):
    if not await guard(call):
        return

    lang = await get_user_lang(call.from_user.id)
    data = await state.get_data()

    required = (
        "name_uz", "name_ru", "desc_uz", "desc_ru",
        "region_uz", "region_ru", "price_from", "price_to",
        "members", "experience", "phone", "telegram", "services"
    )
    if any(key not in data for key in required):
        await call.answer("E'lon ma'lumotlari to'liq emas. / Данные объявления неполные.", show_alert=True)
        return

    if not data["services"]:
        await call.answer("Kamida bitta xizmat tanlang. / Выберите хотя бы одну услугу.", show_alert=True)
        return

    # IMPORTANT: do not shadow the FSMContext with the SQLAlchemy session.
    # The previous implementation used `as state`, so `state.clear()` called
    # on an AsyncSession after publishing and raised an exception.
    async with Session() as session:
        group = Group(
            name_uz=data["name_uz"],
            name_ru=data["name_ru"],
            description_uz=data["desc_uz"],
            description_ru=data["desc_ru"],
            region_uz=data["region_uz"],
            region_ru=data["region_ru"],
            price_from=int(data["price_from"]),
            price_to=int(data["price_to"]),
            members_count=int(data["members"]),
            experience_years=int(data["experience"]),
            phone=data["phone"],
            telegram=data["telegram"],
            photo=data.get("photo"),
            rating=0.0,
            reviews_count=0,
        )

        for service_key in data["services"]:
            service = next((item for item in SERVICES if item[0] == service_key), None)
            if service:
                group.services.append(Service(name_uz=service[1], name_ru=service[2]))

        session.add(group)
        await session.commit()
        await session.refresh(group)
        group_id = group.id

    # Now clear the actual FSM context.
    await state.clear()

    # Replace the preview message with a clear success message.
    try:
        if call.message.photo:
            await call.message.edit_caption(
                caption=t(lang, "group_added") + f"\n\n🆔 ID: {group_id}",
                reply_markup=admin_kb(lang),
            )
        else:
            await call.message.edit_text(
                t(lang, "group_added") + f"\n\n🆔 ID: {group_id}",
                reply_markup=admin_kb(lang),
            )
    except Exception:
        await call.message.answer(
            t(lang, "group_added") + f"\n\n🆔 ID: {group_id}",
            reply_markup=admin_kb(lang),
        )

    await call.answer("✅")

# Generic back routing for add-group wizard. It intentionally restores the previous screen and keeps saved data.
@router.callback_query(F.data.startswith("admin:add_group_back:"))
async def add_group_back(call: CallbackQuery, state: FSMContext):
    if not await guard(call): return
    target=call.data.split(":")[-1]; lang=await get_user_lang(call.from_user.id); data=await state.get_data()
    mapping={
      "name_uz":(AddGroup.name_uz,"enter_name_uz","admin:open"),
      "name_ru":(AddGroup.name_ru,"enter_name_ru","admin:add_group_back:name_uz"),
      "desc_uz":(AddGroup.desc_uz,"enter_desc_uz","admin:add_group_back:name_ru"),
      "desc_ru":(AddGroup.desc_ru,"enter_desc_ru","admin:add_group_back:desc_uz"),
      "region":(AddGroup.region,"choose_region","admin:add_group_back:desc_ru"),
      "services":(AddGroup.services,"choose_services","admin:add_group_back:region"),
      "price_from":(AddGroup.price_from,"enter_price_from","admin:add_group_back:services"),
      "price_to":(AddGroup.price_to,"enter_price_to","admin:add_group_back:price_from"),
      "members":(AddGroup.members,"enter_members","admin:add_group_back:price_to"),
      "experience":(AddGroup.experience,"enter_experience","admin:add_group_back:members"),
      "phone":(AddGroup.phone,"enter_phone","admin:add_group_back:experience"),
      "telegram":(AddGroup.telegram,"enter_telegram","admin:add_group_back:phone"),
      "photo":(AddGroup.photo,"send_photo","admin:add_group_back:telegram"),
    }
    if target in mapping:
        st,key,back=mapping[target]; await state.set_state(st)
        if target=="region": kb=region_admin_kb(lang)
        elif target=="services": kb=services_admin_kb(lang,data.get("services",[]))
        else: kb=back_kb(back,t(lang,"back"))
        await call.message.edit_text(t(lang,key),reply_markup=kb); await call.answer(); return
    await call.answer()

@router.callback_query(F.data=="admin:restart")
async def restart_prompt(call):
    if not await guard(call): return
    lang=await get_user_lang(call.from_user.id)
    kb=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=t(lang,"yes"),callback_data="admin:restart_yes"),InlineKeyboardButton(text=t(lang,"no"),callback_data="admin:open")],[InlineKeyboardButton(text=t(lang,"back"),callback_data="admin:open")]])
    await call.message.edit_text(t(lang,"confirm_restart"),reply_markup=kb); await call.answer()

@router.callback_query(F.data=="admin:restart_yes")
async def restart_yes(call):
    if not await guard(call): return
    await call.answer("Restarting...")
    await call.message.answer("🔄 Restart...")
    await asyncio.sleep(1)
    os.execv(sys.executable,[sys.executable,*sys.argv])


# -------------------- GROUP DELETION --------------------
DELETE_PAGE_SIZE = 5

async def _delete_groups_page(call: CallbackQuery, page: int = 0):
    if not await guard(call):
        return
    lang = await get_user_lang(call.from_user.id)
    async with Session() as state:
        groups = list((await state.scalars(select(Group).order_by(Group.id.desc()))).all())

    if not groups:
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=t(lang, "back"), callback_data="admin:open")]
        ])
        await call.message.edit_text(t(lang, "no_groups_to_delete"), reply_markup=kb)
        await call.answer()
        return

    pages = (len(groups) + DELETE_PAGE_SIZE - 1) // DELETE_PAGE_SIZE
    page = max(0, min(page, pages - 1))
    chunk = groups[page * DELETE_PAGE_SIZE:(page + 1) * DELETE_PAGE_SIZE]
    rows = []
    for g in chunk:
        name = g.name_uz if lang == "uz" else g.name_ru
        rows.append([InlineKeyboardButton(text=f"🗑 {name}", callback_data=f"admin:delete_select:{g.id}")])

    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton(text=t(lang, "prev_page"), callback_data=f"admin:delete_page:{page-1}"))
    nav.append(InlineKeyboardButton(text=f"{page+1} / {pages}", callback_data="noop"))
    if page < pages - 1:
        nav.append(InlineKeyboardButton(text=t(lang, "next_page"), callback_data=f"admin:delete_page:{page+1}"))
    rows.append(nav)
    rows.append([InlineKeyboardButton(text=t(lang, "back"), callback_data="admin:open")])
    kb = InlineKeyboardMarkup(inline_keyboard=rows)
    await call.message.edit_text(t(lang, "delete_groups_title"), reply_markup=kb)
    await call.answer()

@router.callback_query(F.data == "admin:delete_groups")
async def delete_groups_start(call: CallbackQuery):
    await _delete_groups_page(call, 0)

@router.callback_query(F.data.startswith("admin:delete_page:"))
async def delete_groups_page(call: CallbackQuery):
    try:
        page = int(call.data.split(":")[-1])
    except ValueError:
        page = 0
    await _delete_groups_page(call, page)

@router.callback_query(F.data.startswith("admin:delete_select:"))
async def delete_group_select(call: CallbackQuery):
    if not await guard(call):
        return
    lang = await get_user_lang(call.from_user.id)
    try:
        group_id = int(call.data.split(":")[-1])
    except ValueError:
        await call.answer(t(lang, "group_not_found"), show_alert=True)
        return

    async with Session() as state:
        g = await state.get(Group, group_id)
        if not g:
            await call.answer(t(lang, "group_not_found"), show_alert=True)
            return
        name = g.name_uz if lang == "uz" else g.name_ru

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t(lang, "delete_yes"), callback_data=f"admin:delete_yes:{group_id}")],
        [InlineKeyboardButton(text=t(lang, "delete_cancel"), callback_data="admin:delete_groups")],
        [InlineKeyboardButton(text=t(lang, "back"), callback_data="admin:delete_groups")],
    ])
    await call.message.edit_text(t(lang, "delete_confirm", name=name), reply_markup=kb)
    await call.answer()

@router.callback_query(F.data.startswith("admin:delete_yes:"))
async def delete_group_confirm(call: CallbackQuery):
    if not await guard(call):
        return
    lang = await get_user_lang(call.from_user.id)
    try:
        group_id = int(call.data.split(":")[-1])
    except ValueError:
        await call.answer(t(lang, "group_not_found"), show_alert=True)
        return

    async with Session() as state:
        g = await state.get(Group, group_id)
        if not g:
            await call.answer(t(lang, "group_not_found"), show_alert=True)
            return
        await state.delete(g)
        await state.commit()

    await call.answer(t(lang, "group_deleted"), show_alert=True)
    await _delete_groups_page(call, 0)

# -------------------- REQUESTS / REVIEWS --------------------
REQUEST_PAGE_SIZE = 5

async def _requests_page(call: CallbackQuery, page: int = 0):
    if not await guard(call):
        return
    lang = await get_user_lang(call.from_user.id)
    from sqlalchemy.orm import selectinload
    async with Session() as state:
        stmt = select(Group, Request, User).join(
            Request, Group.id == Request.group_id
        ).join(
            User, Request.user_id == User.id
        ).where(Request.status == "pending").order_by(Request.created_at.asc())
        rows = (await state.execute(stmt)).all()
    if not rows:
        kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=t(lang, "back"), callback_data="admin:open")]])
        await call.message.edit_text(t(lang, "no_pending_requests"), reply_markup=kb)
        await call.answer()
        return
    pages = (len(rows) + REQUEST_PAGE_SIZE - 1) // REQUEST_PAGE_SIZE
    page = max(0, min(page, pages - 1))
    chunk = rows[page * REQUEST_PAGE_SIZE:(page + 1) * REQUEST_PAGE_SIZE]
    buttons = []
    for group, req, user in chunk:
        name = group.name_uz if lang == "uz" else group.name_ru
        buttons.append([InlineKeyboardButton(text=f"📩 #{req.id} — {name} — {user.telegram_id}", callback_data=f"admin:req:{req.id}")])
    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton(text=t(lang, "prev_page"), callback_data=f"admin:req_page:{page-1}"))
    nav.append(InlineKeyboardButton(text=f"{page+1} / {pages}", callback_data="noop"))
    if page < pages - 1:
        nav.append(InlineKeyboardButton(text=t(lang, "next_page"), callback_data=f"admin:req_page:{page+1}"))
    buttons.append(nav)
    buttons.append([InlineKeyboardButton(text=t(lang, "back"), callback_data="admin:open")])
    await call.message.edit_text(t(lang, "requests_title"), reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))
    await call.answer()

@router.callback_query(F.data == "admin:requests")
async def requests_start(call: CallbackQuery):
    await _requests_page(call, 0)

@router.callback_query(F.data.startswith("admin:req_page:"))
async def requests_page(call: CallbackQuery):
    try:
        page = int(call.data.split(":")[-1])
    except ValueError:
        page = 0
    await _requests_page(call, page)

@router.callback_query(F.data.startswith("admin:req:"))
async def request_detail(call: CallbackQuery):
    if not await guard(call):
        return
    lang = await get_user_lang(call.from_user.id)
    request_id = int(call.data.split(":")[-1])
    async with Session() as state:
        stmt = select(Request, Group, User).join(Group, Group.id == Request.group_id).join(User, User.id == Request.user_id).where(Request.id == request_id)
        row = (await state.execute(stmt)).first()
    if not row:
        await call.answer(t(lang, "request_not_found"), show_alert=True)
        return
    req, group, user = row
    name = group.name_uz if lang == "uz" else group.name_ru
    text = t(lang, "request_detail", request_id=req.id, name=name, user_id=user.telegram_id, phone=group.phone, telegram=group.telegram, status=req.status)
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t(lang, "mark_completed"), callback_data=f"admin:req_complete:{req.id}")],
        [InlineKeyboardButton(text=t(lang, "back"), callback_data="admin:requests")],
    ])
    await call.message.edit_text(text, reply_markup=kb)
    await call.answer()

@router.callback_query(F.data.startswith("admin:req_complete:"))
async def request_complete(call: CallbackQuery):
    if not await guard(call):
        return
    lang = await get_user_lang(call.from_user.id)
    request_id = int(call.data.split(":")[-1])
    from database.db import complete_request
    async with Session() as state:
        stmt = select(Request, User, Group).join(User, User.id == Request.user_id).join(Group, Group.id == Request.group_id).where(Request.id == request_id)
        row = (await state.execute(stmt)).first()
    req = await complete_request(request_id)
    if not req or not row:
        await call.answer(t(lang, "request_not_found"), show_alert=True)
        return
    _, user, group = row
    user_lang = user.language or "uz"
    from keyboards.reviews import rating_kb
    name = group.name_uz if user_lang == "uz" else group.name_ru
    try:
        await call.bot.send_message(user.telegram_id, t(user_lang, "service_completed", name=name), reply_markup=rating_kb(user_lang, request_id))
    except Exception:
        pass
    await call.answer(t(lang, "request_completed"), show_alert=True)
    await _requests_page(call, 0)
