from django.db import models
from django.contrib.auth.models import AbstractUser, Group
from django.db.models.signals import post_save
from django.dispatch import receiver


class User(AbstractUser):
    tg_id = models.CharField("ID в телеграмме", max_length=20)
    phone = models.CharField("Телефон", max_length=30, blank=True, null=True)


@receiver(post_save, sender=User)
def add_user_to_group(sender, instance, created, **kwargs):
    if created and instance.is_staff == True:
        group = Group.objects.get(id=1)
        group.user_set.add(instance)


class Quiz(models.Model):
    SEND_TYPES = [
        ("TG", 'В телеграмм'),
        ("SMS", 'По SMS'),
        ("TG-SMS", 'В телеграмм и по SMS'),
    ]
    user = models.ForeignKey(User, verbose_name="Автор", related_name='quizzes', on_delete=models.CASCADE)
    title = models.CharField('Название квиза', max_length=500)
    send_results_type = models.CharField('Тип отправки результатов', max_length=6, choices=SEND_TYPES, default="TG")
    is_send_name = models.BooleanField('Отправка имени', default=False)
    is_send_email = models.BooleanField('Отправка email', default=False)
    is_send_phone = models.BooleanField('Отправка телефона', default=False)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Квиз"
        verbose_name_plural = "Квизы"


class Question(models.Model):
    quiz = models.ForeignKey(Quiz, verbose_name="Квиз", related_name='questions', on_delete=models.CASCADE)
    text = models.TextField('Вопрос', max_length=5000, null=False)
    number = models.IntegerField('Порядковый номер вопроса', null=False)

    def __str__(self):
        return self.text[:40]

    class Meta:
        verbose_name = "Вопрос"
        verbose_name_plural = "Вопросы"
        unique_together = ('quiz', 'number')


class Answer(models.Model):
    question = models.ForeignKey(Question, verbose_name="Вопрос", related_name='answers', on_delete=models.CASCADE)
    num = models.IntegerField('Номер ответа', null=False)
    text = models.TextField('Ответ', max_length=500, null=False)
    is_correct = models.BooleanField('Правильный', null=False)

    def __str__(self):
        return self.text[:40]

    class Meta:
        verbose_name = "Ответ"
        verbose_name_plural = "Ответы"
        unique_together = ('question', 'num')
