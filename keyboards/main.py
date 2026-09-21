from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from services.i18n import t

def main_kb(lang, admin=False):
    rows=[[InlineKeyboardButton(text=t(lang,"search"), callback_data="search:open")]]
    if admin:
        rows.append([InlineKeyboardButton(text=t(lang,"admin"), callback_data="admin:open")])
    return InlineKeyboardMarkup(inline_keyboard=rows)

def admin_kb(lang):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t(lang,"add_group"), callback_data="admin:add_group")],
        [InlineKeyboardButton(text=t(lang,"add_admin"), callback_data="admin:add_admin")],
        [InlineKeyboardButton(text=t(lang,"stats"), callback_data="admin:stats")],
        [InlineKeyboardButton(text=t(lang,"delete_group"), callback_data="admin:delete_groups")],
        [InlineKeyboardButton(text=t(lang,"requests"), callback_data="admin:requests")],
        [InlineKeyboardButton(text=t(lang,"restart"), callback_data="admin:restart")],
        [InlineKeyboardButton(text=t(lang,"back"), callback_data="back:main")],
    ])
