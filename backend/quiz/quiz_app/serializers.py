from rest_framework import serializers
from .models import User, Quiz, Question, Answer


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'password', 'is_staff', 'tg_id', 'phone')
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance


class AnswerSerializer(serializers.ModelSerializer):

    class Meta:
        model = Answer
        fields = '__all__'


class QuestionSerializer(serializers.ModelSerializer):

    answers = AnswerSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = ("id", 'quiz', 'number', 'text', 'answers')


class QuizSerializer(serializers.ModelSerializer):

    class Meta:
        model = Quiz
        fields = ('id', 'title')


class QuizDetailSerializer(serializers.ModelSerializer):

    questions = QuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Quiz
        exclude = ('send_results_type',)


class ResultSerializer(serializers.Serializer):
    question = serializers.IntegerField()
    answer = serializers.CharField(max_length=200)


class ContactsSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=200, required=False)
    email = serializers.EmailField(required=False)
    phone = serializers.CharField(max_length=20, required=False)


class QuizResultSerializer(serializers.Serializer):
    quiz = serializers.IntegerField()
    results = ResultSerializer(many=True)
    contacts = ContactsSerializer(required=False)