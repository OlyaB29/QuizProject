from django.urls import path, include
from . import api
from rest_framework import routers


app_name = 'quiz_app'

router = routers.DefaultRouter()
router.register('quizzes', api.QuizViewSet, 'quizzes')
router.register('results', api.ResultViewSet, 'res')


urlpatterns = [
    path('', include(router.urls)),
]



