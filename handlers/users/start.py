import requests
from aiogram import types, Bot
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.builtin import CommandStart, Command

from data.config import BASE_URL, BOT_TOKEN, MY_TOKEN
from keyboards.default.main import menu
from keyboards.inline.buyurtmalar import get_region, Registration
from loader import dp

bot = Bot(token=BOT_TOKEN)


async def check_user(user_id):
    url = f"{BASE_URL}all-orders/"

    payload = {}
    headers = {
        'MyToken': f'{MY_TOKEN}',
        'ChatId': str(user_id)
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    return response.status_code


@dp.message_handler(CommandStart(), state=['check', 'order', 'time', 'activation', 'aktivlashtirish', None])
async def bot_start(message: types.Message, state: FSMContext):
    chat_id = message.from_user.id
    result = await check_user(chat_id)
    if result == 200:
        await message.answer("Xush kelibsiz", reply_markup=menu)
    else:
        await message.answer(f"Quyidagi sayt orqali ro'yxatdan o'tib maxsus kodni yuboring", reply_markup=Registration)
        await state.set_state('activation')


@dp.message_handler(Command("aktivlashtirish"), state=['check', 'order', 'time', 'activation', 'aktivlashtirish', None])
async def bot_activation(message: types.Message, state: FSMContext):
    await message.answer(f"Quyidagi sayt orqali ro'yxatdan o'tib maxsus kodni yuboring", reply_markup=Registration)
    await state.set_state('activation')


@dp.message_handler(state=['activation'])
async def bot_activate(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    token = message.text
    if token.isdigit():
        url = f"{BASE_URL}activation/"

        payload = {'chat_id': str(user_id),
                   'token': token
                   }
        headers = {
            'MyToken': MY_TOKEN
        }

        response = requests.request("POST", url, headers=headers, data=payload)
        res = response.json()
        if res['status'] == 200:
            await message.answer("Xush kelibsiz", reply_markup=menu)
            await state.finish()
        else:
            await bot.send_message(user_id, "Kod xato!\nIltimos tekshirib qaytadan harakat qilib ko'ring")
    else:
        await bot.send_message(user_id, "Kod xato!\nIltimos tekshirib qaytadan harakat qilib ko'ring")
