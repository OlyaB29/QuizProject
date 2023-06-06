from rest_framework.response import Response
from rest_framework import viewsets, permissions
from .models import Quiz
from .serializers import QuizSerializer, QuizDetailSerializer, QuizResultSerializer
from . import validators
from .senders.tg_sender import send_results_tg
from .senders.sms_sender import send_results_sms
import redis
from datetime import date
from django.conf import settings
from django.core.cache import cache
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from .redis_conf import PASSWORD

CACHE_TTL = getattr(settings, 'CACHE_TTL', DEFAULT_TIMEOUT)

redis_client = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0, password=PASSWORD)


def form_message(quiz, results, contacts, lead_quizzes):
    message = f'Результаты прохождения квиза "{quiz.title}":\n\n'
    for res in results:
        message += '{}. {}\n'.format(res['question'], res['answer'])
    if contacts:
        message += '\nДанные участника:\n'
        if 'name' in contacts:
            message += 'Имя - {}\n'.format(validators.validate_name(contacts['name']))
        if 'email' in contacts:
            message += 'Email - {}\n'.format(validators.validate_email(contacts['email']))
        if 'phone' in contacts:
            message += 'Телефон - {}\n'.format(contacts['phone'] if validators.validate_phone(contacts['phone']) else 'не определен')
    message += 'Лидеры среди Ваших квизов сегодня (пройдено раз: {}):\n'.format(lead_quizzes[0][1])
    for quiz in lead_quizzes:
        message += '{}\n'.format(quiz[0]['title'])
    return message


def send_results(quiz, results, contacts):
    msg = form_message(quiz, results, contacts, save_to_redis(quiz))

    if "TG" in quiz.send_results_type:
        send_results_tg(quiz.user.tg_id, msg)
    if "SMS" in quiz.send_results_type and quiz.user.phone:
        resp = send_results_sms(msg, quiz.user.phone)
        print(resp)
        if 'error' in resp:
            if resp['error'] == 'incorrect phone number':
                send_results_tg(quiz.user.tg_id, 'В сервисе квизов в Вашем аккаунте указан некорректный телефонный '
                                                 'номер. Внесите изменения, пожалуйста')


def save_to_redis(quiz):
    # Фиксируем в redis факт очередного прохождения конкретного квиза за сегодня, срок действия ключа 24 часа
    value = redis_client.get("{}_{}".format(date.today(), quiz.id))
    value = int(value) + 1 if value else 1
    redis_client.set("{}_{}".format(date.today(), quiz.id), value, 86400)

    # Находим среди квизов данного автора лидеров на сегодня
    user_quizzes = list(Quiz.objects.filter(user=quiz.user.id).values())
    redis_values = list(map(lambda quiz: (quiz, redis_client.get("{}_{}".format(date.today(), quiz["id"]))), user_quizzes))
    quizzes_in_redis = list(filter(lambda el: el[1] is not None, redis_values))
    max_value = max(list(map(lambda el: int(el[1]), quizzes_in_redis)))
    lead_quizzes = list(map(lambda el: (el[0], int(el[1])), list(filter(lambda el: int(el[1]) == max_value, quizzes_in_redis))))

    return lead_quizzes


class ResultViewSet(viewsets.ViewSet):

    def create(self, request):
        serializer = QuizResultSerializer(data=request.data)
        if serializer.is_valid():
            quiz_id = serializer.validated_data['quiz']
            results = serializer.validated_data['results']
            try:
                contacts = serializer.validated_data['contacts']
            except:
                contacts = None
            quiz = Quiz.objects.get(id=quiz_id)

            try:
                send_results(quiz, results, contacts)
                return Response('ok')
            except Exception as e:
                return Response(e)

        return Response(serializer.errors)


class QuizViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    queryset = Quiz.objects.all()

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return QuizDetailSerializer
        else:
            return QuizSerializer

    def retrieve(self, request, *args, **kwargs):
        quiz = self.get_object()
        if quiz.id in cache:
            # берем данные из cache
            quiz = cache.get(quiz.id)
            return Response(quiz)
        else:
            serializer = self.get_serializer(quiz)
            # сохраняем данные в cache
            cache.set(quiz.id, serializer.data, timeout=CACHE_TTL)
            return Response(serializer.data)



