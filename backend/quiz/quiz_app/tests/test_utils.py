from unittest import TestCase
from unittest.mock import patch
from ..api import send_results
from ..models import User, Quiz


class TestUtils(TestCase):
    @classmethod
    def setUpClass(cls):
        test_user1 = User.objects.create(username='testuser1', password='password1', tg_id='5187812315',
                                         phone='375447215278')
        test_user2 = User.objects.create(username='testuser2', password='password2', tg_id='5187812315',
                                         phone='3754472')
        cls.test_user1 = test_user1
        cls.test_user2 = test_user2
        cls.quiz_send_set = {
            1: (test_user1, 'TG', 1, 0),
            2: (test_user1, 'SMS', 0, 1),
            3: (test_user1, 'TG-SMS', 1, 1),
            4: (test_user2, 'SMS', 1, 1),
        }

    def test_send_results(self):
        results = [{'question': 1, 'answer': 'test answer'}]
        contacts = None

        for num, params in self.quiz_send_set.items():
            with self.subTest(user=params[0], send_type=params[1]):
                quiz = Quiz.objects.create(user=params[0], title='Test quiz %s' % num, send_results_type=params[1])
                with patch('quiz_app.api.send_results_tg') as mock_send_tg:
                    send_results(quiz, results, contacts)
                with patch('quiz_app.api.send_results_sms') as mock_send_sms:
                    send_results(quiz, results, contacts)
                self.assertEqual(mock_send_tg.call_count, params[2])
                self.assertEqual(mock_send_sms.call_count, params[3])

    def test_args_to_send(self):
        quiz1 = Quiz.objects.create(user=self.test_user1, title='Test quiz', send_results_type='TG-SMS',
                                   is_send_name=True, is_send_email=True)
        quiz2 = Quiz.objects.create(user=self.test_user2, title='Test quiz incorrect', send_results_type='SMS',
                                    is_send_name=True, is_send_email=True)
        results = [{'question': 1, 'answer': 'test answer 1'}, {'question': 2, 'answer': 'test answer 2'}]
        contacts = {'name': 'testname', 'email': 'test@tt.com'}

        # send_results_tg.assert_called()
        with patch('quiz_app.api.send_results_tg') as mock_send_tg, patch('quiz_app.api.send_results_sms') as mock_send_sms:
            send_results(quiz1, results, contacts)
        message1 = 'Результаты прохождения квиза "Test quiz":\n\n1. test answer 1\n2. test answer 2\n\nДанные участника:' \
                   '\nИмя - Testname\nEmail - test@tt.com\n'
        mock_send_tg.assert_called_with('5187812315', message1)
        mock_send_sms.assert_called_with(message1, '375447215278')

        with patch('quiz_app.api.send_results_tg') as mock_send_tg:
            send_results(quiz2, results, contacts)
        with patch('quiz_app.api.send_results_sms') as mock_send_sms:
            send_results(quiz2, results, contacts)

        message2 = 'Результаты прохождения квиза "Test quiz incorrect":\n\n1. test answer 1\n2. test answer 2\n\nДанные участника:' \
                   '\nИмя - Testname\nEmail - test@tt.com\n'
        mess_error = 'В сервисе квизов в Вашем аккаунте указан некорректный телефонный номер. Внесите изменения, пожалуйста'

        mock_send_sms.assert_called_with(message2, '3754472')
        mock_send_tg.assert_called_with('5187812315', mess_error)
