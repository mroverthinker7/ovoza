from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def language_kb():
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🇺🇿 O‘zbekcha", callback_data="lang:uz"), InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang:ru")]])
