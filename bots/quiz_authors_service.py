from aiogram import Bot, types, executor
from aiogram.dispatcher import Dispatcher, FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import re
import aiohttp
from bot_config import TOKEN
import logging

logging.basicConfig(level=logging.INFO)

storage = MemoryStorage()
bot = Bot(token=TOKEN, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot, storage=storage)


class QuizAuthorCreate(StatesGroup):
    set_username = State()
    set_password = State()
    confirm_password = State()
    set_phone = State()
    confirm = State()


def create_keyboard(k):
    keyboard = types.InlineKeyboardMarkup()
    back_btn = types.InlineKeyboardButton(text="Начать заново", callback_data='back')
    quiz_admin_btn = types.InlineKeyboardButton(text="Перейти к работе над квизами", url='http://127.0.0.1:8000/admin')
    if k == 'main':
        register_btn = types.InlineKeyboardButton(text="Зарегистрироваться", callback_data='register')
        keyboard.add(register_btn)
        keyboard.add(quiz_admin_btn)
    elif k == 'back':
        keyboard.add(back_btn)
    elif k == 'go_to_confirm':
        without_phone_btn = types.InlineKeyboardButton(text="Не желаю", callback_data='without_phone')
        keyboard.add(without_phone_btn)
        keyboard.add(back_btn)
    elif k == 'confirm':
        conf_btn = types.InlineKeyboardButton(text="Подтвердить", callback_data='ok')
        keyboard.add(conf_btn)
        keyboard.add(back_btn)
    return keyboard


def create_message(data):
    to_send_message = '<b>Ваши данные:</b>\nИмя пользователя - ' + data.get('username') + '\nПароль - ' + data.get('password')
    if data.get('phone'):
        to_send_message += '\nТелефон - ' + data.get('phone')
    to_send_message += '\n\nЕсли все верно, подтвердите'
    return to_send_message


async def user_register(data):
    url = "http://127.0.0.1:8000/auth/users/"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=data) as resp:
                print("Status:", resp.status)
                resp_json = await resp.json()
                print(resp_json)
                return resp.status, resp_json
    except Exception as error:
        print(error)
        return ('error',)


@dp.message_handler(commands=['start'], state='*')
async def start_bot(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer('Здравствуйте, здесь вы можете зарегистрироваться в сервисе по созданию квизов, став одним '
                         'из наших авторов, и перейти к работе', reply_markup=create_keyboard('main'))


@dp.message_handler(state=QuizAuthorCreate.set_username)
async def define_username(message: types.Message, state: FSMContext):
    await state.update_data(username=message.text)
    await message.answer('👇 Введите пароль', reply_markup=create_keyboard('back'))
    await QuizAuthorCreate.next()


@dp.message_handler(state=QuizAuthorCreate.set_password)
async def define_password(message: types.Message, state: FSMContext):
    pattern_password = re.compile(r'^(?=.*[0-9].*)(?=.*[a-z].*)(?=.*[A-Z].*)[0-9a-zA-Z]{8,}$')
    if pattern_password.match(message.text):
        await state.update_data(password=message.text)
        await QuizAuthorCreate.next()
        mess = '👇 Подтвердите пароль'
    else:
        mess = 'Пароль должен содержать хотя бы одну цифру, строчную и заглавную латинскую букву и состоять минимум из ' \
               '8 символов.\nВведите корректный пароль'
    await message.answer(mess, reply_markup=create_keyboard('back'))
    await message.delete()


@dp.message_handler(state=QuizAuthorCreate.confirm_password)
async def confirm_password(message: types.Message, state: FSMContext):
    data = await state.get_data()
    password = data.get('password')
    if message.text == password:
        await message.answer('👇 Если желаете, введите номер телефона в формате +375xxxxxxxxx, по которому будут '
                             'приходить SMS с результатами прохождения ваших квизов (помимо сообщений в телеграмме',
                             reply_markup=create_keyboard('go_to_confirm'))
        await QuizAuthorCreate.next()
    else:
        await message.answer('👇 Пароли не совпадают, введите пароль заново', reply_markup=create_keyboard('back'))
        await QuizAuthorCreate.previous()
    await message.delete()


@dp.message_handler(state=QuizAuthorCreate.set_phone)
async def define_phone(message: types.Message, state: FSMContext):
    await state.update_data(phone=message.text)
    data = await state.get_data()
    data_msg = await message.answer(create_message(data), reply_markup=create_keyboard('confirm'))
    await state.update_data(msg=data_msg)
    await QuizAuthorCreate.next()


@dp.callback_query_handler(lambda call: call.data == 'without_phone', state=QuizAuthorCreate.set_phone)
async def without_phone(call: types.CallbackQuery, state: FSMContext):
    if call.message:
        await bot.answer_callback_query(call.id)
        data = await state.get_data()
        data_msg = await bot.send_message(
            chat_id=call.message.chat.id,
            text=create_message(data),
            reply_markup=create_keyboard('confirm')
        )
        await state.update_data(msg=data_msg)
        await QuizAuthorCreate.next()


@dp.callback_query_handler(lambda call: call.data == 'ok', state=QuizAuthorCreate.confirm)
async def make_registration(call: types.CallbackQuery, state: FSMContext):
    if call.message:
        await bot.answer_callback_query(call.id)
        data = await state.get_data()
        await data['msg'].delete()
        # data['msg'] = None
        data['tg_id'] = call.message.chat.id
        data['is_staff'] = True
        data.pop('msg')
        print(data)
        result = await user_register(data)
        if result[0] == 201:
            msg = 'Поздравляем! Регистрация прошла успешно!\nМожете приступать к работе.\n\n' \
                  'И вступите, пожалуйста, в коммуникацию с ботом, который по Вашему желанию будет присылать результаты ' \
                  'прохождения Ваших квизов\nhttp://t.me/quiz_results_sender_bot'
        elif result[0] == 400 and result[1]['username'][0] == "Пользователь с таким именем уже существует.":
            msg = 'Пользователь с таким именем уже существует,\nпопробуйте сначала'
        else:
            msg = 'Что-то пошло не так, попробуйте сначала'

        await bot.send_message(
            chat_id=call.message.chat.id,
            text=msg,
            reply_markup=create_keyboard('main')
        )
        await state.finish()


@dp.callback_query_handler(lambda call: True, state='*')
async def keyboard_answer(call: types.CallbackQuery, state: FSMContext):
    if call.message:
        await bot.answer_callback_query(call.id)
        if call.data == "register":
            await state.finish()
            await QuizAuthorCreate.set_username.set()
            await bot.send_message(
                chat_id=call.message.chat.id,
                text='👇 Введите имя пользователя латиницей',
                reply_markup=create_keyboard('back'))
        elif call.data == "back":
            await state.finish()
            await bot.send_message(
                chat_id=call.message.chat.id,
                text='👇 Сделайте свой выбор',
                reply_markup=create_keyboard('main'))


if __name__ == "__main__":
    executor.start_polling(dp)
