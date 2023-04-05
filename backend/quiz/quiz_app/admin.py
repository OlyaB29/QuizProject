from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Quiz, Question, Answer


class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ('username', 'is_staff', 'is_active', 'tg_id', 'phone')
    list_filter = ('username', 'is_staff', 'is_active')
    fieldsets = (
        (None, {'fields': ('username', 'password', 'tg_id', 'phone')}),
        ('Permissions', {'fields': ('is_staff', 'is_active')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'is_staff', 'is_active', 'tg_id', 'phone')}
         ),
    )
    search_fields = ('username',)
    ordering = ('username',)

    def get_queryset(self, request):
        if request.user.is_superuser:
            return super(CustomUserAdmin, self).get_queryset(request)
        else:
            qs = super(CustomUserAdmin, self).get_queryset(request)
            return qs.filter(id=request.user.id)


class QuizAdmin(admin.ModelAdmin):
    user_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('title', 'send_results_type', 'is_send_name', 'is_send_email', 'is_send_phone')
        }),
    )

    list_display = ['user', 'title', 'send_results_type', 'is_send_name', 'is_send_email', 'is_send_phone']
    raw_id_list_displayfields = ('user',)
    search_fields = ['user__username', 'title']
    list_editable = ('is_send_name', 'is_send_email', 'is_send_phone')

    def save_model(self, request, obj, form, change):
        if form.is_valid():
            if not request.user.is_superuser or not form.cleaned_data["user"]:
                obj.user = request.user
                obj.save()
            elif form.cleaned_data["user"]:
                obj.user = form.cleaned_data["user"]
                obj.save()

    def preprocess_list_display(self, request):
        if 'user' not in self.list_display:
            self.list_display.insert(self.list_display.__len__(), 'user')
        if not request.user.is_superuser:
            if 'user' in self.list_display:
                self.list_display.remove('user')

    def preprocess_search_fields(self, request):
        if 'user__username' not in self.search_fields:
            self.search_fields.insert(self.search_fields.__len__(), 'user__username')
        if not request.user.is_superuser:
            if 'user__username' in self.search_fields:
                self.search_fields.remove('user__username')

    def changelist_view(self, request, extra_context=None):
        self.preprocess_list_display(request)
        self.preprocess_search_fields(request)
        return super(QuizAdmin, self).changelist_view(request)

    def get_queryset(self, request):
        if request.user.is_superuser:
            return super(QuizAdmin, self).get_queryset(request)
        else:
            qs = super(QuizAdmin, self).get_queryset(request)
            return qs.filter(user=request.user)

    def get_fieldsets(self, request, obj=None):
        if request.user.is_superuser:
            return super(QuizAdmin, self).get_fieldsets(request, obj)
        return self.user_fieldsets


class QuestionAdmin(admin.ModelAdmin):

    list_display = ['quiz', 'number', 'text']
    search_fields = ['quiz']

    def get_queryset(self, request):
        if request.user.is_superuser:
            return super(QuestionAdmin, self).get_queryset(request)
        else:
            qs = super(QuestionAdmin, self).get_queryset(request)
            return qs.filter(quiz__user=request.user)


class AnswerAdmin(admin.ModelAdmin):

    list_display = ['question', 'num', 'text', 'is_correct']
    search_fields = ['question']

    def get_queryset(self, request):
        if request.user.is_superuser:
            return super(AnswerAdmin, self).get_queryset(request)
        else:
            qs = super(AnswerAdmin, self).get_queryset(request)
            return qs.filter(question__quiz__user=request.user)


admin.site.register(User, CustomUserAdmin)
admin.site.register(Quiz, QuizAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Answer, AnswerAdmin)
