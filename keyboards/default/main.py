from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

menu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='📝Buyurtmalar'),
            KeyboardButton(text='🛒Ombor'),
            KeyboardButton(text='📋Hisobot'),
        ],
    ],
    resize_keyboard=True
)
filter_order = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='🗞Hammasi'),
            KeyboardButton(text='📌Qabul qilinganlar'),
        ],
        [
            KeyboardButton(text='⬅️Ortga'),
        ],
    ],
    resize_keyboard=True
)

stock_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="🖨Excel formatda"),
            KeyboardButton(text='⬅️Ortga'),
        ],
    ],
    resize_keyboard=True
)

accounting_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="💵Daromad"),
            KeyboardButton(text='💰Kassa')],
        [
            KeyboardButton(text='📊Tarix'),
            KeyboardButton(text='⬅️Ortga'),
        ],
    ],
    resize_keyboard=True
)
