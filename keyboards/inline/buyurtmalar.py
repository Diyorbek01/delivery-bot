import requests
from aiogram import types
from aiogram.dispatcher.filters import state
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from data.config import BASE_URL, MY_TOKEN


def get_region(user_id):
    url = f"{BASE_URL}my-district-all-orders/"

    payload = {}
    headers = {
        'MyToken': MY_TOKEN,
        'ChatId': str(user_id)
    }

    response = requests.request("GET", url, headers=headers, data=payload)

    keyboard_markup = types.InlineKeyboardMarkup(row_width=2)
    for i in response.json():
        keyboard_markup.insert(
            types.InlineKeyboardButton(text=f"{i['name']} | {i['order_count']}", callback_data=f"{i['id']}"),
        )

    return keyboard_markup


def full_extra_menu(id):
    FullExtraMenu = InlineKeyboardMarkup(
        row_width=2,
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🚚", callback_data=f"delivering-{id}"),
                InlineKeyboardButton(text="✅", callback_data=f"confirm-{id}"),
                InlineKeyboardButton(text="⏰", callback_data=f"extratime-{id}"),
                InlineKeyboardButton(text="❌", callback_data=f"cancel-{id}"),
            ]
        ])
    return FullExtraMenu


def delivering_menu(id):
    DeliveringExtraMenu = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅", callback_data=f"confirm-{id}"),
                InlineKeyboardButton(text="⏰", callback_data=f"extratime-{id}"),
                InlineKeyboardButton(text="❌", callback_data=f"cancel-{id}"),
            ]
        ])
    return DeliveringExtraMenu


def retry_call_menu(id):
    FullExtraMenu = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🚚", callback_data=f"delivering-{id}"),
                InlineKeyboardButton(text="✅", callback_data=f"confirm-{id}"),
                InlineKeyboardButton(text="❌", callback_data=f"cancel-{id}"),

            ]
        ])
    return FullExtraMenu


def time_menu(id):
    TimeMenu = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="1 kun", callback_data=f"1-{id}"),
                InlineKeyboardButton(text="3 kun", callback_data=f"3-{id}"),
            ],
            [
                InlineKeyboardButton(text="5 kun", callback_data=f"5-{id}"),
                InlineKeyboardButton(text="10 kun", callback_data=f"10-{id}"),
            ],
            [
                InlineKeyboardButton(text="⬅️Ortga", callback_data=f"back-{id}"),
            ]
        ])
    return TimeMenu


def confirmation_menu(id, num):
    DeliveringExtraMenu = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅", callback_data=f"confirm-{id}-{num}"),
                InlineKeyboardButton(text="❌", callback_data=f"cancel-{id}-{num}"),
            ]
        ])
    return DeliveringExtraMenu


Registration = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Kodni olish", url=f"https://cs27146.tmweb.ru/driver-login/"),
        ]
    ])
