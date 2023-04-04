from rest_framework.response import Response
from rest_framework.decorators import api_view, renderer_classes
from rest_framework.renderers import JSONRenderer
from rest_framework import viewsets, permissions
from .models import Quiz
from .serializers import QuizSerializer, QuizDetailSerializer, QuizResultSerializer
from .quiz_results_sender import send_quiz_results


# @api_view(('POST',))
# @renderer_classes((JSONRenderer,))
# def send(request):
#     # bot.send_quiz_results('5187812315', 'OK')
#     id = request.POST['quiz']
#     results = request.POST['results']
#     contacts = request.POST['contacts']
#     print(id, results, contacts)
#     ok = {'ok': 'yes'}
#     return Response(ok)

def form_message(quiz, results, contacts):
    message = f'Результаты прохождения квиза "{quiz.title}":\n\n'
    for res in results:
        message += '{}. {}\n'.format(res['question'], res['answer'])
    if contacts:
        message += '\nДанные участника:\n'
        if contacts['name']:
            message += 'Имя - {}\n'.format(contacts['name'])
        if contacts['email']:
            message += 'Email - {}\n'.format(contacts['email'])
        if contacts['phone']:
            message += 'Телефон - {}\n'.format(contacts['phone'])
    return message


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

            if "TG" in quiz.send_results_type:
                send_quiz_results(quiz.user.tg_id, form_message(quiz, results, contacts))

            return Response('ok')
        return Response(serializer.errors)


class QuizViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    queryset = Quiz.objects.all()

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return QuizDetailSerializer
        else:
            return QuizSerializer
