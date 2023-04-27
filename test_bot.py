import unittest
from unittest import IsolatedAsyncioTestCase
from aiogram_unittest import Requester
from aiogram_unittest.handler import CallbackQueryHandler
from aiogram_unittest.handler import MessageHandler
from aiogram_unittest.types.dataset import CALLBACK_QUERY
from aiogram_unittest.types.dataset import MESSAGE, CHAT

from bots.quiz_authors_service import create_keyboard, start_bot, define_username, define_password, confirm_password, \
    define_phone, without_phone, make_registration, keyboard_answer, QuizAuthorCreate


class TestBot(IsolatedAsyncioTestCase):
    @classmethod
    def setUpClass(cls):
        cls.text_set = {
            'test_user88': {'username': ('Введите пароль', 'QuizAuthorCreate:set_password'),
                            'password': ('Введите корректный пароль', 'QuizAuthorCreate:set_password'),
                            'phone': ('Введите корректный', 'QuizAuthorCreate:set_phone')},
            'Test5test!!': {'username': ('Введите корректное имя', 'QuizAuthorCreate:set_username'),
                            'password': ('Подтвердите пароль', 'QuizAuthorCreate:confirm_password'),
                            'phone': ('Введите корректный', 'QuizAuthorCreate:set_phone')},
            'test!77777': {'username': ('Введите корректное имя', 'QuizAuthorCreate:set_username'),
                           'password': ('Введите корректный пароль', 'QuizAuthorCreate:set_password'),
                           'phone': ('Введите корректный', 'QuizAuthorCreate:set_phone')},
            '375441111111': {'username': ('Введите пароль', 'QuizAuthorCreate:set_password'),
                             'password': ('Введите корректный пароль', 'QuizAuthorCreate:set_password'),
                             'phone': ('Ваши данные', 'QuizAuthorCreate:confirm')},
            'T&37529222': {'username': ('Введите корректное имя', 'QuizAuthorCreate:set_username'),
                           'password': ('Введите корректный пароль', 'QuizAuthorCreate:set_password'),
                           'phone': ('Введите корректный', 'QuizAuthorCreate:set_phone')},
        }

    async def test_start_bot(self):
        requester = Requester(request_handler=MessageHandler(start_bot, commands=["start"]))
        message = MESSAGE.as_object(text="/start")
        calls = await requester.query(message)
        answer_message = calls.send_message.fetchone()
        self.assertEqual(answer_message.text,
                         "Здравствуйте, здесь вы можете зарегистрироваться в сервисе по созданию квизов, став одним из "
                         "наших авторов, и перейти к работе")
        self.assertEqual(answer_message.reply_markup, create_keyboard('main'))

    async def test_define_username(self):
        requester = Requester(request_handler=MessageHandler(define_username, state=QuizAuthorCreate.set_username))
        for text, result in self.text_set.items():
            with self.subTest(text=text, result=result['username']):
                message = MESSAGE.as_object(text=text)
                calls = await requester.query(message)
                answer_message = calls.send_message.fetchone()
                self.assertIn(result['username'][0], answer_message.text)
                self.assertEqual(answer_message.reply_markup, create_keyboard('back'))
                state_now = await requester._handler.dp.current_state().get_state()
                self.assertEqual(state_now, result['username'][1])

    async def test_define_password(self):
        requester = Requester(request_handler=MessageHandler(define_password, state=QuizAuthorCreate.set_password))
        for text, result in self.text_set.items():
            with self.subTest(text=text, result=result['password']):
                message = MESSAGE.as_object(text=text)
                calls = await requester.query(message)
                answer_message = calls.send_message.fetchone()
                self.assertIn(result['password'][0], answer_message.text)
                self.assertEqual(answer_message.reply_markup, create_keyboard('back'))
                state_now = await requester._handler.dp.current_state().get_state()
                self.assertEqual(state_now, result['password'][1])

    async def test_confirm_password(self):
        requester = Requester(request_handler=MessageHandler(confirm_password, state=QuizAuthorCreate.confirm_password))
        await requester._handler.dp.current_state().set_data({'password': 'Password9!'})
        password_set = {
            'Password9!': ('номер мобильного телефона', 'go_to_confirm', 'QuizAuthorCreate:set_phone'),
            'passWord%5': ('Пароли не совпадают', 'back', 'QuizAuthorCreate:set_password'),
        }
        for password, result in password_set.items():
            with self.subTest(password=password, result=result):
                message = MESSAGE.as_object(text=password)
                calls = await requester.query(message)
                answer_message = calls.send_message.fetchone()
                self.assertIn(result[0], answer_message.text)
                self.assertEqual(answer_message.reply_markup, create_keyboard(result[1]))
                state_now = await requester._handler.dp.current_state().get_state()
                self.assertEqual(state_now, result[2])

    async def test_define_phone(self):
        requester = Requester(request_handler=MessageHandler(define_phone, state=QuizAuthorCreate.set_phone))
        await requester._handler.dp.current_state().set_data({'username': 'test_user', 'password': 'Password9!'})
        for text, result in self.text_set.items():
            with self.subTest(text=text, result=result['phone']):
                message = MESSAGE.as_object(text=text)
                calls = await requester.query(message)
                answer_message = calls.send_message.fetchone()
                self.assertIn(result['phone'][0], answer_message.text)
                state_now = await requester._handler.dp.current_state().get_state()
                self.assertEqual(state_now, result['phone'][1])

        message = MESSAGE.as_object(text='375295555555')
        calls = await requester.query(message)
        answer_message = calls.send_message.fetchone()
        self.assertEqual(answer_message.text,
                         '<b>Ваши данные:</b>\nИмя пользователя - test_user\nПароль - Password9!\nТелефон - +375(29) 555 55 55\n\nЕсли все верно, подтвердите')
        self.assertEqual(answer_message.reply_markup, create_keyboard('confirm'))
        new_data = await requester._handler.dp.current_state().get_data()
        self.assertIn('msg', new_data)

    async def test_without_phone(self):
        requester = Requester(
            request_handler=CallbackQueryHandler(without_phone, state=QuizAuthorCreate.set_phone)
        )
        await requester._handler.dp.current_state().set_data({'username': 'test_user', 'password': 'Password9!'})
        callback_query = CALLBACK_QUERY.as_object(data="without_phone", message=MESSAGE.as_object())
        calls = await requester.query(callback_query)
        answer_message = calls.send_message.fetchone()

        self.assertEqual(answer_message.text,
                         '<b>Ваши данные:</b>\nИмя пользователя - test_user\nПароль - Password9!\n\nЕсли все верно, подтвердите')
        self.assertEqual(answer_message.reply_markup, create_keyboard('confirm'))
        state_now = await requester._handler.dp.current_state().get_state()
        self.assertEqual(state_now, 'QuizAuthorCreate:confirm')
        new_data = await requester._handler.dp.current_state().get_data()
        self.assertIn('msg', new_data)

    # @unittest.skip('already tested')
    async def test_make_registration(self):
        requester = Requester(
            request_handler=CallbackQueryHandler(make_registration, state=QuizAuthorCreate.confirm)
        )
        user_set = {
            'user_ttest': 'Поздравляем',
            'test_test_user': 'уже существует',
        }
        for username, result in user_set.items():
            with self.subTest(username=username, result=result):
                await requester._handler.dp.current_state().set_data({'username': username, 'password': 'Password9!'})
                callback_query = CALLBACK_QUERY.as_object(data="ok", message=MESSAGE.as_object(chat=CHAT.as_object()))
                calls = await requester.query(callback_query)
                answer_message = calls.send_message.fetchone()
                self.assertIn(result, answer_message.text)
                self.assertEqual(answer_message.reply_markup, create_keyboard('main'))
                state_now = await requester._handler.dp.current_state().get_state()
                self.assertEqual(state_now, None)

    async def test_keyboard_answer(self):
        requester = Requester(
            request_handler=CallbackQueryHandler(keyboard_answer, state="*")
        )
        call_set = {
            'register': ('Введите имя пользователя', 'back', 'QuizAuthorCreate:set_username'),
            'back': ('Сделайте свой выбор', 'main', None),
        }

        for call_data, result in call_set.items():
            with self.subTest(call_data=call_data, result=result):
                callback_query = CALLBACK_QUERY.as_object(data=call_data, message=MESSAGE.as_object())
                calls = await requester.query(callback_query)
                answer_message = calls.send_message.fetchone()
                self.assertIn(result[0], answer_message.text)
                self.assertEqual(answer_message.reply_markup, create_keyboard(result[1]))
                state_now = await requester._handler.dp.current_state().get_state()
                self.assertEqual(state_now, result[2])


if __name__ == "__main__":
    unittest.main()
