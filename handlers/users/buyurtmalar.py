import asyncio
from contextlib import suppress
from datetime import datetime
from datetime import timedelta
import requests
from aiogram import types, Bot
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command, Text, state
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.utils.exceptions import MessageCantBeDeleted, MessageToDeleteNotFound

from data.config import BASE_URL, MY_TOKEN, BOT_TOKEN
from handlers.users.start import check_user
from keyboards.default.main import filter_order, menu
from keyboards.inline.buyurtmalar import get_region, full_extra_menu, time_menu, delivering_menu, retry_call_menu, \
    confirmation_menu, Registration
from loader import dp

bot = Bot(token=BOT_TOKEN)


async def send_request(query, order_id, date, status, chat_id, state):
    url = f"{BASE_URL}change-order-status/"
    or_id = 0
    try:
        if '-' in order_id:
            or_id = order_id.split('-')[-1]
        else:
            or_id = order_id
    except:
        or_id = order_id
    payload = {'order_id': or_id,
               'date': date,
               'status': status}
    headers = {
        'MyToken': MY_TOKEN,
        'ChatId': str(chat_id)
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    res = response.json()
    await query.answer(res['message'], show_alert=True)
    await bot.send_message(chat_id, "Bo'limni tanlang", reply_markup=get_region(chat_id))
    await bot.send_message(chat_id, "Filterlash uchun quyidagi tugmalardan birini tanlang",
                           reply_markup=filter_order)
    await state.set_state("order")
    await query.message.delete()


@dp.message_handler(text='📝Buyurtmalar', state=['check', 'order', 'time', None])
async def send_link(message: Message, state: FSMContext):
    chat_id = message.from_user.id
    result = await check_user(chat_id)
    if result == 200:
        await message.reply("Bo'limni tanlang", reply_markup=get_region(chat_id))
        await bot.send_message(chat_id, "Filterlash uchun quyidagi tugmalardan birini tanlang",
                               reply_markup=filter_order)
        await state.set_state("order")
    else:
        await message.answer(f"Quyidagi sayt orqali ro'yxatdan o'tib maxsus kodni yuboring", reply_markup=Registration)
        await state.set_state('activation')


@dp.callback_query_handler(state=['order', None])
async def inline_kb_answer_callback_handler(query: types.CallbackQuery, state: FSMContext):
    answer_data = query.data
    print(answer_data)
    if "-" not in answer_data:
        user_id = query.from_user.id
        url = f"{BASE_URL}district-orders-details/"

        payload = {'district': f'{answer_data}'}
        headers = {
            'MyToken': MY_TOKEN,
            'ChatId': str(user_id)
        }

        response = requests.request("GET", url, headers=headers, data=payload)
        respons = response.json()
        if response.status_code == 200:
            if len(respons) > 0:
                for res in respons:
                    message = f"<b>Buyurtmachi ismi:</b> {res['customer_name']}\n" \
                              f"<b>Buyurtmachi tel:</b> {res['customer_phone']}\n" \
                              f"<b>Mahsulot:</b> {res['product_amount']} ta | {res['product']}\n" \
                              f"<b>Narxi:</b> {res['product_price']}\n" \
                              f"<b>Tuman:</b> {res['region']} | {res['district']}\n" \
                              f"<b>Mo'ljal:</b> {res['street']}\n" \
                              f"<b>Buyurtma sanasi:</b> {res['order_date']}\n" \
                              f"<b>Topshirish sanasi:</b> {res['delivered_date']}\n" \
                              f"<b>Daromat:</b> {res['driver_fee']}\n\n" \
                              f"<b>Holati:</b> {res['status_name']}"
                    if res['status'] == '7':  # mahsulot kutilmoqda
                        await bot.send_message(user_id, message, parse_mode="HTML")
                        await query.answer(cache_time=60)
                    elif res['status'] == '2':  # qabul qilindi
                        await bot.send_message(user_id, message, parse_mode="HTML",
                                               reply_markup=full_extra_menu(res['id']))

                        await query.answer(cache_time=60)
                    elif res['status'] == '3':  # yetkazilmoqda
                        await bot.send_message(user_id, message, parse_mode="HTML",
                                               reply_markup=delivering_menu(res['id']))

                        await query.answer(cache_time=60)
                    elif res['status'] == '4':  # yetkazib berildi
                        await bot.send_message(user_id, message, parse_mode="HTML",
                                               reply_markup=delivering_menu(res['id']))

                        await query.answer(cache_time=60)
                    elif res['status'] == '6':  # qayta qo'ng'iroq
                        await bot.send_message(user_id, message, parse_mode="HTML",
                                               reply_markup=retry_call_menu(res['id']))

                        await query.answer(cache_time=60)
                    await state.finish()
                    await state.set_state("check")
            else:
                await bot.send_message(user_id, "Ushbu bo'limda buyurtma mavjud emas")
                await state.set_state("order")
        else:
            await state.finish()
            await bot.send_message(user_id, "Xatolik mavjud!")
            await bot.send_message(user_id, "Bo'limni tanlang", reply_markup=get_region(user_id))
            await bot.send_message(user_id, "Filterlash uchun quyidagi tugmalardan birini tanlang",
                                   reply_markup=filter_order)


@dp.callback_query_handler(state=['check'])
async def callback_handlers(query: types.CallbackQuery, state: FSMContext):
    answer_data = query.data
    user_id = query.from_user.id
    if "-" not in answer_data:
        await state.finish()
        await bot.send_message(user_id, "Xatolik mavjud")
        await bot.send_message(user_id, "Bo'limni tanlang", reply_markup=get_region(user_id))
        await bot.send_message(user_id, "Filterlash uchun quyidagi tugmalardan birini tanlang",
                               reply_markup=filter_order)
    else:
        answer = answer_data.split('-')[0]
        order_id = answer_data.split('-')[1]
        date = datetime.now().date()

        if answer == 'confirm':
            await query.message.delete()
            await bot.send_message(user_id, "Siz rostdan ham buyurtmani tasdiqlamoqchimisiz?",
                                   reply_markup=confirmation_menu(order_id, 4))
            await state.set_state('confirmation')
        elif answer == 'delivering':
            await query.message.delete()
            await bot.send_message(user_id, "Siz rostdan ham buyurtma holatini o'zgartirmoqchimisiz?",
                                   reply_markup=confirmation_menu(order_id, 3))
            await state.set_state('confirmation')
        elif answer == 'cancel':
            await query.message.delete()
            await bot.send_message(user_id, "Siz rostdan ham buyurtmani bekor qilmoqchimisiz?",
                                   reply_markup=confirmation_menu(order_id, 5))
            await state.set_state('confirmation')
        elif answer == 'extratime':
            await bot.send_message(user_id, "Quyidagi vaqtlardan birini tanlang:", reply_markup=time_menu(order_id))
            await state.set_state("time")
            await query.answer(cache_time=60)
            await query.message.delete()


@dp.callback_query_handler(state=['confirmation'])
async def callback_handler(query: types.CallbackQuery, state: FSMContext):
    answer_data = query.data
    user_id = query.from_user.id

    if answer_data.count('-') == 2:
        answer = answer_data.split('-')[0]
        order_id = answer_data.split('-')[1]
        status_id = answer_data.split('-')[2]
        date = datetime.now().date()

        if answer == 'confirm':
            await send_request(query, order_id, date, status_id, user_id, state)
        elif answer == 'cancel':
            await bot.send_message(user_id, "Bo'limni tanlang", reply_markup=get_region(user_id))
            await bot.send_message(user_id, "Filterlash uchun quyidagi tugmalardan birini tanlang",
                                   reply_markup=filter_order)
            await state.set_state("order")
            await query.answer(cache_time=60)
            await query.message.delete()
    else:
        await state.finish()
        await bot.send_message(user_id, "Xatolik mavjud.")
        await bot.send_message(user_id, "Bo'limni tanlang", reply_markup=get_region(user_id))
        await bot.send_message(user_id, "Filterlash uchun quyidagi tugmalardan birini tanlang",
                               reply_markup=filter_order)


@dp.callback_query_handler(state=['time'])
async def callback_handlere(query: types.CallbackQuery, state: FSMContext):
    answer_data = query.data
    user_id = query.from_user.id
    back = answer_data.split('-')[0]

    if back == 'back':
        await bot.send_message(user_id, "Bo'limni tanlang", reply_markup=get_region(user_id))
        await bot.send_message(user_id, "Filterlash uchun quyidagi tugmalardan birini tanlang",
                               reply_markup=filter_order)
        await state.set_state("order")
        await query.answer(cache_time=60)
        await query.message.delete()
    else:
        try:
            if "-" not in answer_data:
                answer = int(answer_data.split('-')[0])
                order_id = int(answer_data.split('-')[1])
                date = datetime.now().date()
                example = date + timedelta(days=answer)
                await send_request(query, order_id, example, 6, user_id, state)
                await query.answer(cache_time=60)
                # await query.message.delete()
                await state.finish()
            else:
                await state.finish()
                await bot.send_message(user_id, "Xatolik mavjud.")
                await bot.send_message(user_id, "Bo'limni tanlang", reply_markup=get_region(user_id))
                await bot.send_message(user_id, "Filterlash uchun quyidagi tugmalardan birini tanlang",
                                       reply_markup=filter_order)
        except:
            await state.finish()
            await bot.send_message(user_id, "Xatolik mavjud.")
            await bot.send_message(user_id, "Bo'limni tanlang", reply_markup=get_region(user_id))
            await bot.send_message(user_id, "Filterlash uchun quyidagi tugmalardan birini tanlang",
                                   reply_markup=filter_order)


@dp.message_handler(text='🗞Hammasi', state=['check', 'order', 'time', None])
async def get_order(message: Message, state: FSMContext):
    user_id = message.from_user.id
    result = await check_user(user_id)
    if result == 200:
        url = f"{BASE_URL}all-orders/"

        headers = {
            'MyToken': MY_TOKEN,
            'ChatId': str(user_id)
        }

        response = requests.request("GET", url, headers=headers)
        respons = response.json()
        if len(respons) > 0:
            for res in respons:
                message = f"<b>Buyurtmachi ismi:</b> {res['customer_name']}\n" \
                          f"<b>Buyurtmachi tel:</b> {res['customer_phone']}\n" \
                          f"<b>Mahsulot:</b> {res['product_amount']} ta | {res['product']}\n" \
                          f"<b>Narxi:</b> {res['product_price']}\n" \
                          f"<b>Tuman:</b> {res['region']} | {res['district']}\n" \
                          f"<b>Mo'ljal:</b> {res['street']}\n" \
                          f"<b>Buyurtma sanasi:</b> {res['order_date']}\n" \
                          f"<b>Topshirish sanasi:</b> {res['delivered_date']}\n" \
                          f"<b>Daromat:</b> {res['driver_fee']}\n\n" \
                          f"<b>Holati:</b> {res['status_name']}"
                if res['status'] == '7':  # mahsulot kutilmoqda
                    await bot.send_message(user_id, message, parse_mode="HTML")


                elif res['status'] == '2':  # qabul qilindi
                    await bot.send_message(user_id, message, parse_mode="HTML", reply_markup=full_extra_menu(res['id']))

                elif res['status'] == '3':  # yetkazilmoqda
                    await bot.send_message(user_id, message, parse_mode="HTML", reply_markup=delivering_menu(res['id']))

                elif res['status'] == '4':  # yetkazib berildi
                    await bot.send_message(user_id, message, parse_mode="HTML", reply_markup=delivering_menu(res['id']))

                elif res['status'] == '6':  # qayta qo'ng'iroq
                    await bot.send_message(user_id, message, parse_mode="HTML", reply_markup=retry_call_menu(res['id']))
                await state.finish()
                await state.set_state("check")
        else:
            await bot.send_message(user_id, "Ushbu bo'limda buyurtma mavjud emas")
            await state.set_state("order")
    else:
        await message.answer(f"Quyidagi sayt orqali ro'yxatdan o'tib maxsus kodni yuboring", reply_markup=Registration)
        await state.set_state('activation')


@dp.message_handler(text='📌Qabul qilinganlar', state=['check', 'order', 'time', None])
async def get_filtered(message: Message, state: FSMContext):
    user_id = message.from_user.id
    url = f"{BASE_URL}new-orders/"

    headers = {
        'MyToken': MY_TOKEN,
        'ChatId': str(user_id)
    }

    response = requests.request("GET", url, headers=headers)
    respons = response.json()
    if len(respons) > 0:
        for res in respons:
            message = f"<b>Buyurtmachi ismi:</b> {res['customer_name']}\n" \
                      f"<b>Buyurtmachi tel:</b> {res['customer_phone']}\n" \
                      f"<b>Mahsulot:</b> {res['product_amount']} ta | {res['product']}\n" \
                      f"<b>Narxi:</b> {res['product_price']}\n" \
                      f"<b>Tuman:</b> {res['region']} | {res['district']}\n" \
                      f"<b>Mo'ljal:</b> {res['street']}\n" \
                      f"<b>Buyurtma sanasi:</b> {res['order_date']}\n" \
                      f"<b>Topshirish sanasi:</b> {res['delivered_date']}\n" \
                      f"<b>Daromat:</b> {res['driver_fee']}\n\n" \
                      f"<b>Holati:</b> {res['status_name']}"
            if res['status'] == '7':  # mahsulot kutilmoqda
                await bot.send_message(user_id, message, parse_mode="HTML")


            elif res['status'] == '2':  # qabul qilindi
                await bot.send_message(user_id, message, parse_mode="HTML", reply_markup=full_extra_menu(res['id']))

            elif res['status'] == '3':  # yetkazilmoqda
                await bot.send_message(user_id, message, parse_mode="HTML", reply_markup=delivering_menu(res['id']))

            elif res['status'] == '4':  # yetkazib berildi
                await bot.send_message(user_id, message, parse_mode="HTML", reply_markup=delivering_menu(res['id']))

            elif res['status'] == '6':  # qayta qo'ng'iroq
                await bot.send_message(user_id, message, parse_mode="HTML", reply_markup=retry_call_menu(res['id']))
            await state.finish()
            await state.set_state("check")
    else:
        await bot.send_message(user_id, "Qabul qilingan buyurtmalar mavjud emas")
        await state.set_state("order")


@dp.message_handler(text='⬅️Ortga', state=['check', 'order', 'time', None])
async def back_menu(message: Message, state: FSMContext):
    await bot.send_message(message.from_user.id, 'Bosh sahifa', reply_markup=menu)
