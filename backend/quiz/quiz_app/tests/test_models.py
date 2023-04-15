from django.http import Http404
from django.test import TestCase
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import Group
from ..models import User, Quiz, Question, Answer


class UserModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        Group.objects.create(name='testgroup')
        cls.user = User.objects.create(username='testuser', password='password', is_staff=True)
        cls.params_set = {
            'tg_id': ('ID в телеграмме', 20),
            'phone': ('Телефон', 30),
        }

    def test_labels(self):
        for name, params in self.params_set.items():
            with self.subTest(name=name, label=params[0]):
                field_label = self.user._meta.get_field(name).verbose_name
                self.assertEquals(field_label, params[0])

    def test_max_length(self):
        for name, params in self.params_set.items():
            with self.subTest(name=name, max_length=params[1]):
                max_length = self.user._meta.get_field(name).max_length
                self.assertEquals(max_length, params[1])

    def test_add_user_to_group(self):
        user2=User.objects.create(username='testuser2', password='password2')
        self.assertTrue(self.user.groups.filter(id=1).exists())
        self.assertFalse(user2.groups.filter(id=1).exists())


class QuizModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        test_user = User.objects.create(username='testuser', password='password')
        cls.quiz = Quiz.objects.create(user=test_user, title='Test quiz')
        cls.label_set = {
            'user': 'Автор',
            'title': 'Название квиза',
            'send_results_type': 'Тип отправки результатов',
            'is_send_name': 'Отправка имени',
            'is_send_email': 'Отправка email',
            'is_send_phone': 'Отправка телефона',
        }
        cls.default_fields = {
            'send_results_type': 'TG',
            'is_send_name': False,
            'is_send_email': False,
            'is_send_phone': False,
        }
        cls.send_types = [
            ("TG", 'В телеграмм'),
            ("SMS", 'По SMS'),
            ("TG-SMS", 'В телеграмм и по SMS'),
        ]

    def test_labels(self):
        for name, label in self.label_set.items():
            with self.subTest(name=name, label=label):
                field_label = self.quiz._meta.get_field(name).verbose_name
                self.assertEquals(field_label, label)

    def test_default(self):
        for name, value in self.default_fields.items():
            with self.subTest(name=name, value=value):
                field_value = self.quiz.__getattribute__(name)
                self.assertEquals(field_value, value)

    def test_title_max_length(self):
        max_length = self.quiz._meta.get_field('title').max_length
        self.assertEquals(max_length, 500)

    def test_send_results_choices(self):
        choices = self.quiz._meta.get_field('send_results_type').choices
        self.assertEquals(choices, self.send_types)

    def test_object_str_name(self):
        expected_object_name = '%s' % self.quiz.title
        self.assertEquals(expected_object_name, str(self.quiz))

    def test_model_name(self):
        model_name = self.quiz._meta.verbose_name
        self.assertEquals(model_name, 'Квиз')


class QuestionModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        test_user = User.objects.create(username='testuser', password='password')
        cls.test_quiz = Quiz.objects.create(user=test_user, title='Test quiz')
        cls.question = Question.objects.create(quiz=cls.test_quiz, text='Test question', number=1)
        cls.label_set = {
            'quiz': 'Квиз',
            'text': 'Вопрос',
            'number': 'Порядковый номер вопроса',
        }

    def test_labels(self):
        for name, label in self.label_set.items():
            with self.subTest(name=name, label=label):
                field_label = self.question._meta.get_field(name).verbose_name
                self.assertEquals(field_label, label)

    def test_text_max_length(self):
        max_length = self.question._meta.get_field('text').max_length
        self.assertEquals(max_length, 5000)

    def test_delete_cascade(self):
        self.test_quiz.delete()
        with self.assertRaises(Http404) as context:
            get_object_or_404(Question, pk=1)
        self.assertTrue('No Question matches the given query.' in str(context.exception))

    def test_object_str_name(self):
        expected_object_name = '%s' % self.question.text[:40]
        self.assertEquals(expected_object_name, str(self.question))

    def test_model_name(self):
        model_name = self.question._meta.verbose_name
        self.assertEquals(model_name, 'Вопрос')

    def test_constraint(self):
        self.assertIn(('quiz', 'number'), self.question._meta.unique_together)


class AnswerModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        test_user = User.objects.create(username='testuser', password='password')
        test_quiz = Quiz.objects.create(user=test_user, title='Test quiz')
        cls.test_question = Question.objects.create(quiz=test_quiz, text='Test question', number=1)
        cls.answer = Answer.objects.create(question=cls.test_question, text='Test answer', num=1, is_correct=False)
        cls.label_set = {
            'question': 'Вопрос',
            'text': 'Ответ',
            'num': 'Номер ответа',
            'is_correct': 'Правильный',
        }

    def test_labels(self):
        for name, label in self.label_set.items():
            with self.subTest(name=name, label=label):
                field_label = self.answer._meta.get_field(name).verbose_name
                self.assertEquals(field_label, label)

    def test_text_max_length(self):
        max_length = self.answer._meta.get_field('text').max_length
        self.assertEquals(max_length, 500)

    def test_delete_cascade(self):
        self.test_question.delete()
        with self.assertRaises(Http404) as context:
            get_object_or_404(Answer, pk=1)
        self.assertTrue('No Answer matches the given query.' in str(context.exception))

    def test_object_str_name(self):
        expected_object_name = '%s' % self.answer.text[:40]
        self.assertEquals(expected_object_name, str(self.answer))

    def test_model_name(self):
        model_name = self.answer._meta.verbose_name
        self.assertEquals(model_name, 'Ответ')

    def test_constraint(self):
        self.assertIn(('question', 'num'), self.answer._meta.unique_together)
