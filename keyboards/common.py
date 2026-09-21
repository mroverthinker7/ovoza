from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def back_kb(callback="back:main", text="◀️ Orqaga"):
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=text, callback_data=callback)]])
