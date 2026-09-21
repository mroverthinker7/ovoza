from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from services.i18n import t

def rating_kb(lang: str, request_id: int):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⭐ 1", callback_data=f"review:rate:{request_id}:1"), InlineKeyboardButton(text="⭐ 2", callback_data=f"review:rate:{request_id}:2")],
        [InlineKeyboardButton(text="⭐ 3", callback_data=f"review:rate:{request_id}:3"), InlineKeyboardButton(text="⭐ 4", callback_data=f"review:rate:{request_id}:4")],
        [InlineKeyboardButton(text="⭐ 5", callback_data=f"review:rate:{request_id}:5")],
        [InlineKeyboardButton(text=t(lang, "back"), callback_data="back:main")],
    ])

def review_comment_kb(lang: str, request_id: int):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t(lang, "skip_review_comment"), callback_data=f"review:skip:{request_id}")],
        [InlineKeyboardButton(text=t(lang, "back"), callback_data="back:main")],
    ])
