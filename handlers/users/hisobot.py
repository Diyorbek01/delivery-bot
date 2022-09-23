import urllib

import requests
from aiogram import Bot
from aiogram.dispatcher import FSMContext
from aiogram.types import Message, InputFile

from data.config import BASE_URL, MY_TOKEN, BOT_TOKEN
from handlers.users.start import check_user
from keyboards.default.main import stock_keyboard, accounting_keyboard, menu
from keyboards.inline.buyurtmalar import Registration
from loader import dp

bot = Bot(token=BOT_TOKEN)


@dp.message_handler(text='📋Hisobot', state=['check','confirmation', 'order', 'time', None])
async def send_accounting(message: Message, state: FSMContext):
    await bot.send_message(message.from_user.id, "Hisobot bo'limi", reply_markup=accounting_keyboard)


@dp.message_handler(text='💵Daromad', state=['check', 'order', 'time', None])
async def send_income(message: Message, state: FSMContext):
    user_id = message.from_user.id
    url = f"{BASE_URL}driver-income/"

    payload = {}
    headers = {
        'MyToken': f'{MY_TOKEN}',
        'ChatId': str(user_id)
    }

    response = requests.request("GET", url, headers=headers, data=payload)

    ress = response.json()
    if response.status_code == 200:
        await bot.send_message(message.from_user.id, f'<b>Daromadingiz:</b> {ress["income_total"]} so\'m',
                               parse_mode='HTML')
    elif response.status_code == 404:
        await message.answer(f"Quyidagi sayt orqali ro'yxatdan o'tib maxsus kodni yuboring", reply_markup=Registration)
        await state.set_state('activation')


@dp.message_handler(text='💰Kassa', state=['check','confirmation', 'order', 'time', None])
async def send_profit(message: Message, state: FSMContext):
    user_id = message.from_user.id
    url = f"{BASE_URL}driver-balance/"

    payload = {}
    headers = {
        'MyToken': f'{MY_TOKEN}',
        'ChatId': str(user_id)
    }

    response = requests.request("GET", url, headers=headers, data=payload)

    ress = response.json()
    await bot.send_message(message.from_user.id, f'<b>Olingan mahsulotlar summasi:</b> {ress["balance"]} so\'m',
                           parse_mode='HTML')


@dp.message_handler(text='📊Tarix', state=['check', 'order', 'time', None])
async def send_history(message: Message, state: FSMContext):
    user_id = message.from_user.id
    url = f"{BASE_URL}driver-history/"

    payload = {}
    headers = {
        'MyToken': f'{MY_TOKEN}',
        'ChatId': str(user_id)
    }

    response = requests.request("GET", url, headers=headers, data=payload)

    res = response.json()
    text = f"<b>🏷Qabul qilingan:</b> {res['accepted']} ta\n" \
           f"<b>🚚Yetkazilmoqda:</b> {res['being_delivered']} ta\n" \
           f"<b>📌Yetkazilgan:</b> {res['delivered']} ta\n" \
           f"<b>❌Bekor qilingan:</b> {res['canceled']} ta\n" \
           f"<b>☎️Qayta qo'ng'iroq:</b> {res['call_back']} ta\n" \
           f"<b>⏱Kutilmoqda:</b> {res['wait']} ta"
    await bot.send_message(message.from_user.id, text,
                           parse_mode='HTML')


@dp.message_handler(text='⬅️Ortga')
async def back_menu(message: Message, state: FSMContext):
    await bot.send_message(message.from_user.id, 'Bosh sahifa', reply_markup=menu)
