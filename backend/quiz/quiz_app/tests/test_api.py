from django.test import TestCase
from unittest.mock import patch
from rest_framework.test import APITestCase, APIRequestFactory, APIClient
from ..models import User, Quiz
from ..api import QuizViewSet, ResultViewSet
from ..serializers import QuizResultSerializer


class QuizViewSetTest(APITestCase):

    @classmethod
    def setUpTestData(cls):
        number_of_quizzes = 5
        cls.test_user = User.objects.create(username='testuser', password='password')
        for quiz_num in range(number_of_quizzes):
            Quiz.objects.create(user=cls.test_user, title='Test quiz %s' % quiz_num)

    def test_url_quiz_list_exists(self):
        resp = self.client.get('/api/quizzes/')
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(len(resp.data) == 5)
        self.assertEqual(resp.data[0], {'id': 1, 'title': 'Test quiz 0'})

    def test_url_quiz_list_data(self):
        resp = self.client.get('/api/quizzes/')
        self.assertTrue(len(resp.data) == 5)
        self.assertEqual(resp.data[0], {'id': 1, 'title': 'Test quiz 0'})

    def test_url_quiz_detail_exists(self):
        test_quiz = Quiz.objects.first()
        resp_detail = self.client.get('/api/quizzes/{}/'.format(test_quiz.pk))
        self.assertEqual(resp_detail.status_code, 200)

    def test_url_quiz_detail_data(self):
        test_quiz = Quiz.objects.first()
        resp_detail = self.client.get('/api/quizzes/{}/'.format(test_quiz.pk))
        self.assertEqual(resp_detail.data,
                         {'id': test_quiz.id, 'questions': [], 'title': test_quiz.title, 'is_send_name': False,
                          'is_send_email': False, 'is_send_phone': False, 'user': 1}
                         )

    def test_list_view(self):
        view = QuizViewSet.as_view({'get': 'list'})
        request = APIRequestFactory().get('/api/quizzes/')
        response = view(request)
        self.assertEqual(response.data,
                         [{'id': 1, 'title': 'Test quiz 0'}, {'id': 2, 'title': 'Test quiz 1'},
                          {'id': 3, 'title': 'Test quiz 2'}, {'id': 4, 'title': 'Test quiz 3'},
                          {'id': 5, 'title': 'Test quiz 4'}])

    def test_detail_view(self):
        view = QuizViewSet.as_view({'get': 'retrieve'})
        request = APIRequestFactory().get('/api/quizzes/5')
        response = view(request, pk='5')
        self.assertEqual(response.data,
                         {'id': 5, 'questions': [], 'title': 'Test quiz 4', 'is_send_name': False,
                          'is_send_email': False, 'is_send_phone': False, 'user': 1})

    def test_permissions(self):
        client = APIClient()
        resp_not_auth_1 = client.get('/api/quizzes/1/')
        resp_not_auth_2 = client.put('/api/quizzes/1/', data={'title': 'Edited test quiz'})
        self.assertTrue(resp_not_auth_1.status_code == 200)
        self.assertFalse(resp_not_auth_2.status_code == 200)

        client.force_authenticate(user=self.test_user)
        resp_auth = client.put('/api/quizzes/1/', data={'title': 'Edited test quiz'})
        self.assertEqual(resp_auth.status_code, 200)


class ResultViewSetTest(APITestCase):

    @classmethod
    def setUpTestData(cls):
        cls.results = [{'question': 1, 'answer': 'test answer 1'}, {'question': 2, 'answer': 'test answer 2'}]
        cls.contacts = {'name': 'testname', 'email': 'test@tt.com'}
        test_user = User.objects.create(username='testuser', password='password', tg_id='5187812315')
        cls.quiz = Quiz.objects.create(user=test_user, title='Test quiz')
        cls.invalid_data = [{},
                            {'quiz': cls.quiz.id},
                            {'results': []},
                            {'quiz': 'quiz', 'results': []},
                            {'quiz': cls.quiz.id, 'results': 'res'},
                            {'quiz': cls.quiz.id, 'results': [], 'contacts':'contacts'},
                            {'quiz': cls.quiz.id, 'results': {}, 'contacts': {}},
                            {'quiz': {}, 'results': [], 'contacts': {}},
                            {'quiz': cls.quiz.id, 'results': [{'question':'ques','answer':'ans'}], 'contacts': {}},
                            {'quiz': cls.quiz.id, 'results': [{'question':1}], 'contacts': {}},
                            {'quiz': cls.quiz.id, 'results': [{'question':1, 'answer':'ans'}], 'contacts': {'name':[]}},
                            {'quiz': cls.quiz.id, 'results': [], 'contacts': {'email': {}}},
                            {'quiz': cls.quiz.id, 'results': [], 'contacts': {'name': 'olala','phone':[]}}]

    def test_url_results_exists(self):
        resp = self.client.post('/api/results/', data={'quiz': 1, 'results': []})
        self.assertEqual(resp.status_code, 200)

    def test_view(self):
        view = ResultViewSet.as_view({'post': 'create'})
        request = APIRequestFactory().post('/api/results/', data={'quiz': self.quiz.id, 'results': []}, format='json')
        response = view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, 'ok')

    def test_valid_post_data(self):
        resp = self.client.post('/api/results/', data={'quiz': self.quiz.id, 'results': self.results,
                                                       'contacts': self.contacts}, format='json')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data, 'ok')

        self.assertRaises(Exception, self.client.post('/api/results/', data={'quiz': self.quiz.id, 'results': []}, format='json'))

        for data in self.invalid_data:
            with self.subTest(data=data):
                resp = self.client.post('/api/results/', data=data, format='json')
                self.assertEqual(resp.status_code, 200)
                serializer = QuizResultSerializer(data=data)
                serializer.is_valid()
                self.assertEqual(resp.data, serializer.errors)

    def test_call_send_results(self):
        with patch('quiz_app.api.send_results') as mock_send_results:
            resp = self.client.post('/api/results/', data={'quiz': self.quiz.id, 'results': self.results,
                                                           'contacts': self.contacts}, format='json')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data, 'ok')
        mock_send_results.assert_called_with(self.quiz, self.results, self.contacts)


