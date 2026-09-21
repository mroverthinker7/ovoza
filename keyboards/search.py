from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from services.i18n import t
from services.catalog import SERVICES, CITY, DISTRICTS

def filter_kb(lang, filters=None):
    filters = filters or {}
    service_mark = "✅ " if filters.get("service") else ""
    region_mark = "✅ " if filters.get("region") else ""
    price_mark = "✅ " if "min_price" in filters or "max_price" in filters else ""
    rating_mark = "✅ " if filters.get("rating", 0) else ""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=service_mark + t(lang,"service"), callback_data="filter:service")],
        [InlineKeyboardButton(text=region_mark + t(lang,"region"), callback_data="filter:region")],
        [InlineKeyboardButton(text=price_mark + t(lang,"price"), callback_data="filter:price")],
        [InlineKeyboardButton(text=rating_mark + t(lang,"rating"), callback_data="filter:rating")],
        [InlineKeyboardButton(text=t(lang,"show_results"), callback_data="search:results")],
        [InlineKeyboardButton(text=t(lang,"all"), callback_data="search:all")],
        [InlineKeyboardButton(text=t(lang,"reset"), callback_data="search:reset")],
        [InlineKeyboardButton(text=t(lang,"back"), callback_data="back:main")],
    ])

def service_kb(lang):
    rows=[[InlineKeyboardButton(text=(u if lang=="uz" else r), callback_data=f"setservice:{k}")] for k,u,r in SERVICES]
    rows.append([InlineKeyboardButton(text=t(lang,"back"), callback_data="filter:back")])
    return InlineKeyboardMarkup(inline_keyboard=rows)

def region_kb(lang):
    city_text = CITY[1] if lang == "uz" else CITY[2]
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"📍 {city_text}", callback_data="setregion:toshkent")],
        [InlineKeyboardButton(text=t(lang, "back"), callback_data="filter:back")],
    ])

def district_kb(lang):
    rows=[]
    for i in range(0, len(DISTRICTS), 2):
        rows.append([InlineKeyboardButton(text=(DISTRICTS[j][1] if lang=="uz" else DISTRICTS[j][2]), callback_data=f"setdistrict:{DISTRICTS[j][0]}") for j in range(i, min(i+2, len(DISTRICTS)))])
    rows.append([InlineKeyboardButton(text=t(lang, "back"), callback_data="filter:region")])
    return InlineKeyboardMarkup(inline_keyboard=rows)

def price_kb(lang):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t(lang,"price_any"), callback_data="setprice:any")],
        [InlineKeyboardButton(text=t(lang,"price_1"), callback_data="setprice:1")],
        [InlineKeyboardButton(text=t(lang,"price_2"), callback_data="setprice:2")],
        [InlineKeyboardButton(text=t(lang,"price_3"), callback_data="setprice:3")],
        [InlineKeyboardButton(text=t(lang,"price_4"), callback_data="setprice:4")],
        [InlineKeyboardButton(text=t(lang,"back"), callback_data="filter:back")],
    ])

def rating_kb(lang):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t(lang,"rating_any"), callback_data="setrating:0")],
        [InlineKeyboardButton(text="⭐ 3+", callback_data="setrating:3")],
        [InlineKeyboardButton(text="⭐ 4+", callback_data="setrating:4")],
        [InlineKeyboardButton(text="⭐ 4.5+", callback_data="setrating:4.5")],
        [InlineKeyboardButton(text="⭐ 5", callback_data="setrating:5")],
        [InlineKeyboardButton(text=t(lang,"back"), callback_data="filter:back")],
    ])

def results_kb(lang, idx, total):
    nav=[]
    if idx>0: nav.append(InlineKeyboardButton(text=t(lang,"prev"), callback_data=f"result:{idx-1}"))
    nav.append(InlineKeyboardButton(text=f"{idx+1} / {total}", callback_data="noop"))
    if idx<total-1: nav.append(InlineKeyboardButton(text=t(lang,"next"), callback_data=f"result:{idx+1}"))
    return InlineKeyboardMarkup(inline_keyboard=[nav,[InlineKeyboardButton(text=t(lang,"contact"),callback_data="request:contact")],[InlineKeyboardButton(text=t(lang,"filters_btn"),callback_data="filter:back")],[InlineKeyboardButton(text=t(lang,"back"),callback_data="back:main")]])
