import urllib

import requests
from aiogram import Bot
from aiogram.dispatcher import FSMContext
from aiogram.types import Message, InputFile

from data.config import BASE_URL, MY_TOKEN, BOT_TOKEN
from handlers.users.start import check_user
from keyboards.default.main import stock_keyboard, menu
from keyboards.inline.buyurtmalar import Registration
from loader import dp

bot = Bot(token=BOT_TOKEN)


@dp.message_handler(text='🛒Ombor', state=['check', 'order','confirmation', 'time', None])
async def send_statistic(message: Message, state: FSMContext):
    user_id = message.from_user.id

    url = f"{BASE_URL}driver-store-house-list/"

    headers = {
        'MyToken': f'{MY_TOKEN}',
        'ChatId': str(user_id)
    }

    response = requests.request("GET", url, headers=headers)

    ress = response.json()
    if ress == []:
        await message.answer(
            f"Hech narsa topilmadi")

    if response.status_code == 200:
        for res in ress:
            text = f"<b>Mahsulot:</b> {res['name']}\n" \
                   f"-----------------------\n\n" \
                   f"<b>Jami:</b> {res['statistic']['total']}\n" \
                   f"<b>Qabul qilindi:</b> {res['statistic']['accepted']}\n" \
                   f"<b>Yetkazilmoqda:</b> {res['statistic']['being_delivered']}\n" \
                   f"<b>Qayta qo'ng'iroq:</b> {res['statistic']['call_back']}\n" \
                   f"<b>Zahirada:</b> {res['statistic']['stock']}\n" \
                   f"<b>Kutilmoqda:</b> {res['statistic']['wait']}"
            await bot.send_message(message.from_user.id, text, reply_markup=stock_keyboard, parse_mode='HTML')
    else:
        await message.answer(f"Quyidagi sayt orqali ro'yxatdan o'tib maxsus kodni yuboring", reply_markup=Registration)
        await state.set_state('activation')

@dp.message_handler(text='🖨Excel formatda', state=['check','confirmation','order', 'time', None])
async def send_excel(message: Message, state: FSMContext):
    user_id = message.from_user.id
    url = f"{BASE_URL}driver-store-house-excel/"

    payload = {}
    headers = {
        'MyToken': f'{MY_TOKEN}',
        'ChatId': str(user_id)
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    ress = response.json()
    dls = ress['url']
    urllib.request.urlretrieve(dls, "documents/stock.xlsx")
    file_id = InputFile(path_or_bytesio="documents/stock.xlsx")
    await bot.send_document(message.from_user.id, file_id)


@dp.message_handler(text='⬅️Ortga')
async def back_menu(message: Message, state: FSMContext):
    await bot.send_message(message.from_user.id, 'Bosh sahifa', reply_markup=menu)
