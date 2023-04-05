from rest_framework.response import Response
from rest_framework import viewsets, permissions
from .models import Quiz
from .serializers import QuizSerializer, QuizDetailSerializer, QuizResultSerializer
from .senders.tg_sender import send_results_tg
from .senders.sms_sender import send_results_sms


def form_message(quiz, results, contacts):
    message = f'Результаты прохождения квиза "{quiz.title}":\n\n'
    for res in results:
        message += '{}. {}\n'.format(res['question'], res['answer'])
    if contacts:
        message += '\nДанные участника:\n'
        if 'name' in contacts:
            message += 'Имя - {}\n'.format(contacts['name'])
        if 'email' in contacts:
            message += 'Email - {}\n'.format(contacts['email'])
        if 'phone' in contacts:
            message += 'Телефон - {}\n'.format(contacts['phone'])
    return message


def send_results(quiz, results, contacts):
    msg = form_message(quiz, results, contacts)

    if "TG" in quiz.send_results_type:
        send_results_tg(quiz.user.tg_id, msg)
    if "SMS" in quiz.send_results_type and quiz.user.phone:
        resp = send_results_sms(msg[:10], quiz.user.phone)
        print(resp)
        if 'error' in resp:
            if resp['error'] == 'incorrect phone number':
                send_results_tg(quiz.user.tg_id, 'В сервисе квизов в Вашем аккаунте указан некорректный телефонный '
                                                 'номер. Внесите изменения, пожалуйста')


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
